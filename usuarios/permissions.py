from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permissão customizada que permite acesso apenas ao dono do objeto ou a administradores.
    """
    
    def has_object_permission(self, request, view, obj):
        # Administradores podem fazer tudo
        if request.user.has_permission('ADMINISTRADOR'):
            return True
        
        # Dono do objeto pode acessar
        return obj == request.user


class IsAdminUser(permissions.BasePermission):
    """
    Permissão que permite acesso apenas a administradores.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.has_permission('ADMINISTRADOR')


class IsFinanceiroOrAdmin(permissions.BasePermission):
    """
    Permissão que permite acesso a usuários com permissão FINANCEIRO ou ADMINISTRADOR.
    """
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.has_permission('FINANCEIRO')
        )


class IsAtendimentoOrAbove(permissions.BasePermission):
    """
    Permissão que permite acesso a usuários com permissão ATENDIMENTO ou superior.
    """
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.has_permission('ATENDIMENTO')
        )