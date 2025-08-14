# core/models.py

from django.db import models
from django.utils import timezone
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

# Modelo para as Categorias dos Sócios
# Ex: "Proprietário", "Familiar", "Individual"
class CategoriaSocio(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Categoria de Sócio"
        verbose_name_plural = "Categorias de Sócios"


# Modelo para os Convênios
# Ex: "Empresa X", "Sindicato Y"
class Convenio(models.Model):
    nome = models.CharField(max_length=150, unique=True)
    empresa_contato = models.CharField(max_length=100, blank=True)
    telefone_contato = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.nome


# Modelo Principal de Sócio (Refatorado)
class Socio(models.Model):
    
    # --- Choices (Opções pré-definidas) ---
    class EstadoCivil(models.TextChoices):
        SOLTEIRO = 'SOLTEIRO', 'Solteiro(a)'
        CASADO = 'CASADO', 'Casado(a)'
        DIVORCIADO = 'DIVORCIADO', 'Divorciado(a)'
        VIUVO = 'VIUVO', 'Viúvo(a)'
        UNIAO_ESTAVEL = 'UNIAO', 'União Estável'

    class Situacao(models.TextChoices):
        ATIVO = 'ATIVO', 'Ativo'
        INATIVO = 'INATIVO', 'Inativo'
        SUSPENSO = 'SUSPENSO', 'Suspenso'
        CANCELADO = 'CANCELADO', 'Cancelado'

    # --- Identificação e Contrato ---
    num_registro = models.IntegerField(unique=True, help_text="Número de registro único do sócio.")
    num_contrato = models.IntegerField(unique=True, blank=True, null=True, help_text="Número do contrato, se aplicável.")
    
    # --- Relações ---
    categoria = models.ForeignKey(CategoriaSocio, on_delete=models.PROTECT, related_name='socios')
    convenio = models.ForeignKey(Convenio, on_delete=models.SET_NULL, blank=True, null=True, related_name='socios')

    # --- Dados Pessoais ---
    nome = models.CharField(max_length=255, verbose_name="Nome Completo")
    apelido = models.CharField(max_length=100, blank=True)
    data_nascimento = models.DateField()
    cpf = models.CharField(max_length=14, unique=True, verbose_name="CPF")
    rg = models.CharField(max_length=20, blank=True, verbose_name="RG")
    nacionalidade = models.CharField(max_length=100, blank=True, default="Brasileira")
    naturalidade = models.CharField(max_length=100, blank=True, verbose_name="Cidade Natal")
    estado_civil = models.CharField(max_length=10, choices=EstadoCivil.choices, blank=True)
    profissao = models.CharField(max_length=100, blank=True)
    
    # --- Filiação ---
    nome_pai = models.CharField(max_length=255, blank=True, verbose_name="Nome do Pai")
    nome_mae = models.CharField(max_length=255, blank=True, verbose_name="Nome da Mãe")

    # --- Contato ---
    email = models.EmailField(unique=True, blank=True, null=True)
    tel_residencial = models.CharField(max_length=20, blank=True, verbose_name="Telefone Residencial")
    tel_trabalho = models.CharField(max_length=20, blank=True, verbose_name="Telefone do Trabalho")

    # --- Endereço ---
    endereco = models.CharField(max_length=255, blank=True, verbose_name="Endereço (Rua, Nº)")
    bairro = models.CharField(max_length=100, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=2, blank=True, verbose_name="UF")
    cep = models.CharField(max_length=9, blank=True, verbose_name="CEP")

    # --- Dados do Clube ---
    data_admissao = models.DateField(default=timezone.now)
    situacao = models.CharField(max_length=10, choices=Situacao.choices, default=Situacao.ATIVO)
    foto = models.ImageField(upload_to='fotos_socios/', blank=True, null=True)
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    # O campo `VBomDeBola` parecia muito específico, pode ser adicionado depois se necessário.
    # O campo `Carencia` pode ser calculado com base na data_admissao, se houver uma regra.

    def __str__(self):
        return f"{self.nome} (Matrícula: {self.num_registro})"

    class Meta:
        verbose_name = "Sócio"
        verbose_name_plural = "Sócios"
        ordering = ['nome']


Usuario = get_user_model()


# Modelo para Configuração do Sistema
class ConfiguracaoSistema(models.Model):
    """Modelo para armazenar configurações do sistema"""
    
    CHAVE_CHOICES = [
        ('NOME_CLUBE', 'Nome do Clube'),
        ('LOGO_CLUBE', 'Logo do Clube'),
        ('ENDERECO_CLUBE', 'Endereço do Clube'),
        ('TELEFONE_CLUBE', 'Telefone do Clube'),
        ('EMAIL_CLUBE', 'E-mail do Clube'),
        ('CNPJ_CLUBE', 'CNPJ do Clube'),
        ('DIA_VENCIMENTO_MENSALIDADE', 'Dia de Vencimento da Mensalidade'),
        ('VALOR_MENSALIDADE_PADRAO', 'Valor da Mensalidade Padrão'),
        ('PERMITIR_CANCELAMENTO_MENSALIDADE', 'Permitir Cancelamento de Mensalidade'),
        ('DIAS_TOLERANCIA_MENSALIDADE', 'Dias de Tolerância para Mensalidade'),
        ('PERCENTUAL_JUROS_ATRASO', 'Percentual de Juros por Atraso'),
        ('EMAIL_NOTIFICACOES', 'E-mail para Notificações'),
        ('WHATSAPP_API_TOKEN', 'Token da API do WhatsApp'),
        ('WHATSAPP_API_URL', 'URL da API do WhatsApp'),
        ('SMTP_HOST', 'Servidor SMTP'),
        ('SMTP_PORT', 'Porta SMTP'),
        ('SMTP_USER', 'Usuário SMTP'),
        ('SMTP_PASSWORD', 'Senha SMTP'),
        ('SMTP_USE_TLS', 'Usar TLS no SMTP'),
        ('GOOGLE_ANALYTICS_ID', 'ID do Google Analytics'),
        ('FACEBOOK_PIXEL_ID', 'ID do Facebook Pixel'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    chave = models.CharField(
        max_length=100,
        choices=CHAVE_CHOICES,
        unique=True,
        verbose_name='Chave'
    )
    
    valor = models.TextField(
        verbose_name='Valor'
    )
    
    descricao = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descrição'
    )
    
    ativo = models.BooleanField(
        default=True,
        verbose_name='Ativo'
    )
    
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação'
    )
    
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name='Data de Atualização'
    )
    
    class Meta:
        verbose_name = 'Configuração do Sistema'
        verbose_name_plural = 'Configurações do Sistema'
        ordering = ['chave']
    
    def __str__(self):
        return f"{self.get_chave_display()}: {self.valor[:50]}..."
    
    @classmethod
    def get_valor(cls, chave, default=None):
        """Método estático para obter o valor de uma configuração"""
        try:
            config = cls.objects.get(chave=chave, ativo=True)
            return config.valor
        except cls.DoesNotExist:
            return default
    
    @classmethod
    def set_valor(cls, chave, valor, descricao=None):
        """Método estático para definir o valor de uma configuração"""
        config, created = cls.objects.get_or_create(
            chave=chave,
            defaults={
                'valor': valor,
                'descricao': descricao or f'Configuração {chave}'
            }
        )
        if not created:
            config.valor = valor
            if descricao:
                config.descricao = descricao
            config.save()
        return config


