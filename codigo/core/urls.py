from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", auth_views.LoginView.as_view(template_name="core/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("registro/", views.registro, name="registro"),

    # Acervo e interações do leitor
    path("acervo/", views.acervo, name="acervo"),
    path("consulta/", RedirectView.as_view(pattern_name="acervo", query_string=True), name="consulta"),
    path("livro/<int:pk>/", views.livro_detalhe, name="livro_detalhe"),
    path("livro/<int:pk>/interagir/", views.livro_interagir, name="livro_interagir"),
    path("livro/<int:pk>/avaliar/", views.livro_avaliar, name="livro_avaliar"),
    path("minha-central/", views.minha_central, name="minha_central"),

    # Gestão (equipe)
    path("personalizacao/", views.personalizacao, name="personalizacao"),
    path("livros/", views.livro_list, name="livro_list"),
    path("livros/novo/", views.livro_form, name="livro_novo"),
    path("livros/<int:pk>/editar/", views.livro_form, name="livro_editar"),
    path("livros/<int:pk>/excluir/", views.livro_delete, name="livro_excluir"),
    path("autores/", views.autor_list, name="autor_list"),
    path("autores/novo/", views.autor_form, name="autor_novo"),
    path("autores/<int:pk>/editar/", views.autor_form, name="autor_editar"),
    path("autores/<int:pk>/excluir/", views.autor_delete, name="autor_excluir"),
    path("categorias/", views.categoria_list, name="categoria_list"),
    path("categorias/nova/", views.categoria_form, name="categoria_nova"),
    path("categorias/<int:pk>/editar/", views.categoria_form, name="categoria_editar"),
    path("categorias/<int:pk>/excluir/", views.categoria_delete, name="categoria_excluir"),
    path("mensagens/", views.mensagens, name="mensagens"),

    path("contato/", views.contato, name="contato"),
]
