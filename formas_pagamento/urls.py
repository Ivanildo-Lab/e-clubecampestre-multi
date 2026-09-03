from django.urls import path
from .views import (
    FormaPagamentoListView,
    FormaPagamentoCreateView,
    FormaPagamentoUpdateView,
    FormaPagamentoDeleteView,
)

app_name = 'formas_pagamento'

urlpatterns = [
    path('', FormaPagamentoListView.as_view(), name='lista_formas_pagamento'),
    path('adicionar/', FormaPagamentoCreateView.as_view(), name='adicionar_forma_pagamento'),
    path('<int:pk>/editar/', FormaPagamentoUpdateView.as_view(), name='editar_forma_pagamento'),
    path('<int:pk>/excluir/', FormaPagamentoDeleteView.as_view(), name='excluir_forma_pagamento'),
]
