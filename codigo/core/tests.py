from django.contrib.auth.models import User
from django.test import TestCase

from .models import (
    Autor, Categoria, ConfiguracaoBiblioteca, Contato, InteracaoLivro, Livro,
)


class LeitorTest(TestCase):
    """Fluxos do leitor comum: navegação, estante pessoal e avaliações."""

    def setUp(self):
        self.user = User.objects.create_user("leitor", password="leitor123", first_name="Léo")
        self.livro = Livro.objects.create(titulo="Dom Casmurro", ano=1899, exemplares=2)
        self.client.login(username="leitor", password="leitor123")

    def test_paginas_do_leitor(self):
        for url in ["/", "/acervo/", "/minha-central/", "/contato/", f"/livro/{self.livro.pk}/"]:
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_consulta_redireciona_para_acervo(self):
        resp = self.client.get("/consulta/", {"q": "Dom"})
        self.assertRedirects(resp, "/acervo/?q=Dom")

    def test_sem_login_redireciona(self):
        self.client.logout()
        self.assertEqual(self.client.get("/").status_code, 302)
        self.assertEqual(self.client.get("/acervo/").status_code, 302)

    def test_leitor_nao_acessa_gestao(self):
        for url in ["/livros/", "/autores/", "/categorias/", "/mensagens/", "/personalizacao/"]:
            resp = self.client.get(url)
            self.assertRedirects(resp, "/", msg_prefix=url)

    def test_estante_fila_lendo_lido(self):
        url = f"/livro/{self.livro.pk}/interagir/"
        self.client.post(url, {"acao": "fila"})
        i = InteracaoLivro.objects.get(usuario=self.user, livro=self.livro)
        self.assertEqual(i.status, "fila")

        self.client.post(url, {"acao": "lendo"})
        i.refresh_from_db()
        self.assertEqual(i.status, "lendo")

        self.client.post(url, {"acao": "lido"})
        i.refresh_from_db()
        self.assertEqual(i.status, "lido")

        resp = self.client.get("/minha-central/")
        self.assertContains(resp, "Dom Casmurro")

        # remover da estante sem favorito/avaliação apaga a interação
        self.client.post(url, {"acao": "remover"})
        self.assertFalse(InteracaoLivro.objects.filter(usuario=self.user, livro=self.livro).exists())

    def test_favoritar_e_desfavoritar(self):
        url = f"/livro/{self.livro.pk}/interagir/"
        self.client.post(url, {"acao": "favoritar"})
        self.assertTrue(InteracaoLivro.objects.get(usuario=self.user, livro=self.livro).favorito)
        self.client.post(url, {"acao": "favoritar"})
        self.assertFalse(InteracaoLivro.objects.filter(usuario=self.user, livro=self.livro).exists())

    def test_avaliar(self):
        self.client.post(f"/livro/{self.livro.pk}/avaliar/", {"nota": 5, "resenha": "Obra-prima."})
        i = InteracaoLivro.objects.get(usuario=self.user, livro=self.livro)
        self.assertEqual(i.avaliacao, 5)
        self.assertEqual(i.resenha, "Obra-prima.")
        resp = self.client.get(f"/livro/{self.livro.pk}/")
        self.assertContains(resp, "Obra-prima.")

    def test_avaliacao_invalida_nao_grava(self):
        self.client.post(f"/livro/{self.livro.pk}/avaliar/", {"nota": 9})
        self.assertFalse(InteracaoLivro.objects.exists())

    def test_filtros_do_acervo(self):
        cat = Categoria.objects.create(nome="Clássicos")
        self.livro.categorias.add(cat)
        Livro.objects.create(titulo="Outro Livro", ano=2020)

        resp = self.client.get("/acervo/", {"q": "Casmurro"})
        self.assertContains(resp, "Dom Casmurro")
        self.assertNotContains(resp, "Outro Livro")

        resp = self.client.get("/acervo/", {"categoria": cat.pk})
        self.assertContains(resp, "Dom Casmurro")
        self.assertNotContains(resp, "Outro Livro")


