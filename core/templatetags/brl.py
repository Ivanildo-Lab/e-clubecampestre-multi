from django import template

register = template.Library()

@register.filter(name='brl')
def brl(value):
    """Formata Decimal/float como moeda brasileira: 9250.23 -> 9.250,23"""
    if value is None:
        return "0,00"
    try:
        # Converte para float para formatar
        v = float(value)
        # Formata com separador americano e depois converte
        s = f"{v:,.2f}"  # 9,250.23
        # Troca , por X temporário, . por ,, X por .
        s = s.replace(",", "X").replace(".", ",").replace("X", ".")
        return s
    except:
        return str(value)

@register.filter(name='brl_currency')
def brl_currency(value):
    return f"R$ {brl(value)}"
