from django.urls import path
from .views import MensalidadeListView, MarcarComoPagaView, MensalidadeUpdateView, GerarMensalidadesEmMassaView


app_name = 'financeiro'

urlpatterns = [
    path('mensalidades/', MensalidadeListView.as_view(), name='lista_mensalidades'),
    path('mensalidades/<int:pk>/marcar-paga/', MarcarComoPagaView.as_view(), name='marcar_paga'),
    path('mensalidades/<int:pk>/editar/', MensalidadeUpdateView.as_view(), name='editar_mensalidade'),
    path('mensalidades/gerar-em-massa/', GerarMensalidadesEmMassaView.as_view(), name='gerar_mensalidades_massa'),
]