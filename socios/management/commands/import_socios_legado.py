import csv
import re
from datetime import datetime, date
from decimal import Decimal
from collections import Counter

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from core.models import Empresa, CategoriaSocio, Convenio, Socio, Dependente


def parse_date(date_str):
    if not date_str or not date_str.strip():
        return None
    s = date_str.strip()
    for fmt in ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def clean_cpf(cpf_raw):
    if not cpf_raw:
        return None
    digits = re.sub(r'\D', '', cpf_raw)
    if len(digits) != 11:
        return None
    if digits == digits[0] * 11:
        return None
    return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"


def clean_cep(cep_raw):
    if not cep_raw:
        return ""
    digits = re.sub(r'\D', '', cep_raw)
    if len(digits) == 8:
        return f"{digits[:5]}-{digits[5:]}"
    return cep_raw.strip()[:9]


def fix_encoding(s):
    if not s:
        return s
    s = s.replace("A�AILANDIA", "AÇAILÂNDIA")
    s = s.replace("A�AIL�NDIA", "AÇAILÂNDIA")
    s = s.replace("PEQUI�", "PEQUIÁ")
    s = s.replace("S�O", "SÃO")
    s = s.replace("S�o", "São")
    s = s.replace("JARDIM AM�RICA", "JARDIM AMÉRICA")
    s = s.replace("B�RBARA", "BÁRBARA")
    s = s.replace("N�O", "NÃO")
    s = s.replace("S�", "SÓ")
    s = s.replace("�", "Ã")  # fallback
    return s.strip()


ESTADO_CIVIL_MAP = {"0": "", "1": "SOLTEIRO", "2": "CASADO", "3": "DIVORCIADO", "4": "VIUVO", "5": "UNIAO", "": ""}
SITUACAO_MAP = {"1": "ATIVO", "0": "INATIVO", "2": "SUSPENSO", "3": "CANCELADO"}
PARENTESCO_MAP = {
    "ESPOSA": "CONJUGE", "ESPOSO": "CONJUGE", "CONJUGE": "CONJUGE",
    "FILHO": "FILHO", "FILHA": "FILHO", "FILHO (A)": "FILHO",
    "ENTEADO": "FILHO", "ENTEADA": "FILHO",
    "PAI": "PAI",
    "MAE": "MAE", "MÃE": "MAE", "MÃE": "MAE",
}


def map_parentesco(raw):
    if not raw:
        return "OUTRO"
    r = raw.strip().upper()
    r = r.replace("Á", "A").replace("Ã", "A").replace("É", "E")
    # Normalize
    if r in ("ESPOSA","ESPOSO","CONJUGE","ESPOSA (O)"):
        return "CONJUGE"
    if r in ("FILHO","FILHA","ENTEADO","ENTEADA"):
        return "FILHO"
    if r == "PAI":
        return "PAI"
    if r in ("MAE","MÃE","MAE"):
        return "MAE"
    return "OUTRO"


