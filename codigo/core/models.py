from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models

hex_color = RegexValidator(r"^#[0-9a-fA-F]{6}$", "Informe uma cor no formato #RRGGBB.")


class ConfiguracaoBiblioteca(models.Model):
    """Configuração de marca/tema da biblioteca (registro único, editável pelo administrador)."""

    nome = models.CharField("Nome da biblioteca", max_length=80, default="Biblioteca")
    subtitulo = models.CharField("Subtítulo", max_length=120, default="Sistema de Gestão", blank=True)
    logo = models.ImageField("Logo", upload_to="logo/", blank=True, null=True)
    cor_primaria = models.CharField("Cor primária", max_length=7, default="#24425c", validators=[hex_color])
    cor_destaque = models.CharField("Cor de destaque", max_length=7, default="#b7791f", validators=[hex_color])
    cor_fundo = models.CharField("Cor de fundo", max_length=7, default="#eef0f2", validators=[hex_color])
    mensagem_boas_vindas = models.TextField(
        "Mensagem de boas-vindas", blank=True,
        default="Consulte o acervo, organize sua fila de leitura e acompanhe suas leituras.",
    )
    rodape = models.CharField("Texto do rodapé", max_length=200, blank=True, default="")

    class Meta:
        verbose_name = "Configuração da biblioteca"
        verbose_name_plural = "Configuração da biblioteca"

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        self.pk = 1  # registro único
        super().save(*args, **kwargs)

    @classmethod
    def carregar(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @staticmethod
    def _ajustar(cor, fator):
        """Clareia (fator > 0) ou escurece (fator < 0) uma cor #RRGGBB."""
        try:
            r, g, b = (int(cor[i:i + 2], 16) for i in (1, 3, 5))
        except (ValueError, IndexError):
            return cor
        if fator >= 0:
            r, g, b = (round(c + (255 - c) * fator) for c in (r, g, b))
        else:
            r, g, b = (round(c * (1 + fator)) for c in (r, g, b))
        return f"#{r:02x}{g:02x}{b:02x}"

    @property
    def cor_primaria_escura(self):
        return self._ajustar(self.cor_primaria, -0.28)

    @property
    def cor_primaria_clara(self):
        return self._ajustar(self.cor_primaria, 0.88)


class Autor(models.Model):
    nome = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Autores"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Categoria(models.Model):
    nome = models.CharField(max_length=60, unique=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Livro(models.Model):
    titulo = models.CharField(max_length=100)
    ano = models.PositiveIntegerField()
    autores = models.ManyToManyField(Autor, related_name="livros", blank=True)
    categorias = models.ManyToManyField(Categoria, related_name="livros", blank=True)
    sinopse = models.TextField(blank=True)
    isbn = models.CharField("ISBN", max_length=20, blank=True)
    editora = models.CharField(max_length=100, blank=True)
    paginas = models.PositiveIntegerField("Páginas", null=True, blank=True)
    capa = models.ImageField("Capa (arquivo)", upload_to="capas/", blank=True, null=True)
    capa_url = models.URLField("Capa (URL)", max_length=300, blank=True)
    exemplares = models.PositiveIntegerField("Exemplares", default=1)

    class Meta:
        ordering = ["titulo"]

    def __str__(self):
        return self.titulo

    @property
    def capa_src(self):
        """URL da capa: arquivo enviado tem prioridade sobre a URL externa."""
        if self.capa:
            return self.capa.url
        return self.capa_url or ""

    @property
    def emprestados(self):
        return self.emprestimos.filter(data_devolucao__isnull=True).count()

    @property
    def disponiveis(self):
        return max(self.exemplares - self.emprestados, 0)


class Usuario(models.Model):
    """Leitor da biblioteca (tabela Usuario do modelo relacional)."""
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=100)

    def __str__(self):
        return self.nome


class Emprestimo(models.Model):
    data_emprestimo = models.DateField()
    data_devolucao = models.DateField(null=True, blank=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name="emprestimos")
    funcionario = models.ForeignKey("auth.User", on_delete=models.PROTECT, related_name="emprestimos")
    livros = models.ManyToManyField(Livro, related_name="emprestimos")

    def __str__(self):
        return f"Empréstimo #{self.pk} - {self.usuario}"


class InteracaoLivro(models.Model):
    """Relação de um leitor (usuário logado) com um livro: estante pessoal, favorito e avaliação."""

    class Status(models.TextChoices):
        FILA = "fila", "Na fila"
        LENDO = "lendo", "Lendo"
        LIDO = "lido", "Lido"

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="interacoes")
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE, related_name="interacoes")
    status = models.CharField(max_length=10, choices=Status.choices, blank=True)
    favorito = models.BooleanField(default=False)
    avaliacao = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    resenha = models.TextField(blank=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("usuario", "livro")]
        verbose_name = "Interação com livro"
        verbose_name_plural = "Interações com livros"

    def __str__(self):
        return f"{self.usuario} × {self.livro}"


class Contato(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    mensagem = models.TextField()
    enviado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} ({self.enviado_em:%d/%m/%Y})"
