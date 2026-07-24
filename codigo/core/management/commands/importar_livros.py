"""
Importa livros reais do Open Library por assunto, com capa, autores, ano,
páginas e ISBN. Prioriza edições em português e completa com títulos
populares em outros idiomas se necessário.

Uso:
    python manage.py importar_livros              # importa até o acervo ter 500 livros
    python manage.py importar_livros --alvo 300   # outro tamanho de acervo
"""
import json
import re
import unicodedata
import urllib.parse
import urllib.request

from django.core.management.base import BaseCommand

from core.models import Autor, Categoria, Livro

# Caracteres fora do alfabeto latino (cirílico, grego, árabe, hebraico, CJK, hangul...)
NAO_LATINO = re.compile(
    r"[Ͱ-ϿЀ-ӿ֐-׿؀-ۿ"
    r"ऀ-෿฀-๿぀-ヿ㐀-鿿가-힯]"
)


def normalizar(texto):
    return unicodedata.normalize("NFC", texto).strip()

# (consulta de assunto no Open Library, [categorias do sistema])
ASSUNTOS = [
    ("science_fiction", ["Ficção Científica"]),
    ("fantasy", ["Fantasia"]),
    ("horror", ["Terror"]),
    ("detective and mystery stories", ["Mistério"]),
    ("romance", ["Romance"]),
    ("adventure stories", ["Aventura"]),
    ("short stories", ["Contos"]),
    ("poetry", ["Poesia"]),
    ("drama", ["Teatro"]),
    ("juvenile fiction", ["Infantojuvenil"]),
    ("dystopias", ["Distopia"]),
    ("classic literature", ["Clássicos"]),
    ("brazilian fiction", ["Literatura Brasileira"]),
    ("history", ["Não ficção", "História"]),
    ("biography", ["Não ficção", "Biografia"]),
    ("science", ["Não ficção", "Ciências"]),
    ("philosophy", ["Não ficção", "Filosofia"]),
    ("psychology", ["Não ficção", "Psicologia"]),
    ("fiction", ["Literatura Estrangeira"]),
]

CAMPOS = "title,author_name,first_publish_year,cover_i,isbn,number_of_pages_median"
POR_PAGINA = 100


def buscar(assunto, pagina, idioma=None):
    q = f'subject:"{assunto}"'
    if idioma:
        q += f" language:{idioma}"
    params = {
        "q": q,
        "fields": CAMPOS,
        "limit": POR_PAGINA,
        "offset": pagina * POR_PAGINA,
        "sort": "editions",  # obras com mais edições primeiro (mais conhecidas)
    }
    url = "https://openlibrary.org/search.json?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=25) as resposta:
            return json.load(resposta).get("docs", [])
    except Exception:
        return []


def doc_valido(doc):
    titulo = normalizar(doc.get("title") or "")
    autores = [normalizar(a) for a in doc.get("author_name") or []]
    return (
        titulo
        and len(titulo) <= 100
        and "summary" not in titulo.lower()
        and not NAO_LATINO.search(titulo)
        and doc.get("cover_i")
        and autores
        and not any(NAO_LATINO.search(a) for a in autores)
        and doc.get("first_publish_year")
        and 1000 <= doc["first_publish_year"] <= 2026
    )


class Command(BaseCommand):
    help = "Importa livros do Open Library até o acervo atingir o tamanho alvo."

    def add_arguments(self, parser):
        parser.add_argument("--alvo", type=int, default=500, help="Tamanho final do acervo.")

    def handle(self, *args, **opcoes):
        alvo = opcoes["alvo"]
        titulos = {t.lower() for t in Livro.objects.values_list("titulo", flat=True)}
        categorias = {}

        def obter_categoria(nome):
            if nome not in categorias:
                categorias[nome], _ = Categoria.objects.get_or_create(nome=nome)
            return categorias[nome]

        criados = 0
        # 1ª passada: só edições em português; 2ª: qualquer idioma
        for idioma in ("por", None):
            if Livro.objects.count() >= alvo:
                break
            rotulo = "português" if idioma else "todos os idiomas"
            self.stdout.write(f"--- Passada: {rotulo} ---")
            for assunto, nomes_cat in ASSUNTOS:
                if Livro.objects.count() >= alvo:
                    break
                novos_do_assunto = 0
                for pagina in range(3):  # até 300 resultados por assunto
                    if Livro.objects.count() >= alvo or novos_do_assunto >= 40:
                        break
                    docs = buscar(assunto, pagina, idioma)
                    if not docs:
                        break
                    for doc in docs:
                        if Livro.objects.count() >= alvo or novos_do_assunto >= 40:
                            break
                        if not doc_valido(doc):
                            continue
                        titulo = normalizar(doc["title"])
                        if titulo.lower() in titulos:
                            continue
                        livro = Livro.objects.create(
                            titulo=titulo,
                            ano=doc["first_publish_year"],
                            capa_url=f"https://covers.openlibrary.org/b/id/{doc['cover_i']}-L.jpg",
                            isbn=next((i for i in doc.get("isbn", []) if len(i) == 13), ""),
                            paginas=doc.get("number_of_pages_median") or None,
                        )
                        livro.exemplares = 1 + (livro.pk % 4)
                        livro.save()
                        livro.autores.set([
                            Autor.objects.get_or_create(nome=normalizar(n)[:100])[0]
                            for n in doc["author_name"][:2]
                        ])
                        livro.categorias.set([obter_categoria(n) for n in nomes_cat])
                        titulos.add(titulo.lower())
                        criados += 1
                        novos_do_assunto += 1
                self.stdout.write(f"  {assunto}: +{novos_do_assunto} (acervo: {Livro.objects.count()})")

        self.stdout.write(self.style.SUCCESS(
            f"Importação concluída: {criados} livros novos, acervo com {Livro.objects.count()}."
        ))