class Command(BaseCommand):
    help = "Importa socios (e dependentes, categorias, convenios) do sistema legado AERCA para empresa id=1"

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, default=r'F:\HD 1tb\Dados\Projetos\Access2013\Projetos\Aerca\qrySocioTxt.txt', help='Caminho socios txt')
        parser.add_argument('--cat-file', type=str, default=r'F:\HD 1tb\Dados\Projetos\Access2013\Projetos\Aerca\qryCategoria.txt', help='Caminho categorias')
        parser.add_argument('--conv-file', type=str, default=r'F:\HD 1tb\Dados\Projetos\Access2013\Projetos\Aerca\qryConvenios.txt', help='Caminho convenios')
        parser.add_argument('--dep-file', type=str, default=r'F:\HD 1tb\Dados\Projetos\Access2013\Projetos\Aerca\qryDependentes.txt', help='Caminho dependentes')
        parser.add_argument('--empresa', type=int, default=1)
        parser.add_argument('--dry-run', action='store_true')
        parser.add_argument('--limit', type=int, default=None)
        parser.add_argument('--update-existing', action='store_true')
        parser.add_argument('--skip-dependentes', action='store_true', help='Nao importa dependentes')
        parser.add_argument('--only-dependentes', action='store_true', help='Importa apenas dependentes (requer socios ja importados)')

    def handle(self, *args, **options):
        empresa_id = options['empresa']
        dry_run = options['dry_run']
        limit = options['limit']
        update_existing = options['update_existing']
        skip_deps = options['skip_dependentes']
        only_deps = options['only_dependentes']
        cat_file = options['cat_file']
        conv_file = options['conv_file']
        dep_file = options['dep_file']
        file_path = options['file']

        try:
            empresa = Empresa.objects.get(id=empresa_id)
        except Empresa.DoesNotExist:
            self.stderr.write(f"Empresa id={empresa_id} nao encontrada")
            return

        self.stdout.write(f"Empresa: {empresa.nome} (id={empresa.id})")
        if dry_run:
            self.stdout.write(self.style.WARNING("MODO DRY-RUN"))
        if only_deps:
            self.stdout.write("Modo: apenas dependentes")
            self.import_dependentes(empresa, dep_file, file_path, dry_run)
            return

        # 1. Import categorias
        self.import_categorias(empresa, cat_file, dry_run)
        # 2. Import convenios
        self.import_convenios(empresa, conv_file, dry_run)
        # 3. Import socios
        cod_map = self.import_socios(empresa, file_path, dry_run, limit, update_existing)
        # 4. Import dependentes
        if not skip_deps and cod_map is not None:
            self.import_dependentes(empresa, dep_file, file_path, dry_run, cod_map)

    def import_categorias(self, empresa, cat_file, dry_run):
        self.stdout.write(f"\n--- Categorias: {cat_file} ---")
        try:
            with open(cat_file, 'r', encoding='cp1252') as f:
                reader = csv.DictReader(f, delimiter=';')
                rows = list(reader)
        except FileNotFoundError:
            self.stderr.write(f"Arquivo categorias nao encontrado: {cat_file}")
            return
        self.stdout.write(f"Encontradas {len(rows)} categorias legadas")
        for r in rows:
            cod = r['CodCategoria'].strip()
            desc = fix_encoding(r['DescricaoCategoria'].strip())
            if not desc:
                desc = f"Categoria {cod}"
            # Mapeia para CategoriaSocio
            # Tenta achar por nome exato
            existing = CategoriaSocio.objects.filter(empresa=empresa, nome=desc).first()
            if existing:
                self.stdout.write(f"  Categoria {cod} '{desc}' -> ja existe id={existing.id}")
                continue
            # Tenta achar por codigo legado no descricao?
            if dry_run:
                self.stdout.write(f"  [DRY] Criaria categoria '{desc}' (cod {cod})")
            else:
                cat, created = CategoriaSocio.objects.get_or_create(
                    empresa=empresa, nome=desc,
                    defaults={'valor_mensalidade': Decimal("0.00"), 'dia_vencimento': 10, 'descricao': f'Importada legado cod={cod}'}
                )
                self.stdout.write(f"  Categoria '{desc}' -> id={cat.id} {'(criada)' if created else ''}")
        # Garante Isento para cod 0
        if not CategoriaSocio.objects.filter(empresa=empresa, nome="Isento / Cortesia").exists():
            if not CategoriaSocio.objects.filter(empresa=empresa, nome__icontains="Isento").exists():
                if dry_run:
                    self.stdout.write(f"  [DRY] Criaria categoria 'Isento / Cortesia' para cod 0")
                else:
                    c, _ = CategoriaSocio.objects.get_or_create(empresa=empresa, nome="Isento / Cortesia", defaults={'valor_mensalidade': Decimal("0.00"), 'dia_vencimento': 10})
                    self.stdout.write(f"  Categoria Isento -> id={c.id}")

    def import_convenios(self, empresa, conv_file, dry_run):
        self.stdout.write(f"\n--- Convenios: {conv_file} ---")
        try:
            with open(conv_file, 'r', encoding='cp1252') as f:
                reader = csv.DictReader(f, delimiter=';')
                rows = list(reader)
        except FileNotFoundError:
            self.stderr.write(f"Arquivo convenios nao encontrado: {conv_file}")
            return
        self.stdout.write(f"Encontrados {len(rows)} convenios legados")
        for r in rows:
            cod = r['CodConvenio'].strip()
            desc = fix_encoding(r['DescricaoConvenio'].strip())
            if not desc:
                desc = f"Convênio {cod}"
            if desc.strip() == "":
                continue
            existing = Convenio.objects.filter(empresa=empresa, nome=desc).first()
            if existing:
                self.stdout.write(f"  Convenio {cod} '{desc}' -> ja existe id={existing.id}")
                continue
            if dry_run:
                self.stdout.write(f"  [DRY] Criaria convenio '{desc}' (cod {cod})")
            else:
                conv, created = Convenio.objects.get_or_create(
                    empresa=empresa, nome=desc,
                    defaults={'empresa_contato': '', 'telefone_contato': ''}
                )
                self.stdout.write(f"  Convenio '{desc}' -> id={conv.id} {'(criado)' if created else ''}")

    def import_socios(self, empresa, file_path, dry_run, limit, update_existing):
        self.stdout.write(f"\n--- Socios: {file_path} ---")
        try:
            f = open(file_path, 'r', encoding='cp1252')
        except FileNotFoundError:
            self.stderr.write(f"Arquivo nao encontrado: {file_path}")
            return None
        reader = csv.DictReader(f, delimiter=';')
        rows = list(reader)
        f.close()
        if limit:
            rows = rows[:limit]
        self.stdout.write(f"Total linhas: {len(rows)}")
        cat_counter = Counter(r['CodCategoria'] for r in rows)
        conv_counter = Counter(r['CodConvenio'] for r in rows)
        self.stdout.write(f"Categorias: {dict(cat_counter)} | Convenios distintos: {len(conv_counter)}")

        # Cache categorias por cod e por nome
        # Monta mapa cod->categoria usando arquivo qryCategoria se possivel
        # Primeiro tenta mapear via nome exato da categoria legada
        cat_map = {}
        # Carrega nomes legados
        cat_file = r'F:\HD 1tb\Dados\Projetos\Access2013\Projetos\Aerca\qryCategoria.txt'
        try:
            with open(cat_file, 'r', encoding='cp1252') as cf:
                cr = csv.DictReader(cf, delimiter=';')
                for cr_row in cr:
                    cod = cr_row['CodCategoria'].strip()
                    desc = fix_encoding(cr_row['DescricaoCategoria'].strip())
                    if desc and not desc.startswith("N�O"):
                        # normaliza
                        desc = desc.replace("N�O", "NÃO")
                    # busca categoria criada
                    cat = CategoriaSocio.objects.filter(empresa=empresa, nome=desc).first()
                    if cat:
                        cat_map[cod] = cat
                    else:
                        # fallback busca por Isento
                        if cod == "0":
                            cat = CategoriaSocio.objects.filter(empresa=empresa, nome__icontains="Isento").first()
                            if cat:
                                cat_map[cod] = cat
        except:
            pass
        # Fallback para codigos nao mapeados: busca generica
        for cod in set(r['CodCategoria'] for r in rows):
            cod = cod.strip() or "0"
            if cod in cat_map:
                continue
            # tenta legenda
            if cod == "0":
                cat = CategoriaSocio.objects.filter(empresa=empresa, nome__icontains="Isento").first()
                if cat:
                    cat_map[cod] = cat
                    continue
            # tenta por nome legado
            desc_try = {"1": "PADRAO", "2": "CONTRIBUINTE", "3": "CONVENIO", "4": "FUNCIONARIO", "5": "NÃO SÓCIO"}.get(cod, f"Categoria {cod}")
            cat = CategoriaSocio.objects.filter(empresa=empresa, nome__icontains=desc_try.split()[0]).first()
            if cat:
                cat_map[cod] = cat
            else:
                cat = CategoriaSocio.objects.filter(empresa=empresa).first()
                cat_map[cod] = cat

        for k, v in cat_map.items():
            self.stdout.write(f"  Cat cod {k} -> {v.nome if v else 'None'} (id={v.id if v else '?'})")

        # Convenio cache por nome
        conv_map = {}
        for cod in set(r['CodConvenio'] for r in rows):
            cod = cod.strip()
            if not cod or cod == "0":
                conv_map[cod] = None
                continue
            # busca pelo nome criado
            # Precisa carregar descricao do arquivo convenios
            desc_map = {}
            try:
                with open(r'F:\HD 1tb\Dados\Projetos\Access2013\Projetos\Aerca\qryConvenios.txt', 'r', encoding='cp1252') as cf:
                    cr = csv.DictReader(cf, delimiter=';')
                    for cr_row in cr:
                        desc_map[cr_row['CodConvenio'].strip()] = fix_encoding(cr_row['DescricaoConvenio'].strip())
            except:
                pass
            desc = desc_map.get(cod, f"Convênio Legado {cod}")
            conv = Convenio.objects.filter(empresa=empresa, nome=desc).first()
            if not conv:
                # tenta genérico
                conv = Convenio.objects.filter(empresa=empresa, nome__icontains=desc.split()[0]).first()
            conv_map[cod] = conv

        existing_num_reg = set(Socio.objects.filter(empresa=empresa).values_list('num_registro', flat=True))
        existing_cpf_digits = set(re.sub(r'\D','',c) for c in Socio.objects.filter(empresa=empresa).exclude(cpf__isnull=True).exclude(cpf__exact='').values_list('cpf', flat=True) if c)
        existing_emails = set(Socio.objects.filter(empresa=empresa).exclude(email__isnull=True).values_list('email', flat=True))
        max_num = max(existing_num_reg) if existing_num_reg else 0
        self.stdout.write(f"Socios existentes: {len(existing_num_reg)}, max num={max_num}")

        # Map CodCliente -> Socio (para dependentes)
        cod_to_socio = {}
        # Pre-popula com existentes
        for s in Socio.objects.filter(empresa=empresa):
            cod_to_socio[str(s.num_registro)] = s

        seen_num = set()
        seen_cpf_digits = set()
        criados = pulados = atualizados = 0
        erros = []
        # Para mapear CodCliente legado -> novo Socio
        legacy_cod_to_new_num = {}

        for idx, row in enumerate(rows, start=2):
            try:
                cod_cliente = row['CodCliente'].strip()
                num_reg_raw = row['NumRegistro'].strip()
                nome = fix_encoding(row['NomeSocio'].strip())
                if not nome:
                    pulados += 1
                    continue
                try:
                    num_reg = int(num_reg_raw) if num_reg_raw else 0
                except:
                    num_reg = 0
                if num_reg == 0 or str(num_reg) in seen_num or num_reg in existing_num_reg:
                    max_num += 1
                    num_reg = max_num
                    while num_reg in existing_num_reg or str(num_reg) in seen_num:
                        max_num += 1
                        num_reg = max_num
                seen_num.add(str(num_reg))
                seen_num.add(num_reg)
                legacy_cod_to_new_num[cod_cliente] = num_reg

                # Resto dos campos (reusa logica anterior simplificada)
                num_cont_raw = row['NumContrato'].strip()
                num_contrato = None
                if num_cont_raw:
                    try:
                        nc = int(num_cont_raw)
                        if nc != 0 and not Socio.objects.filter(num_contrato=nc).exists():
                            num_contrato = nc
                    except:
                        pass
                cod_cat = row['CodCategoria'].strip() or "0"
                categoria = cat_map.get(cod_cat) or list(cat_map.values())[0]
                cod_conv = row['CodConvenio'].strip()
                convenio = conv_map.get(cod_conv)

                nacionalidade = fix_encoding(row['NacionalidadeSocio'].strip()) or "Brasileira"
                naturalidade = fix_encoding(row['NaturalidadeSocio'].strip())
                data_nasc = parse_date(row['DataNascimentoSocio'])
                if not data_nasc:
                    data_nasc = date(1970, 1, 1)
                estado_civil = ESTADO_CIVIL_MAP.get(row['EstadoCivilSocio'].strip(), "")
                nome_pai = fix_encoding(row['NomePaiSocio'].strip())
                nome_mae = fix_encoding(row['NomeMaeSocio'].strip())
                profissao = fix_encoding(row['ProfissaoSocio'].strip())
                cargo = fix_encoding(row['Cargosocio'].strip())
                endereco = fix_encoding(row['EnderecoResidencial'].strip())
                bairro = fix_encoding(row['BairroSocio'].strip())
                cidade = fix_encoding(row['CidadeSocio'].strip())
                estado = fix_encoding(row['EstadoSocio'].strip())[:2].upper()
                cep = clean_cep(row['CepSocio'])
                fone = row['FoneResidencial'].strip()
                data_adm = parse_date(row['DataAdmissao'])
                if not data_adm:
                    data_adm = timezone.now().date()
                obs = fix_encoding(row['ObsSocio'].strip())
                if cargo:
                    obs = f"{obs}\nCargo: {cargo}" if obs else f"Cargo: {cargo}"
                rg = row['RgSocio'].strip()[:20]
                cpf_raw = row['CpfSocio'].strip()
                cpf = clean_cpf(cpf_raw)
                if cpf:
                    digits = re.sub(r'\D','', cpf)
                    if digits in existing_cpf_digits or digits in seen_cpf_digits:
                        cpf = None
                    else:
                        seen_cpf_digits.add(digits)
                if not cpf and cod_cliente.isdigit():
                    fake_digits = f"999999999{int(cod_cliente)%100:02d}"
                    fake_digits = fake_digits[:11].ljust(11,'0')
                    fake_cpf = f"{fake_digits[:3]}.{fake_digits[3:6]}.{fake_digits[6:9]}-{fake_digits[9:]}"
                    fd = re.sub(r'\D','', fake_cpf)
                    if fd not in existing_cpf_digits and fd not in seen_cpf_digits:
                        cpf = fake_cpf
                        seen_cpf_digits.add(fd)
                situacao = SITUACAO_MAP.get(row['SituacaoSocio'].strip(), "ATIVO")
                email_raw = row['email'].strip().lower()
                email = email_raw if email_raw else None
                if email and (email in existing_emails or Socio.objects.filter(email=email).exists()):
                    email = None
                apelido = fix_encoding(row['Apelido'].strip())[:100]

                existing = Socio.objects.filter(empresa=empresa, num_registro=num_reg).first()
                if existing and not update_existing:
                    pulados += 1
                    cod_to_socio[cod_cliente] = existing
                    continue

                socio_data = {
                    'empresa': empresa,
                    'num_registro': num_reg,
                    'num_contrato': num_contrato,
                    'categoria': categoria,
                    'convenio': convenio,
                    'nome': nome[:255],
                    'apelido': apelido,
                    'data_nascimento': data_nasc,
                    'cpf': cpf,
                    'rg': rg,
                    'nacionalidade': nacionalidade[:100],
                    'naturalidade': naturalidade[:100],
                    'estado_civil': estado_civil,
                    'profissao': profissao[:100],
                    'nome_pai': nome_pai[:255],
                    'nome_mae': nome_mae[:255],
                    'email': email,
                    'tel_residencial': fone[:20],
                    'tel_trabalho': "",
                    'endereco': endereco[:255],
                    'bairro': bairro[:100],
                    'cidade': cidade[:100],
                    'estado': estado,
                    'cep': cep,
                    'data_admissao': data_adm,
                    'situacao': situacao,
                    'observacoes': obs or "",
                }
                if not socio_data['cpf']:
                    placeholder = f"SEMCPF{num_reg:06d}"
                    socio_data['cpf'] = placeholder
                    socio_data['observacoes'] = (socio_data['observacoes'] + f"\nCPF original: '{cpf_raw}' -> {placeholder}").strip()

                if dry_run:
                    criados += 1
                    # simula cod_to_socio
                    fake = Socio(**socio_data)
                    fake.id = 99999
                    cod_to_socio[cod_cliente] = fake
                    continue

                with transaction.atomic():
                    if existing and update_existing:
                        for k, v in socio_data.items():
                            if k == 'empresa':
                                continue
                            setattr(existing, k, v)
                        existing.save()
                        atualizados += 1
                        cod_to_socio[cod_cliente] = existing
                    else:
                        s = Socio.objects.create(**socio_data)
                        criados += 1
                        cod_to_socio[cod_cliente] = s
                        if email:
                            existing_emails.add(email)
            except Exception as e:
                import traceback
                erros.append(f"linha {idx}: {e}")
                if len(erros) < 5:
                    traceback.print_exc()

        self.stdout.write(self.style.SUCCESS(f"\nSocios -> criados={criados} atualizados={atualizados} pulados={pulados} erros={len(erros)}"))
        if erros:
            for err in erros[:5]:
                self.stdout.write(f" - {err}")
        return cod_to_socio if not dry_run else legacy_cod_to_new_num

    def import_dependentes(self, empresa, dep_file, socios_file, dry_run, cod_map=None):
        self.stdout.write(f"\n--- Dependentes: {dep_file} ---")
        try:
            with open(dep_file, 'r', encoding='cp1252') as f:
                reader = csv.DictReader(f, delimiter=';')
                rows = list(reader)
        except FileNotFoundError:
            self.stderr.write(f"Arquivo dependentes nao encontrado: {dep_file}")
            return
        self.stdout.write(f"Total linhas dependentes: {len(rows)}")
        # Filtra apenas dependentes cujo CodCliente esta no socios ativos
        try:
            with open(socios_file, 'r', encoding='cp1252') as sf:
                sr = csv.DictReader(sf, delimiter=';')
                srows = list(sr)
                socios_codes = set(r['CodCliente'].strip() for r in srows if r['NomeSocio'].strip())
        except:
            socios_codes = None

        if socios_codes:
            before = len(rows)
            rows = [r for r in rows if r['CodCliente'].strip() in socios_codes]
            self.stdout.write(f"Filtrados apenas de socios ativos: {before} -> {len(rows)} (removidos {before-len(rows)})")

        # Carrega todos socios da empresa para mapear CodCliente -> Socio
        # Tenta usar map de importacao se disponivel, senao busca por num_registro == CodCliente
        if cod_map is None:
            cod_map = {}
            for s in Socio.objects.filter(empresa=empresa):
                cod_map[str(s.num_registro)] = s

        criados = pulados = 0
        erros = []
        for idx, row in enumerate(rows, start=2):
            try:
                cod_cliente = row['CodCliente'].strip()
                nome = fix_encoding(row['Nomedep'].strip())
                if not nome or not cod_cliente:
                    pulados += 1
                    continue
                socio = cod_map.get(cod_cliente)
                if not socio:
                    # tenta buscar por CodCliente == NumRegistro original
                    socio = Socio.objects.filter(empresa=empresa, num_registro=int(cod_cliente) if cod_cliente.isdigit() else -1).first()
                if not socio:
                    # tenta buscar por nome? pula
                    pulados += 1
                    continue
                # Se socio é fake de dry-run, pula criacao real
                if dry_run and getattr(socio, 'id', 99999) == 99999:
                    criados += 1
                    continue

                parentesco = map_parentesco(row['ParentescoDep'])
                data_nasc = parse_date(row['DatanascimentoDep'])
                if not data_nasc:
                    data_nasc = date(1990, 1, 1)  # default
                # Cpf nao tem no legado para dependentes, deixa None? model exige unique nullable? Em Dependente cpf é unique True blank True null True
                # Entao pode ser None

                # Verifica duplicado: mesmo nome + mesmo socio
                if Dependente.objects.filter(socio_titular=socio, nome=nome).exists():
                    pulados += 1
                    continue

                if dry_run:
                    criados += 1
                    continue

                with transaction.atomic():
                    Dependente.objects.create(
                        socio_titular=socio,
                        nome=nome[:255],
                        data_nascimento=data_nasc,
                        cpf=None,
                        parentesco=parentesco,
                    )
                    criados += 1
            except Exception as e:
                erros.append(f"linha {idx}: {e}")
                if len(erros) < 5:
                    import traceback; traceback.print_exc()

        self.stdout.write(self.style.SUCCESS(f"Dependentes -> criados={criados} pulados={pulados} erros={len(erros)}"))
        if erros:
            for e in erros[:5]:
                self.stdout.write(f" - {e}")
