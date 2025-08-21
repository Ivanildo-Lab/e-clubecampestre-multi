from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from financeiro.models import Mensalidade
from core.models import Socio
from django.db.models.functions import TruncMonth

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin



# Adicione esta classe no FINAL do arquivo core/views.py
class HealthCheckView(viewsets.ViewSet):
    """View para health check da API"""
    
    def list(self, request):
        return Response({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'version': '1.0.0'
        })


class ConfiguracaoSistemaViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar configurações do sistema"""
   
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        chave = self.request.query_params.get('chave')
        if chave:
            queryset = queryset.filter(chave=chave)
        return queryset
    
    @action(detail=False, methods=['get'])
    def por_chave(self, request):
        """Obter configuração por chave"""
        chave = request.query_params.get('chave')
        if not chave:
            return Response(
                {'error': 'Parâmetro "chave" é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            config = ConfiguracaoSistema.objects.get(chave=chave, ativo=True)
            serializer = self.get_serializer(config)
            return Response(serializer.data)
        except ConfiguracaoSistema.DoesNotExist:
            return Response(
                {'error': 'Configuração não encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )


class AuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para visualizar auditoria do sistema"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        usuario = self.request.query_params.get('usuario')
        acao = self.request.query_params.get('acao')
        modelo = self.request.query_params.get('modelo')
        
        if usuario:
            queryset = queryset.filter(usuario_id=usuario)
        if acao:
            queryset = queryset.filter(acao=acao)
        if modelo:
            queryset = queryset.filter(modelo=modelo)
        
        return queryset.order_by('-data_acao')


class BackupViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar backups do sistema"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset.order_by('-data_inicio')
    
    @action(detail=True, methods=['post'])
    def executar(self, request, pk=None):
        """Executar o backup"""
        backup = self.get_object()
        if backup.status != 'PENDENTE':
            return Response(
                {'error': 'Backup já está em processamento ou foi concluído'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Aqui seria implementada a lógica de backup
        backup.status = 'PROCESSANDO'
        backup.save()
        
        return Response({'message': 'Backup iniciado com sucesso'})




class DashboardViewSet(viewsets.ViewSet):
    """ViewSet para dados do dashboard"""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Obter dados para o dashboard"""
        from socios.models import Socio
        from financeiro.models import Mensalidade, Receita, Despesa
        
        # Dados de sócios
        total_socios = Socio.objects.count()
        socios_ativos = Socio.objects.filter(ativo=True).count()
        
        # Dados financeiros
        mensalidades_pendentes = Mensalidade.objects.filter(status='PENDENTE').count()
        mensalidades_atrasadas = Mensalidade.objects.filter(status='ATRASADO').count()
        
        # Receitas do mês atual
        inicio_mes = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        receitas_mes = Receita.objects.filter(
            data_recebimento__gte=inicio_mes,
            status='RECEBIDO'
        ).aggregate(total=Sum('valor'))['total'] or 0
        
        # Despesas do mês atual
        despesas_mes = Despesa.objects.filter(
            data_pagamento__gte=inicio_mes,
            status='PAGO'
        ).aggregate(total=Sum('valor'))['total'] or 0
        
        # Inadimplência
        total_mensalidades = Mensalidade.objects.count()
        if total_mensalidades > 0:
            taxa_inadimplencia = (mensalidades_atrasadas / total_mensalidades) * 100
        else:
            taxa_inadimplencia = 0
        
        # Novos sócios nos últimos 30 dias
        trinta_dias_atras = timezone.now() - timedelta(days=30)
        novos_socios = Socio.objects.filter(
            data_cadastro__gte=trinta_dias_atras
        ).count()
        
        dashboard_data = {
            'socios': {
                'total': total_socios,
                'ativos': socios_ativos,
                'novos_ultimos_30_dias': novos_socios,
            },
            'financeiro': {
                'mensalidades_pendentes': mensalidades_pendentes,
                'mensalidades_atrasadas': mensalidades_atrasadas,
                'receitas_mes': float(receitas_mes),
                'despesas_mes': float(despesas_mes),
                'saldo_mes': float(receitas_mes - despesas_mes),
            },
            'indicadores': {
                'taxa_inadimplencia': round(taxa_inadimplencia, 2),
            }
        }
        
        return Response(dashboard_data)
    
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html' # Usaremos o index.html como nosso dashboard
    login_url = '/admin/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Dashboard'
        # ATUALIZA O STATUS DE MENSALIDADES VENCIDAS ANTES DE CALCULAR
        Mensalidade.objects.atualizar_status_atrasadas()
        
        hoje = timezone.now()
        primeiro_dia_mes = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # --- DADOS PARA OS CARDS ---
        mensalidades_mes = Mensalidade.objects.filter(competencia__month=hoje.month, competencia__year=hoje.year)
        
        context['total_socios'] = Socio.objects.filter(situacao='ATIVO').count()
        
        receita_mensal = mensalidades_mes.filter(status='PAGA').aggregate(total=Sum('valor'))['total'] or 0
        context['receita_mensal'] = receita_mensal

        pendentes = mensalidades_mes.filter(status='PENDENTE').count()
        atrasadas = mensalidades_mes.filter(status='ATRASADA').count()
        context['pagamentos_pendentes'] = pendentes + atrasadas

        total_cobradas = mensalidades_mes.count()
        if total_cobradas > 0:
            taxa_inadimplencia = (atrasadas / total_cobradas) * 100
        else:
            taxa_inadimplencia = 0
        context['taxa_inadimplencia'] = round(taxa_inadimplencia, 2)

        # --- DADOS PARA O GRÁFICO (Últimos 6 meses) ---
        seis_meses_atras = hoje - timezone.timedelta(days=180)
        receitas_por_mes = Mensalidade.objects.filter(
            status='PAGA',
            data_pagamento__gte=seis_meses_atras
        ).annotate(
            mes=TruncMonth('data_pagamento')
        ).values('mes').annotate(
            total=Sum('valor')
        ).order_by('mes')

        # Formatando para o Chart.js
        chart_labels = [mes['mes'].strftime('%b/%Y') for mes in receitas_por_mes]
        chart_data = [float(mes['total']) for mes in receitas_por_mes]
        context['chart_labels'] = chart_labels
        context['chart_data'] = chart_data

        # --- DADOS PARA ATIVIDADE RECENTE ---
        context['atividades_recentes'] = Mensalidade.objects.filter(status='PAGA').order_by('-data_pagamento')[:5]

        # --- DADOS PARA LISTA DE INADIMPLENTES ---
        context['inadimplentes'] = Mensalidade.objects.filter(
            status='ATRASADA'
        ).select_related('socio').order_by('data_vencimento')[:10]
        return context