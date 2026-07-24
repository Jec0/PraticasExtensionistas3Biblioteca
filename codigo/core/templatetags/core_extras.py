from django import template

register = template.Library()


@register.filter
def dictkey(dicionario, chave):
    """Retorna dicionario[chave] ou None. Uso: {{ meu_dict|dictkey:objeto.pk }}"""
    if dicionario:
        return dicionario.get(chave)
    return None