class Auditoria(models.Model):
    """Modelo para registrar auditoria do sistema"""
    
    ACAO_CHOICES = [
        ('CREATE', 'Criar'),
        ('UPDATE', 'Atualizar'),
        ('DELETE', 'Excluir'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('EXPORT', 'Exportar'),
        ('IMPORT', 'Importar'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='auditorias',
        verbose_name='Usuário'
    )
    
    acao = models.CharField(
        max_length=20,
        choices=ACAO_CHOICES,
        verbose_name='Ação'
    )
    
    modelo = models.CharField(
        max_length=100,
        verbose_name='Modelo'
    )
    
    objeto_id = models.CharField(
        max_length=100,
        verbose_name='ID do Objeto'
    )
    
    descricao = models.TextField(
        verbose_name='Descrição'
    )
    
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name='Endereço IP'
    )
    
    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name='User Agent'
    )
    
    dados_antigos = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Dados Antigos'
    )
    
    dados_novos = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Dados Novos'
    )
    
    data_acao = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data da Ação'
    )
    
    class Meta:
        verbose_name = 'Auditoria'
        verbose_name_plural = 'Auditorias'
        ordering = ['-data_acao']
    
    def __str__(self):
        return f"{self.usuario} - {self.get_acao_display()} - {self.modelo}"


