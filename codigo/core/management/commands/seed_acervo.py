"""
Enriquece o acervo: categorias, sinopses, páginas, exemplares e capas (Open Library),
além de cadastrar novos títulos populares. Idempotente — pode rodar mais de uma vez.

Uso:
    python manage.py seed_acervo             # completo (busca capas na internet)
    python manage.py seed_acervo --sem-capas # não acessa a internet
"""
import json
import urllib.parse
import urllib.request

from django.core.management.base import BaseCommand

from core.models import Autor, Categoria, ConfiguracaoBiblioteca, Livro

# titulo: (categorias, sinopse, paginas, busca_no_openlibrary_ou_None)
DADOS = {
    "Dom Casmurro": (["Literatura Brasileira", "Clássicos", "Romance"], "Bento Santiago narra sua vida e o ciúme que o consome ao suspeitar de Capitu, no romance mais debatido da literatura brasileira.", 256, None),
    "A Hora da Estrela": (["Literatura Brasileira", "Clássicos"], "A nordestina Macabéa vaga por um Rio de Janeiro indiferente nesta novela comovente sobre invisibilidade e destino.", 88, None),
    "Memórias Póstumas de Brás Cubas": (["Literatura Brasileira", "Clássicos"], "Um defunto autor narra com ironia a própria vida, inaugurando o realismo no Brasil.", 208, None),
    "Quincas Borba": (["Literatura Brasileira", "Clássicos"], "Rubião herda a fortuna e a filosofia do Humanitismo de Quincas Borba — e é devorado pela corte carioca.", 240, None),
    "O Alienista": (["Literatura Brasileira", "Clássicos", "Contos"], "O médico Simão Bacamarte transforma Itaguaí num laboratório da loucura nesta sátira genial sobre ciência e poder.", 96, None),
    "Perto do Coração Selvagem": (["Literatura Brasileira", "Clássicos"], "O romance de estreia de Clarice acompanha o fluxo de consciência de Joana, entre a infância e o casamento.", 224, None),
    "Laços de Família": (["Literatura Brasileira", "Contos"], "Treze contos sobre epifanias domésticas — o cotidiano que se rompe e revela o estranho.", 160, None),
    "Capitães da Areia": (["Literatura Brasileira", "Clássicos"], "Meninos de rua de Salvador vivem entre o crime e a ternura neste retrato social inesquecível.", 288, None),
    "Gabriela, Cravo e Canela": (["Literatura Brasileira", "Romance"], "A chegada de Gabriela transforma Ilhéus nos anos do cacau, entre o coronelismo e o desejo.", 424, None),
    "Dona Flor e Seus Dois Maridos": (["Literatura Brasileira", "Romance"], "Viúva do boêmio Vadinho e casada com o certinho Teodoro, Flor se vê entre dois maridos — um deles fantasma.", 480, None),
    "Vidas Secas": (["Literatura Brasileira", "Clássicos"], "A família de Fabiano atravessa o sertão em retirada, numa prosa seca como a paisagem.", 176, None),
    "São Bernardo": (["Literatura Brasileira", "Clássicos"], "Paulo Honório conquista terras e poder, mas destrói tudo o que ama — inclusive Madalena.", 192, None),
    "Angústia": (["Literatura Brasileira", "Clássicos"], "O monólogo febril de Luís da Silva, funcionário público consumido pela obsessão e pelo rancor.", 288, None),
    "Iracema": (["Literatura Brasileira", "Clássicos", "Romance"], "A lenda da virgem dos lábios de mel e do guerreiro branco Martim, mito de fundação do Ceará.", 128, None),
    "O Guarani": (["Literatura Brasileira", "Clássicos", "Aventura"], "O índio Peri e Cecília vivem um amor impossível entre os perigos do Brasil colonial.", 384, None),
    "Senhora": (["Literatura Brasileira", "Clássicos", "Romance"], "Aurélia compra em leilão o homem que a rejeitou, num acerto de contas sobre amor e dinheiro.", 288, None),
    "O Cortiço": (["Literatura Brasileira", "Clássicos"], "A vida pulsante de um cortiço carioca, onde o meio molda — e corrói — seus moradores.", 304, None),
    "Grande Sertão: Veredas": (["Literatura Brasileira", "Clássicos"], "Riobaldo revive a travessia do sertão, o pacto com o demo e o amor por Diadorim.", 608, None),
    "Sagarana": (["Literatura Brasileira", "Contos"], "Nove novelas do sertão mineiro, onde bois, jagunços e burrinhos carregam filosofia.", 336, None),
    "Olhai os Lírios do Campo": (["Literatura Brasileira", "Romance"], "O médico Eugênio persegue riqueza e status até aprender, tarde, o valor do essencial.", 304, None),
    "Triste Fim de Policarpo Quaresma": (["Literatura Brasileira", "Clássicos"], "O patriota Policarpo Quaresma acredita no Brasil até as últimas consequências.", 256, None),
    "Os Sertões": (["Literatura Brasileira", "Clássicos", "Não ficção"], "A guerra de Canudos narrada como epopeia: a terra, o homem e a luta.", 528, None),
    "Macunaíma": (["Literatura Brasileira", "Clássicos"], "O herói sem nenhum caráter atravessa o Brasil em delírio modernista.", 224, None),
    "O Quinze": (["Literatura Brasileira", "Clássicos"], "A seca de 1915 no Ceará marca o destino de Conceição e do vaqueiro Vicente.", 160, None),
    "A Rosa do Povo": (["Literatura Brasileira", "Poesia"], "Drummond em sua fase mais engajada: a poesia diante da guerra e da esperança.", 304, None),
    "Sentimento do Mundo": (["Literatura Brasileira", "Poesia"], "Poemas entre o eu e o mundo em colapso, do maior poeta brasileiro do século XX.", 96, None),
    "Libertinagem": (["Literatura Brasileira", "Poesia"], "O livro em que Bandeira encontra sua voz definitiva — de 'Vou-me embora pra Pasárgada' ao cotidiano transfigurado.", 96, None),
    "Auto da Compadecida": (["Literatura Brasileira", "Teatro"], "João Grilo e Chicó enganam a morte no sertão, num auto que mistura riso e fé.", 208, None),
    "O Pagador de Promessas": (["Literatura Brasileira", "Teatro"], "Zé do Burro cumpre sua promessa carregando uma cruz — e esbarra na intolerância da cidade.", 144, None),
    "Vestido de Noiva": (["Literatura Brasileira", "Teatro"], "Três planos — realidade, memória e alucinação — se cruzam na peça que revolucionou o teatro brasileiro.", 176, None),
    "Reinações de Narizinho": (["Literatura Brasileira", "Infantojuvenil"], "As primeiras aventuras do Sítio do Picapau Amarelo, com Narizinho, Emília e o Visconde.", 320, None),
    "Dois Irmãos": (["Literatura Brasileira", "Romance"], "A rivalidade dos gêmeos Yaqub e Omar despedaça uma família libanesa em Manaus.", 264, None),
    "Leite Derramado": (["Literatura Brasileira", "Romance"], "Um centenário delirante narra dois séculos de Brasil a partir de um leito de hospital.", 200, None),
    "Budapeste": (["Literatura Brasileira", "Romance"], "Um ghost-writer carioca se apaixona por Budapeste e pelo idioma húngaro — e se desdobra em dois.", 176, None),
    "Olhos d'Água": (["Literatura Brasileira", "Contos"], "Quinze contos sobre mulheres negras brasileiras, entre a dor e a resistência.", 116, None),
    "Ponciá Vicêncio": (["Literatura Brasileira", "Romance"], "Ponciá deixa a terra dos antepassados rumo à cidade, carregando memória e herança escravista.", 128, None),
    "Torto Arado": (["Literatura Brasileira", "Romance"], "As irmãs Bibiana e Belonísia partilham uma língua e um destino no coração da Chapada Diamantina.", 264, None),
    "O Alquimista": (["Literatura Brasileira", "Romance", "Aventura"], "O pastor Santiago cruza o deserto em busca de seu tesouro — e de sua Lenda Pessoal.", 208, ("The Alchemist", "Paulo Coelho")),
    "1984": (["Literatura Estrangeira", "Distopia", "Ficção Científica"], "Winston Smith desafia o Grande Irmão num mundo de vigilância total e verdade reescrita.", 416, ("1984", "George Orwell")),
    "A Revolução dos Bichos": (["Literatura Estrangeira", "Distopia"], "Os animais expulsam os humanos da fazenda — e descobrem que alguns são mais iguais que outros.", 152, ("Animal Farm", "George Orwell")),
    "O Pequeno Príncipe": (["Literatura Estrangeira", "Infantojuvenil", "Clássicos"], "Um piloto caído no deserto encontra um pequeno príncipe que vê o essencial, invisível aos olhos.", 96, ("The Little Prince", "Antoine de Saint-Exupéry")),
    "Cem Anos de Solidão": (["Literatura Estrangeira", "Clássicos", "Romance"], "Sete gerações dos Buendía em Macondo, no auge do realismo mágico.", 448, ("One Hundred Years of Solitude", "Gabriel García Márquez")),
    "O Amor nos Tempos do Cólera": (["Literatura Estrangeira", "Romance"], "Florentino Ariza espera mais de cinquenta anos pelo amor de Fermina Daza.", 432, ("Love in the Time of Cholera", "Gabriel García Márquez")),
    "Crime e Castigo": (["Literatura Estrangeira", "Clássicos"], "Raskólnikov comete um assassinato 'justificado' e afunda na própria consciência.", 592, ("Crime and Punishment", "Fyodor Dostoevsky")),
    "Os Irmãos Karamázov": (["Literatura Estrangeira", "Clássicos"], "Três irmãos, um parricídio e as grandes questões de Deus, culpa e liberdade.", 1000, ("The Brothers Karamazov", "Fyodor Dostoevsky")),
    "Anna Kariênina": (["Literatura Estrangeira", "Clássicos", "Romance"], "O amor proibido de Anna e Vronski contra a hipocrisia da alta sociedade russa.", 864, ("Anna Karenina", "Leo Tolstoy")),
    "Orgulho e Preconceito": (["Literatura Estrangeira", "Clássicos", "Romance"], "Elizabeth Bennet e o orgulhoso Sr. Darcy duelam em espírito no romance mais amado de Austen.", 424, ("Pride and Prejudice", "Jane Austen")),
    "Frankenstein": (["Literatura Estrangeira", "Clássicos", "Terror", "Ficção Científica"], "Victor Frankenstein dá vida a uma criatura — e foge da responsabilidade de tê-la criado.", 336, ("Frankenstein", "Mary Shelley")),
    "Drácula": (["Literatura Estrangeira", "Clássicos", "Terror"], "O conde vampiro deixa os Cárpatos rumo a Londres, em cartas e diários que definiram um gênero.", 512, ("Dracula", "Bram Stoker")),
    "A Metamorfose": (["Literatura Estrangeira", "Clássicos"], "Gregor Samsa acorda transformado em um inseto monstruoso — e a família segue em frente.", 96, ("The Metamorphosis", "Franz Kafka")),
    "O Processo": (["Literatura Estrangeira", "Clássicos"], "Josef K. é preso sem saber por quê, num labirinto burocrático sem saída.", 272, ("The Trial", "Franz Kafka")),
    "O Velho e o Mar": (["Literatura Estrangeira", "Clássicos", "Aventura"], "O velho Santiago trava sua batalha solitária contra um peixe gigante — e contra a derrota.", 128, ("The Old Man and the Sea", "Ernest Hemingway")),
    "Romeu e Julieta": (["Literatura Estrangeira", "Clássicos", "Teatro", "Romance"], "Dois jovens de famílias rivais pagam com a vida o preço do amor em Verona.", 208, ("Romeo and Juliet", "William Shakespeare")),
    "Hamlet": (["Literatura Estrangeira", "Clássicos", "Teatro"], "O príncipe da Dinamarca hesita entre a dúvida e a vingança do pai assassinado.", 320, ("Hamlet", "William Shakespeare")),
    "Dom Quixote": (["Literatura Estrangeira", "Clássicos", "Aventura"], "O fidalgo que enlouqueceu de tanto ler cavalaria sai pelo mundo com Sancho Pança.", 1056, ("Don Quixote", "Miguel de Cervantes")),
    "Os Miseráveis": (["Literatura Estrangeira", "Clássicos"], "Jean Valjean busca redenção na França do século XIX, perseguido pelo implacável Javert.", 1504, ("Les Misérables", "Victor Hugo")),
    "O Nome da Rosa": (["Literatura Estrangeira", "Mistério"], "Mortes misteriosas numa abadia medieval desafiam o franciscano Guilherme de Baskerville.", 576, ("The Name of the Rose", "Umberto Eco")),
    "O Hobbit": (["Literatura Estrangeira", "Fantasia", "Aventura"], "Bilbo Bolseiro deixa o conforto do Condado numa jornada até a Montanha Solitária.", 336, ("The Hobbit", "J.R.R. Tolkien")),
    "O Senhor dos Anéis: A Sociedade do Anel": (["Literatura Estrangeira", "Fantasia", "Aventura"], "Frodo herda o Um Anel e parte com a Sociedade para destruí-lo na Montanha da Perdição.", 576, ("The Fellowship of the Ring", "J.R.R. Tolkien")),
    "Harry Potter e a Pedra Filosofal": (["Literatura Estrangeira", "Fantasia", "Infantojuvenil"], "No seu 11º aniversário, Harry descobre que é um bruxo — e que tem um destino em Hogwarts.", 264, ("Harry Potter and the Philosopher's Stone", "J.K. Rowling")),
    "As Crônicas de Nárnia": (["Literatura Estrangeira", "Fantasia", "Infantojuvenil"], "Quatro irmãos atravessam um guarda-roupa e encontram um reino sob o feitiço do inverno eterno.", 768, ("The Chronicles of Narnia", "C.S. Lewis")),
    "Ensaio sobre a Cegueira": (["Literatura Estrangeira", "Distopia"], "Uma epidemia de cegueira branca revela o melhor e o pior da condição humana.", 312, ("Blindness", "José Saramago")),
    "Os Maias": (["Literatura Estrangeira", "Clássicos", "Romance"], "A decadência de uma família lisboeta e um amor trágico no retrato maior do Portugal oitocentista.", 712, ("Os Maias", "Eça de Queirós")),
    "Assassinato no Expresso do Oriente": (["Literatura Estrangeira", "Mistério"], "Hercule Poirot investiga um assassinato a bordo de um trem preso na neve — todos são suspeitos.", 256, ("Murder on the Orient Express", "Agatha Christie")),
    "Um Estudo em Vermelho": (["Literatura Estrangeira", "Mistério"], "O primeiro caso de Sherlock Holmes e Dr. Watson, das ruas de Londres aos desertos de Utah.", 176, ("A Study in Scarlet", "Arthur Conan Doyle")),
    "A Casa dos Espíritos": (["Literatura Estrangeira", "Romance"], "Quatro gerações da família Trueba entre paixões, espíritos e a história do Chile.", 448, ("The House of the Spirits", "Isabel Allende")),
    "Admirável Mundo Novo": (["Literatura Estrangeira", "Distopia", "Ficção Científica"], "Num futuro de felicidade fabricada e castas biológicas, um 'selvagem' questiona tudo.", 312, ("Brave New World", "Aldous Huxley")),
    "Fahrenheit 451": (["Literatura Estrangeira", "Distopia", "Ficção Científica"], "O bombeiro Montag queima livros — até começar a lê-los.", 216, ("Fahrenheit 451", "Ray Bradbury")),
}

