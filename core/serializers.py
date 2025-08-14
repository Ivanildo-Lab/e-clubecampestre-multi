from rest_framework import serializers
from .models import ConfiguracaoSistema, Auditoria, Backup, Notificacao


class ConfiguracaoSistemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracaoSistema
        fields = '__all__'
        read_only_fields = ['data_criacao', 'data_atualizacao']


class AuditoriaSerializer(serializers.ModelSerializer):
    usuario_nome = serializers.CharField(source='usuario.get_full_name', read_only=True)
    
    class Meta:
        model = Auditoria
        fields = '__all__'
        read_only_fields = ['data_acao']


class BackupSerializer(serializers.ModelSerializer):
    usuario_nome = serializers.CharField(source='usuario.get_full_name', read_only=True)
    tamanho_formatado = serializers.CharField(read_only=True)
    duracao = serializers.DurationField(read_only=True)
    
    class Meta:
        model = Backup
        fields = '__all__'
        read_only_fields = ['data_inicio', 'data_fim']


class NotificacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacao
        fields = '__all__'
        read_only_fields = ['usuario', 'data_criacao', 'data_leitura', 'data_arquivamento']
    
    def create(self, validated_data):
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)


class DashboardSerializer(serializers.Serializer):
    """Serializer para dados do dashboard"""
    socios = serializers.DictField()
    financeiro = serializers.DictField()
    indicadores = serializers.DictField()