class Backup(models.Model):
    """Modelo para gerenciar backups do sistema"""
    
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('PROCESSANDO', 'Processando'),
        ('CONCLUIDO', 'Concluído'),
        ('FALHA', 'Falha'),
    ]
    
    TIPO_CHOICES = [
        ('COMPLETO', 'Completo'),
        ('DADOS', 'Apenas Dados'),
        ('ARQUIVOS', 'Apenas Arquivos'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    nome = models.CharField(
        max_length=200,
        verbose_name='Nome do Backup'
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name='Tipo de Backup'
    )
    
    arquivo = models.FileField(
        upload_to='backups/',
        blank=True,
        null=True,
        verbose_name='Arquivo de Backup'
    )
    
    tamanho = models.BigIntegerField(
        blank=True,
        null=True,
        verbose_name='Tamanho (bytes)'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDENTE',
        verbose_name='Status'
    )
    
    data_inicio = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Início'
    )
    
    data_fim = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Data de Fim'
    )
    
    descricao = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descrição'
    )
    
    erro = models.TextField(
        blank=True,
        null=True,
        verbose_name='Erro'
    )
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='backups_criados',
        verbose_name='Usuário'
    )
    
    class Meta:
        verbose_name = 'Backup'
        verbose_name_plural = 'Backups'
        ordering = ['-data_inicio']
    
    def __str__(self):
        return f"{self.nome} - {self.get_status_display()}"
    
    @property
    def duracao(self):
        if self.data_fim and self.data_inicio:
            return self.data_fim - self.data_inicio
        return None
    
    @property
    def tamanho_formatado(self):
        if self.tamanho:
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if self.tamanho < 1024.0:
                    return f"{self.tamanho:.2f} {unit}"
                self.tamanho /= 1024.0
        return "0 B"


class Notificacao(models.Model):
    """Modelo para gerenciar notificações do sistema"""
    
    TIPO_CHOICES = [
        ('INFO', 'Informação'),
        ('SUCCESS', 'Sucesso'),
        ('WARNING', 'Aviso'),
        ('ERROR', 'Erro'),
    ]
    
    PRIORIDADE_CHOICES = [
        ('BAIXA', 'Baixa'),
        ('MEDIA', 'Média'),
        ('ALTA', 'Alta'),
        ('URGENTE', 'Urgente'),
    ]
    
    STATUS_CHOICES = [
        ('NAO_LIDA', 'Não Lida'),
        ('LIDA', 'Lida'),
        ('ARQUIVADA', 'Arquivada'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    titulo = models.CharField(
        max_length=200,
        verbose_name='Título'
    )
    
    mensagem = models.TextField(
        verbose_name='Mensagem'
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='INFO',
        verbose_name='Tipo'
    )
    
    prioridade = models.CharField(
        max_length=20,
        choices=PRIORIDADE_CHOICES,
        default='MEDIA',
        verbose_name='Prioridade'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='NAO_LIDA',
        verbose_name='Status'
    )
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='notificacoes',
        verbose_name='Usuário'
    )
    
    link_acao = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Link de Ação'
    )
    
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação'
    )
    
    data_leitura = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Data de Leitura'
    )
    
    data_arquivamento = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Data de Arquivamento'
    )
    
    class Meta:
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.titulo} - {self.usuario}"
    
    def marcar_como_lida(self):
        """Marca a notificação como lida"""
        self.status = 'LIDA'
        self.data_leitura = timezone.now()
        self.save()
    
    def arquivar(self):
        """Arquiva a notificação"""
        self.status = 'ARQUIVADA'
        self.data_arquivamento = timezone.now()
        self.save()