class RegistroTest(TestCase):
    def test_registro_cria_e_loga(self):
        resp = self.client.post("/registro/", {
            "first_name": "Ana", "email": "ana@ex.com", "username": "ana",
            "password1": "SenhaForte!42", "password2": "SenhaForte!42",
        })
        self.assertRedirects(resp, "/")
        self.assertTrue(User.objects.filter(username="ana").exists())
        # já está logada
        self.assertEqual(self.client.get("/minha-central/").status_code, 200)


class GestaoTest(TestCase):
    """Fluxos da equipe (staff): CRUDs, mensagens e personalização."""

    def setUp(self):
        User.objects.create_user("chefe", password="chefe123", is_staff=True)
        self.client.login(username="chefe", password="chefe123")

    def test_crud_livro(self):
        self.client.post("/livros/novo/", {"titulo": "Teste", "ano": 2026, "exemplares": 3})
        livro = Livro.objects.get(titulo="Teste")
        self.assertEqual(livro.exemplares, 3)
        self.client.post(f"/livros/{livro.pk}/editar/", {"titulo": "Teste 2", "ano": 2026, "exemplares": 3})
        self.assertTrue(Livro.objects.filter(titulo="Teste 2").exists())
        self.client.post(f"/livros/{livro.pk}/excluir/")
        self.assertFalse(Livro.objects.filter(pk=livro.pk).exists())

    def test_crud_autor(self):
        self.client.post("/autores/novo/", {"nome": "Autor X"})
        autor = Autor.objects.get(nome="Autor X")
        self.client.post(f"/autores/{autor.pk}/editar/", {"nome": "Autor Y"})
        self.assertTrue(Autor.objects.filter(nome="Autor Y").exists())
        self.client.post(f"/autores/{autor.pk}/excluir/")
        self.assertFalse(Autor.objects.filter(pk=autor.pk).exists())

    def test_crud_categoria(self):
        self.client.post("/categorias/nova/", {"nome": "Fantasia"})
        cat = Categoria.objects.get(nome="Fantasia")
        self.client.post(f"/categorias/{cat.pk}/editar/", {"nome": "Fantasia Épica"})
        self.assertTrue(Categoria.objects.filter(nome="Fantasia Épica").exists())
        self.client.post(f"/categorias/{cat.pk}/excluir/")
        self.assertFalse(Categoria.objects.filter(pk=cat.pk).exists())

    def test_contato_e_mensagens(self):
        self.client.post("/contato/", {"nome": "Ana", "email": "a@a.com", "mensagem": "Oi"})
        self.assertEqual(Contato.objects.count(), 1)
        self.assertContains(self.client.get("/mensagens/"), "Ana")

    def test_personalizacao(self):
        resp = self.client.post("/personalizacao/", {
            "nome": "Biblioteca Dom Pedro", "subtitulo": "Acervo Municipal",
            "cor_primaria": "#336699", "cor_destaque": "#cc8800", "cor_fundo": "#f4f4f0",
            "mensagem_boas_vindas": "Olá!", "rodape": "Prefeitura",
        })
        self.assertRedirects(resp, "/personalizacao/")
        config = ConfiguracaoBiblioteca.carregar()
        self.assertEqual(config.nome, "Biblioteca Dom Pedro")
        self.assertEqual(config.cor_primaria, "#336699")
        # o tema aparece nas páginas
        resp = self.client.get("/")
        self.assertContains(resp, "Biblioteca Dom Pedro")
        self.assertContains(resp, "#336699")

    def test_cores_derivadas(self):
        config = ConfiguracaoBiblioteca.carregar()
        config.cor_primaria = "#000000"
        self.assertEqual(config.cor_primaria_escura, "#000000")
        config.cor_primaria = "#ffffff"
        self.assertEqual(config.cor_primaria_clara, "#ffffff")