# Novos títulos: (titulo, ano, [autores], categorias, sinopse, paginas, busca)
NOVOS = [
    ("A Menina que Roubava Livros", 2005, ["Markus Zusak"], ["Literatura Estrangeira", "Romance"], "Na Alemanha nazista, Liesel rouba livros e divide palavras — sob o olhar da Morte, a narradora.", 480, ("The Book Thief", "Markus Zusak")),
    ("O Diário de Anne Frank", 1947, ["Anne Frank"], ["Literatura Estrangeira", "Não ficção"], "O diário da adolescente judia escondida em Amsterdã durante a ocupação nazista.", 352, ("The Diary of a Young Girl", "Anne Frank")),
    ("Duna", 1965, ["Frank Herbert"], ["Literatura Estrangeira", "Ficção Científica", "Aventura"], "Paul Atreides e a luta pelo planeta Arrakis, fonte da especiaria mais valiosa do universo.", 680, ("Dune", "Frank Herbert")),
    ("Fundação", 1951, ["Isaac Asimov"], ["Literatura Estrangeira", "Ficção Científica"], "Hari Seldon prevê a queda do Império Galáctico e cria uma fundação para encurtar a barbárie.", 256, ("Foundation", "Isaac Asimov")),
    ("Neuromancer", 1984, ["William Gibson"], ["Literatura Estrangeira", "Ficção Científica"], "O hacker Case ganha uma última chance no ciberespaço, no romance que fundou o cyberpunk.", 320, ("Neuromancer", "William Gibson")),
    ("O Conto da Aia", 1985, ["Margaret Atwood"], ["Literatura Estrangeira", "Distopia"], "Na República de Gilead, Offred vive como aia — e resiste em silêncio.", 368, ("The Handmaid's Tale", "Margaret Atwood")),
    ("O Iluminado", 1977, ["Stephen King"], ["Literatura Estrangeira", "Terror"], "O inverno isola a família Torrance no Hotel Overlook — que tem planos para Danny e seu dom.", 512, ("The Shining", "Stephen King")),
    ("It: A Coisa", 1986, ["Stephen King"], ["Literatura Estrangeira", "Terror"], "Sete amigos enfrentam o mal que assombra Derry, vestido de palhaço, na infância e 27 anos depois.", 1104, ("It", "Stephen King")),
    ("Sapiens: Uma Breve História da Humanidade", 2011, ["Yuval Noah Harari"], ["Não ficção"], "Da savana africana à era digital: como o Homo sapiens conquistou o planeta.", 464, ("Sapiens: A Brief History of Humankind", "Yuval Noah Harari")),
    ("A Guerra dos Tronos", 1996, ["George R.R. Martin"], ["Literatura Estrangeira", "Fantasia"], "As grandes casas de Westeros disputam o Trono de Ferro enquanto o inverno se aproxima.", 600, ("A Game of Thrones", "George R.R. Martin")),
    ("Percy Jackson e o Ladrão de Raios", 2005, ["Rick Riordan"], ["Literatura Estrangeira", "Fantasia", "Infantojuvenil"], "Percy descobre que é filho de Poseidon — e que o raio-mestre de Zeus sumiu.", 400, ("The Lightning Thief", "Rick Riordan")),
    ("A Culpa é das Estrelas", 2012, ["John Green"], ["Literatura Estrangeira", "Romance", "Infantojuvenil"], "Hazel e Augustus se conhecem num grupo de apoio e vivem um amor que desafia o tempo.", 288, ("The Fault in Our Stars", "John Green")),
    ("O Morro dos Ventos Uivantes", 1847, ["Emily Brontë"], ["Literatura Estrangeira", "Clássicos", "Romance"], "A paixão devastadora de Heathcliff e Catherine varre duas gerações nos páramos ingleses.", 416, ("Wuthering Heights", "Emily Brontë")),
    ("Jane Eyre", 1847, ["Charlotte Brontë"], ["Literatura Estrangeira", "Clássicos", "Romance"], "A órfã Jane conquista independência e amor — mas Thornfield guarda um segredo no sótão.", 576, ("Jane Eyre", "Charlotte Brontë")),
    ("O Retrato de Dorian Gray", 1890, ["Oscar Wilde"], ["Literatura Estrangeira", "Clássicos"], "Dorian permanece jovem enquanto seu retrato envelhece e registra cada pecado.", 272, ("The Picture of Dorian Gray", "Oscar Wilde")),
]


