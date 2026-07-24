from functools import wraps

from django import forms
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.forms import ModelForm
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Autor, Categoria, ConfiguracaoBiblioteca, Contato, InteracaoLivro, Livro


def staff_required(view):
    """Restringe a view à equipe da biblioteca (staff)."""
    @wraps(view)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, "Área restrita à equipe da biblioteca.")
            return redirect("home")
        return view(request, *args, **kwargs)
    return wrapper


# ---------- Formulários ----------

class LivroForm(ModelForm):
    class Meta:
        model = Livro
        fields = [
            "titulo", "ano", "autores", "categorias", "sinopse", "isbn",
            "editora", "paginas", "exemplares", "capa", "capa_url",
        ]
        widgets = {"sinopse": forms.Textarea(attrs={"rows": 4})}


class AutorForm(ModelForm):
    class Meta:
        model = Autor
        fields = ["nome"]


class CategoriaForm(ModelForm):
    class Meta:
        model = Categoria
        fields = ["nome"]


class ContatoForm(ModelForm):
    class Meta:
        model = Contato
        fields = ["nome", "email", "mensagem"]


class ConfiguracaoForm(ModelForm):
    class Meta:
        model = ConfiguracaoBiblioteca
        fields = [
            "nome", "subtitulo", "logo", "cor_primaria", "cor_destaque",
            "cor_fundo", "mensagem_boas_vindas", "rodape",
        ]
        widgets = {
            "cor_primaria": forms.TextInput(attrs={"type": "color"}),
            "cor_destaque": forms.TextInput(attrs={"type": "color"}),
            "cor_fundo": forms.TextInput(attrs={"type": "color"}),
            "mensagem_boas_vindas": forms.Textarea(attrs={"rows": 3}),
        }


class RegistroForm(UserCreationForm):
    first_name = forms.CharField(label="Nome", max_length=150)
    email = forms.EmailField(label="E-mail")

    class Meta:
        model = User
        fields = ["first_name", "email", "username", "password1", "password2"]


# ---------- Páginas principais ----------

@login_required
def home(request):
    recentes = Livro.objects.prefetch_related("autores").order_by("-pk")[:6]
    populares = (
        Livro.objects.prefetch_related("autores")
        .annotate(
            leitores=Count("interacoes", filter=Q(interacoes__status=InteracaoLivro.Status.LIDO)),
            nota_media=Avg("interacoes__avaliacao"),
        )
        .filter(Q(leitores__gt=0) | Q(nota_media__isnull=False))
        .order_by("-leitores", "-nota_media")[:6]
    )
    minha_fila = (
        InteracaoLivro.objects.filter(usuario=request.user, status=InteracaoLivro.Status.FILA)
        .select_related("livro")[:4]
    )
    contexto = {
        "total_livros": Livro.objects.count(),
        "total_autores": Autor.objects.count(),
        "total_categorias": Categoria.objects.count(),
        "total_leitores": User.objects.filter(is_active=True).count(),
        "recentes": recentes,
        "populares": populares,
        "minha_fila": minha_fila,
    }
    return render(request, "core/home.html", contexto)


