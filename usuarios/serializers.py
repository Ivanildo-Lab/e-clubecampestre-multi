from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Usuario

Usuario = get_user_model()


class UsuarioSerializer(serializers.ModelSerializer):
    nome_completo = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'nome_completo',
            'nivel_permissao', 'telefone', 'foto', 'ativo', 'date_joined',
            'data_criacao', 'data_atualizacao'
        ]
        read_only_fields = ['id', 'date_joined', 'data_criacao', 'data_atualizacao']


class UsuarioCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'password', 'confirm_password',
            'first_name', 'last_name', 'nivel_permissao', 'telefone'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("As senhas não coincidem")
        
        if Usuario.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError("Este e-mail já está em uso")
        
        if Usuario.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError("Este nome de usuário já está em uso")
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = Usuario.objects.create_user(**validated_data)
        return user


class UsuarioUpdateSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False, min_length=8)
    confirm_password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Usuario
        fields = [
            'first_name', 'last_name', 'email', 'telefone', 'foto',
            'current_password', 'new_password', 'confirm_password'
        ]
    
    def validate(self, attrs):
        # Validação de senha apenas se estiver tentando alterar
        if 'new_password' in attrs:
            if not attrs.get('current_password'):
                raise serializers.ValidationError("Senha atual é obrigatória para alterar a senha")
            
            if attrs['new_password'] != attrs.get('confirm_password', ''):
                raise serializers.ValidationError("As novas senhas não coincidem")
            
            # Verificar senha atual
            if not self.instance.check_password(attrs['current_password']):
                raise serializers.ValidationError("Senha atual incorreta")
        
        return attrs
    
    def update(self, instance, validated_data):
        # Remover campos de senha se existirem
        validated_data.pop('current_password', None)
        validated_data.pop('new_password', None)
        validated_data.pop('confirm_password', None)
        
        # Se há nova senha, atualizá-la separadamente
        if 'new_password' in self.initial_data:
            instance.set_password(self.initial_data['new_password'])
        
        return super().update(instance, validated_data)


class UsuarioListSerializer(serializers.ModelSerializer):
    nome_completo = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'nome_completo',
            'nivel_permissao', 'ativo', 'date_joined'
        ]