def buscar_capa(titulo, autor, busca=None):
    """Busca capa e ISBN no Open Library. Retorna (capa_url, isbn) ou ('', '')."""
    if busca:
        titulo, autor = busca
    params = {"title": titulo, "limit": 3, "fields": "cover_i,isbn"}
    if autor:
        params["author"] = autor
    url = "https://openlibrary.org/search.json?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=15) as resposta:
            dados = json.load(resposta)
    except Exception:
        return "", ""
    for doc in dados.get("docs", []):
        if doc.get("cover_i"):
            isbn = next((i for i in doc.get("isbn", []) if len(i) == 13), "")
            return f"https://covers.openlibrary.org/b/id/{doc['cover_i']}-L.jpg", isbn
    return "", ""


class Command(BaseCommand):
    help = "Enriquece o acervo com categorias, sinopses, capas e novos títulos."

    def add_arguments(self, parser):
        parser.add_argument("--sem-capas", action="store_true", help="Não busca capas na internet.")

    def handle(self, *args, **opcoes):
        ConfiguracaoBiblioteca.carregar()  # garante a configuração padrão

        categorias = {}
        for entrada in list(DADOS.values()) + [n[3:] for n in NOVOS]:
            for nome in entrada[0] if isinstance(entrada[0], list) else []:
                if nome not in categorias:
                    categorias[nome], _ = Categoria.objects.get_or_create(nome=nome)
        self.stdout.write(f"Categorias: {len(categorias)}")

        # Novos títulos
        criados = 0
        for titulo, ano, autores, cats, sinopse, paginas, busca in NOVOS:
            livro, novo = Livro.objects.get_or_create(titulo=titulo, defaults={"ano": ano})
            if novo:
                criados += 1
                livro.autores.set([Autor.objects.get_or_create(nome=n)[0] for n in autores])
            DADOS[titulo] = (cats, sinopse, paginas, busca)
        self.stdout.write(f"Novos livros criados: {criados}")

        # Enriquecimento + capas
        com_capa = sem_capa = 0
        for livro in Livro.objects.all():
            info = DADOS.get(livro.titulo)
            if info:
                cats, sinopse, paginas, busca = info
                livro.categorias.set([categorias[c] for c in cats])
                livro.sinopse = livro.sinopse or sinopse
                livro.paginas = livro.paginas or paginas
            else:
                busca = None
            if livro.exemplares <= 1:
                livro.exemplares = 1 + (livro.pk % 4)  # 1 a 4 exemplares, determinístico
            if not opcoes["sem_capas"] and not livro.capa_url and not livro.capa:
                autor = livro.autores.first()
                capa_url, isbn = buscar_capa(livro.titulo, autor.nome if autor else "", busca)
                if capa_url:
                    livro.capa_url = capa_url
                    livro.isbn = livro.isbn or isbn
                    com_capa += 1
                    self.stdout.write(f"  capa ok: {livro.titulo}")
                else:
                    sem_capa += 1
                    self.stdout.write(self.style.WARNING(f"  sem capa: {livro.titulo}"))
            livro.save()

        self.stdout.write(self.style.SUCCESS(
            f"Concluído: {Livro.objects.count()} livros no acervo, "
            f"{com_capa} capas novas, {sem_capa} sem capa."
        ))