def registro(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = RegistroForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Conta criada com sucesso.")
        return redirect("home")
    return render(request, "core/registro.html", {"form": form})


# ---------- Acervo (catálogo com capas e filtros) ----------

@login_required
def acervo(request):
    q = request.GET.get("q", "").strip()
    categoria_id = request.GET.get("categoria", "")
    ordem = request.GET.get("ordem", "titulo")

    livros = Livro.objects.prefetch_related("autores", "categorias").annotate(
        nota_media=Avg("interacoes__avaliacao")
    )
    if q:
        livros = livros.filter(
            Q(titulo__icontains=q) | Q(autores__nome__icontains=q) | Q(isbn__icontains=q)
        ).distinct()
    if categoria_id.isdigit():
        livros = livros.filter(categorias__id=categoria_id)

    ordens = {"titulo": "titulo", "recentes": "-pk", "ano": "-ano", "avaliacao": "-nota_media"}
    livros = livros.order_by(ordens.get(ordem, "titulo"))

    paginador = Paginator(livros, 24)
    pagina = paginador.get_page(request.GET.get("pagina"))

    minhas = {
        i.livro_id: i
        for i in InteracaoLivro.objects.filter(usuario=request.user, livro__in=pagina.object_list)
    }
    contexto = {
        "pagina": pagina,
        "q": q,
        "categorias": Categoria.objects.all(),
        "categoria_id": categoria_id,
        "ordem": ordem,
        "minhas": minhas,
    }
    return render(request, "core/acervo.html", contexto)


@login_required
def livro_detalhe(request, pk):
    livro = get_object_or_404(Livro.objects.prefetch_related("autores", "categorias"), pk=pk)
    interacao = InteracaoLivro.objects.filter(usuario=request.user, livro=livro).first()
    resenhas = (
        livro.interacoes.filter(avaliacao__isnull=False)
        .select_related("usuario")
        .order_by("-atualizado_em")
    )
    nota_media = resenhas.aggregate(m=Avg("avaliacao"))["m"]
    contexto = {
        "livro": livro,
        "interacao": interacao,
        "resenhas": resenhas,
        "nota_media": nota_media,
        "estrelas": range(1, 6),
    }
    return render(request, "core/livro_detalhe.html", contexto)


@login_required
@require_POST
def livro_interagir(request, pk):
    livro = get_object_or_404(Livro, pk=pk)
    acao = request.POST.get("acao", "")
    interacao, _ = InteracaoLivro.objects.get_or_create(usuario=request.user, livro=livro)

    if acao in InteracaoLivro.Status.values:
        interacao.status = acao
        interacao.save()
        messages.success(request, f'"{livro.titulo}" marcado como {interacao.get_status_display().lower()}.')
    elif acao == "remover":
        interacao.status = ""
        interacao.save()
        messages.success(request, f'"{livro.titulo}" removido da sua estante.')
    elif acao == "favoritar":
        interacao.favorito = not interacao.favorito
        interacao.save()
        texto = "adicionado aos" if interacao.favorito else "removido dos"
        messages.success(request, f'"{livro.titulo}" {texto} favoritos.')

    if not interacao.favorito and not interacao.status and interacao.avaliacao is None:
        interacao.delete()

    proximo = request.POST.get("proximo", "")
    if proximo.startswith("/"):  # volta para a página de origem (acervo, central...)
        return redirect(proximo)
    return redirect("livro_detalhe", pk=pk)


@login_required
@require_POST
def livro_avaliar(request, pk):
    livro = get_object_or_404(Livro, pk=pk)
    try:
        nota = int(request.POST.get("nota", ""))
    except ValueError:
        nota = 0
    if 1 <= nota <= 5:
        interacao, _ = InteracaoLivro.objects.get_or_create(usuario=request.user, livro=livro)
        interacao.avaliacao = nota
        interacao.resenha = request.POST.get("resenha", "").strip()
        interacao.save()
        messages.success(request, "Avaliação registrada.")
    else:
        messages.error(request, "Escolha uma nota de 1 a 5 estrelas.")
    return redirect("livro_detalhe", pk=pk)


# ---------- Minha Central ----------

@login_required
def minha_central(request):
    interacoes = InteracaoLivro.objects.filter(usuario=request.user).select_related("livro").prefetch_related("livro__autores")
    por_status = lambda s: [i for i in interacoes if i.status == s]  # noqa: E731
    lendo = por_status(InteracaoLivro.Status.LENDO)
    fila = por_status(InteracaoLivro.Status.FILA)
    lidos = por_status(InteracaoLivro.Status.LIDO)
    favoritos = [i for i in interacoes if i.favorito]
    avaliacoes = [i for i in interacoes if i.avaliacao]
    notas = [i.avaliacao for i in avaliacoes]
    contexto = {
        "lendo": lendo,
        "fila": fila,
        "lidos": lidos,
        "favoritos": favoritos,
        "avaliacoes": avaliacoes,
        "nota_media": round(sum(notas) / len(notas), 1) if notas else None,
    }
    return render(request, "core/minha_central.html", contexto)


# ---------- Personalização (white-label) ----------

@staff_required
def personalizacao(request):
    config = ConfiguracaoBiblioteca.carregar()
    form = ConfiguracaoForm(request.POST or None, request.FILES or None, instance=config)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Personalização salva.")
        return redirect("personalizacao")
    return render(request, "core/personalizacao.html", {"form": form})


# ---------- CRUD de Livros (equipe) ----------

@staff_required
def livro_list(request):
    livros = Livro.objects.prefetch_related("autores", "categorias")
    return render(request, "core/livro_list.html", {"livros": livros})


@staff_required
def livro_form(request, pk=None):
    livro = get_object_or_404(Livro, pk=pk) if pk else None
    form = LivroForm(request.POST or None, request.FILES or None, instance=livro)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Livro salvo com sucesso.")
        return redirect("livro_list")
    return render(request, "core/livro_form.html", {"form": form, "livro": livro})


@staff_required
def livro_delete(request, pk):
    livro = get_object_or_404(Livro, pk=pk)
    if request.method == "POST":
        livro.delete()
        messages.success(request, "Livro excluído.")
        return redirect("livro_list")
    return render(request, "core/livro_delete.html", {"livro": livro})


# ---------- CRUD de Autores (equipe) ----------

@staff_required
def autor_list(request):
    return render(request, "core/autor_list.html", {"autores": Autor.objects.annotate(qtd=Count("livros"))})


@staff_required
def autor_form(request, pk=None):
    autor = get_object_or_404(Autor, pk=pk) if pk else None
    form = AutorForm(request.POST or None, instance=autor)
    if form.is_valid():
        form.save()
        messages.success(request, "Autor salvo com sucesso.")
        return redirect("autor_list")
    return render(request, "core/autor_form.html", {"form": form, "autor": autor})


@staff_required
def autor_delete(request, pk):
    autor = get_object_or_404(Autor, pk=pk)
    if request.method == "POST":
        autor.delete()
        messages.success(request, "Autor excluído.")
        return redirect("autor_list")
    return render(request, "core/autor_delete.html", {"autor": autor})


# ---------- CRUD de Categorias (equipe) ----------

@staff_required
def categoria_list(request):
    return render(request, "core/categoria_list.html", {"categorias": Categoria.objects.annotate(qtd=Count("livros"))})


@staff_required
def categoria_form(request, pk=None):
    categoria = get_object_or_404(Categoria, pk=pk) if pk else None
    form = CategoriaForm(request.POST or None, instance=categoria)
    if form.is_valid():
        form.save()
        messages.success(request, "Categoria salva com sucesso.")
        return redirect("categoria_list")
    return render(request, "core/categoria_form.html", {"form": form, "categoria": categoria})


@staff_required
def categoria_delete(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == "POST":
        categoria.delete()
        messages.success(request, "Categoria excluída.")
        return redirect("categoria_list")
    return render(request, "core/categoria_delete.html", {"categoria": categoria})


# ---------- Mensagens recebidas (somente administrador) ----------

@staff_required
def mensagens(request):
    lista = Contato.objects.order_by("-enviado_em")
    return render(request, "core/mensagens.html", {"mensagens": lista})


# ---------- Contato ----------

def contato(request):
    form = ContatoForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Mensagem enviada à equipe da biblioteca.")
        return redirect("contato")
    return render(request, "core/contato.html", {"form": form})
