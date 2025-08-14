from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Usuario
from .serializers import UsuarioSerializer, UsuarioCreateSerializer, UsuarioUpdateSerializer
from .permissions import IsOwnerOrAdmin

Usuario = get_user_model()


class UsuarioViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar usuários"""
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UsuarioUpdateSerializer
        return super().get_serializer_class()
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwnerOrAdmin()]
        return super().get_permissions()
    
    def get_queryset(self):
        queryset = super().get_queryset()
        nivel_permissao = self.request.query_params.get('nivel_permissao')
        ativo = self.request.query_params.get('ativo')
        
        if nivel_permissao:
            queryset = queryset.filter(nivel_permissao=nivel_permissao)
        if ativo is not None:
            queryset = queryset.filter(ativo=ativo.lower() == 'true')
        
        # Usuários normais só podem ver a si mesmos
        if not self.request.user.has_permission('ADMINISTRADOR'):
            queryset = queryset.filter(id=self.request.user.id)
        
        return queryset.order_by('-date_joined')
    
    def perform_create(self, serializer):
        # Criptografar a senha antes de salvar
        password = serializer.validated_data.get('password')
        if password:
            serializer.validated_data['password'] = make_password(password)
        serializer.save()
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """Endpoint customizado para login"""
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'error': 'Email e senha são obrigatórios'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Autenticar usando email (username no Django)
        user = authenticate(username=email, password=password)
        
        if not user:
            return Response(
                {'error': 'Credenciais inválidas'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.ativo:
            return Response(
                {'error': 'Usuário inativo'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Gerar tokens JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UsuarioSerializer(user).data
        })
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """Endpoint para logout (blacklist refresh token)"""
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'message': 'Logout realizado com sucesso'})
        except Exception as e:
            return Response(
                {'error': 'Erro ao realizar logout'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Obter perfil do usuário atual"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def permissions(self, request):
        """Listar permissões do usuário atual"""
        user_permissions = {
            'nivel_permissao': request.user.nivel_permissao,
            'permissoes': {
                'ADMINISTRADOR': request.user.has_permission('ADMINISTRADOR'),
                'FINANCEIRO': request.user.has_permission('FINANCEIRO'),
                'ATENDIMENTO': request.user.has_permission('ATENDIMENTO'),
            }
        }
        return Response(user_permissions)
    
    @action(detail=True, methods=['post'])
    def ativar_desativar(self, request, pk=None):
        """Ativar ou desativar usuário (apenas admin)"""
        if not request.user.has_permission('ADMINISTRADOR'):
            return Response(
                {'error': 'Permissão negada'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        usuario = self.get_object()
        usuario.ativo = not usuario.ativo
        usuario.save()
        
        status_msg = 'ativado' if usuario.ativo else 'desativado'
        return Response({
            'message': f'Usuário {status_msg} com sucesso',
            'ativo': usuario.ativo
        })


# Views simplificadas
class UsuarioCreateView(generics.CreateAPIView):
    """View para criação de usuários"""
    queryset = Usuario.objects.all()
    serializer_class = UsuarioCreateSerializer
    permission_classes = [permissions.AllowAny]


class UsuarioLoginView(generics.GenericAPIView):
    """View para login de usuários"""
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'error': 'Email e senha são obrigatórios'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(username=email, password=password)
        
        if not user:
            return Response(
                {'error': 'Credenciais inválidas'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.ativo:
            return Response(
                {'error': 'Usuário inativo'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UsuarioSerializer(user).data
        })


class UsuarioLogoutView(generics.GenericAPIView):
    """View para logout de usuários"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'message': 'Logout realizado com sucesso'})
        except Exception as e:
            return Response(
                {'error': 'Erro ao realizar logout'},
                status=status.HTTP_400_BAD_REQUEST
            )


class UsuarioProfileView(generics.RetrieveAPIView):
    """View para obter perfil do usuário atual"""
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UsuarioProfileUpdateView(generics.UpdateAPIView):
    """View para atualizar perfil do usuário atual"""
    serializer_class = UsuarioUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UsuarioListView(generics.ListAPIView):
    """View para listar usuários"""
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.has_permission('ADMINISTRADOR'):
            queryset = queryset.filter(id=self.request.user.id)
        return queryset.order_by('-date_joined')


class UsuarioDetailView(generics.RetrieveAPIView):
    """View para detalhes de usuário"""
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]


class UsuarioPermissionsView(generics.GenericAPIView):
    """View para obter permissões do usuário atual"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user_permissions = {
            'nivel_permissao': request.user.nivel_permissao,
            'permissoes': {
                'ADMINISTRADOR': request.user.has_permission('ADMINISTRADOR'),
                'FINANCEIRO': request.user.has_permission('FINANCEIRO'),
                'ATENDIMENTO': request.user.has_permission('ATENDIMENTO'),
            }
        }
        return Response(user_permissions)