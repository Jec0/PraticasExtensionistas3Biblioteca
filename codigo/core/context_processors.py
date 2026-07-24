from .models import ConfiguracaoBiblioteca


def configuracao(request):
    """Disponibiliza a configuração de marca/tema em todos os templates."""
    return {"config": ConfiguracaoBiblioteca.carregar()}
