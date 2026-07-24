from django.contrib import admin

from .models import (
    Autor, Categoria, ConfiguracaoBiblioteca, Contato, Emprestimo,
    InteracaoLivro, Livro, Usuario,
)


@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ["titulo", "ano", "editora", "exemplares"]
    list_filter = ["categorias"]
    search_fields = ["titulo", "isbn", "autores__nome"]
    filter_horizontal = ["autores", "categorias"]


@admin.register(InteracaoLivro)
class InteracaoLivroAdmin(admin.ModelAdmin):
    list_display = ["usuario", "livro", "status", "favorito", "avaliacao", "atualizado_em"]
    list_filter = ["status", "favorito", "avaliacao"]


admin.site.register([Autor, Categoria, ConfiguracaoBiblioteca, Usuario, Emprestimo, Contato])
