from rest_framework import serializers







class DashboardSerializer(serializers.Serializer):
    """Serializer para dados do dashboard"""
    socios = serializers.DictField()
    financeiro = serializers.DictField()
    indicadores = serializers.DictField()