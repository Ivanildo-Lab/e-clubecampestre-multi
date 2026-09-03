from django.contrib import admin
from .models import Venda, ItemVenda


class ItemVendaInline(admin.TabularInline):
    model = ItemVenda
    extra = 0
    readonly_fields = ('subtotal',)


@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ('id', 'empresa', 'socio', 'tipo', 'valor_total', 'status', 'data_venda', 'usuario')
    list_filter = ('tipo', 'status', 'data_venda')
    search_fields = ('observacao', 'socio__nome')
    inlines = [ItemVendaInline]
    readonly_fields = ('valor_total',)


@admin.register(ItemVenda)
class ItemVendaAdmin(admin.ModelAdmin):
    list_display = ('venda', 'produto', 'quantidade', 'preco_unitario', 'subtotal')
    search_fields = ('produto__nome',)
