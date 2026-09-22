# Sistema de Gestão de Biblioteca

Sistema web completo para bibliotecas de qualquer porte, com acervo digital, área do leitor e identidade visual totalmente personalizável.

Projeto desenvolvido nas disciplinas de **Práticas Extensionistas III e IV**. A Prática III entregou a modelagem e o MVP funcional; a Prática IV dá continuidade ao mesmo produto, tratando da arquitetura da aplicação, da arquitetura de implantação, da esteira DevOps e da infraestrutura de publicação.

## Integrantes

- Gabriel do Amaral Martini - 412830
- Jaime Luiz Hansen Filho - 294833
- João Vitor Chüler Battistella - 447607
- Jorge Luiz Lopes Polli - 369818
- Manueli Vitória de Oliveira Cerutti - 412287
- Pablo Pellizzari Bisollo - 425790
- Phaola Cristina Panegalli - 402224

## 🌐 Aplicação online

Acesse a aplicação publicada:

**(https://praticasextensionistas3biblioteca.onrender.com/)**

## Sobre o projeto

**Introdução:**
As novas tecnologias mudaram a forma como as pessoas acessam informação, fazendo com que bibliotecas se adaptem a um público mais digital e exigente, que busca praticidade e personalização. Nesse contexto, as bibliotecas passam a usar tecnologia e novas formas de comunicação para atrair e engajar usuários, deixando de ser apenas espaços físicos e se tornando ambientes mais interativos e acessíveis.

**Objetivo:**
O estudo tem como objetivo analisar como uma biblioteca utiliza estratégias para atrair e manter seus usuários.

**Metodologia:**
Trata-se de uma pesquisa exploratória, com abordagem qualitativa, realizada por meio de observação, entrevistas e análise de documentos da biblioteca.

**Resultados:**
Observou-se que a biblioteca busca se comunicar melhor com seus usuários, oferecendo conteúdos e serviços alinhados aos seus interesses. No entanto, há dificuldades em atender diferentes perfis de público e em entender completamente a experiência do usuário ao longo do uso dos serviços.

**Conclusão:**
Conclui-se que as estratégias adotadas ajudam na aproximação com o público, mas é importante melhorar o entendimento da jornada do usuário para oferecer serviços mais eficientes e adequados.

**Palavras-chave:**
Biblioteca. Usuários. Tecnologia. Comunicação. Experiência.

## O sistema

O sistema foi pensado como um produto pronto para ser adotado por qualquer biblioteca: escola, universidade, empresa ou biblioteca municipal. A instituição personaliza nome, logo e cores, importa o próprio acervo e passa a oferecer aos leitores um catálogo digital com capas, busca, fila de leitura e avaliações.

O acervo de demonstração conta com **500 livros reais**, todos com capa, autor, ano, categoria e número de páginas.

Existem dois perfis de acesso:

- **Leitor**: cria a própria conta, navega pelo acervo, monta a fila de leitura, marca livros como lidos, favorita e escreve avaliações.
- **Equipe da biblioteca** (staff): além de tudo isso, gerencia livros, autores e categorias, lê as mensagens de contato e controla a personalização visual do sistema.

### Funcionalidades

| Funcionalidade | Rota | Acesso |
|---|---|---|
| Login | `/login/` | Público |
| Criação de conta de leitor | `/registro/` | Público |
| Página inicial com estatísticas e destaques | `/` | Autenticado |
| Acervo com capas, busca e filtros | `/acervo/` | Autenticado |
| Detalhe do livro com disponibilidade e avaliações | `/livro/<id>/` | Autenticado |
| Minha Central (fila, leituras, favoritos, avaliações) | `/minha-central/` | Autenticado |
| Formulário de contato com a equipe | `/contato/` | Público |
| CRUD de livros (com capa, sinopse, ISBN, exemplares) | `/livros/` | Equipe |
| CRUD de autores | `/autores/` | Equipe |
| CRUD de categorias | `/categorias/` | Equipe |
| Mensagens recebidas | `/mensagens/` | Equipe |
| Personalização visual (nome, logo, cores, textos) | `/personalizacao/` | Equipe |
| Painel administrativo do Django | `/admin/` | Equipe |

## Capturas de tela

### Acesso

Tela de login e criação de conta de leitor. Qualquer pessoa pode se cadastrar para usar o catálogo.

![Tela de login](capturas/login.png)

![Criação de conta de leitor](capturas/registro.png)

### Página inicial

Resumo do acervo, próximos livros da fila do leitor, títulos adicionados recentemente e os mais lidos pela comunidade.

![Página inicial](capturas/home.png)

### Acervo

Catálogo em grade com capas, busca por título, autor ou ISBN, filtro por categoria e ordenação por título, ano, data de cadastro ou avaliação. O selo sobre a capa indica a situação do livro na estante do leitor.

![Acervo](capturas/acervo.png)

Resultado com filtros aplicados, ordenado pelos melhor avaliados:

![Acervo com filtros](capturas/acervo_filtros.png)

### Detalhe do livro

Capa, sinopse, categorias, disponibilidade de exemplares, ações de estante (fila, lendo, lido, favorito) e avaliações dos leitores com nota e resenha.

![Detalhe do livro](capturas/livro_detalhe.png)

### Minha Central

Área pessoal do leitor: o que está lendo, fila de leitura, livros já lidos, favoritos e o histórico de avaliações, com estatísticas no topo.

![Minha Central](capturas/minha_central.png)

### Gestão do acervo

Telas restritas à equipe da biblioteca: listagem de livros com miniaturas, formulário completo de cadastro (capa por arquivo ou URL), autores e categorias.

![Gestão de livros](capturas/livros.png)

![Formulário de livro](capturas/livro_form.png)

![Gestão de autores](capturas/autores.png)

![Gestão de categorias](capturas/categorias.png)

### Contato e mensagens

O leitor envia mensagens pelo formulário de contato e a equipe as consulta no sistema.

![Formulário de contato](capturas/contato.png)

![Mensagens recebidas](capturas/mensagens.png)

## Personalização (white-label)

Toda a identidade visual do sistema é configurável pela própria equipe da biblioteca, sem tocar em código: nome, subtítulo, logo, cor primária, cor de destaque, cor de fundo, mensagem de boas-vindas e rodapé. Os tons mais claros e mais escuros são derivados automaticamente da cor primária, garantindo um tema sempre consistente.

![Tela de personalização](capturas/personalizacao.png)

O mesmo sistema, depois de alterar apenas nome e cores na tela de personalização:

![Tema alternativo](capturas/tema_alternativo.png)

## Populando o acervo

O repositório já traz o banco populado com 500 livros. Além do cadastro manual, dois comandos automatizam a carga do acervo:

```bash
# Enriquece o acervo base: categorias, sinopses, capas e novos títulos selecionados
python manage.py seed_acervo

# Importa livros reais da API do Open Library, por assunto, priorizando
# edições em português, até o acervo atingir o tamanho desejado
python manage.py importar_livros --alvo 500
```

O importador busca capa, autores, ano, número de páginas e ISBN de cada obra, descarta registros incompletos ou com títulos em alfabetos não latinos e pode ser executado novamente sem duplicar livros.

## Tecnologias utilizadas

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.12 |
| Framework web | Django 5.x |
| Banco de dados | SQLite (desenvolvimento) e PostgreSQL (produção) |
| Servidor de aplicação | Gunicorn (WSGI) |
| Arquivos estáticos | WhiteNoise |
| Configuração de banco | dj-database-url (leitura de `DATABASE_URL`) |
| Imagens | Pillow (upload de logo e capas) |
| Front-end | HTML e CSS renderizados pelo servidor, sem dependências de JavaScript |
| Dados do acervo | API pública do Open Library (capas e metadados) |
| Testes | Django TestCase (16 testes automatizados) |
| Integração contínua | GitHub Actions |
| Publicação | Nuvem PaaS (Render) com PostgreSQL gerenciado |

## Como executar

Requisitos: Python 3.10 ou superior.

```bash
cd codigo
python3 -m venv .venv
source .venv/bin/activate      # no Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
```

Acesse http://127.0.0.1:8000/ e entre com um dos usuários de demonstração:

| Perfil | Usuário | Senha |
|---|---|---|
| Equipe (staff) | `admin` | `admin123` |
| Leitora | `beatriz` | `leitora123` |

O banco SQLite já vem com o acervo completo, categorias, empréstimos e avaliações de exemplo. Para recriar tudo do zero:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_acervo
python manage.py importar_livros --alvo 500
```

Para rodar os testes automatizados:

```bash
python manage.py test
```

## Arquitetura

Os diagramas de arquitetura estão publicados no repositório em formato PNG e SVG (vetorial, para ampliação sem perda).

### Diagrama UML de pacotes — arquitetura da aplicação

Organização interna do sistema em camadas seguindo o padrão MTV do Django, com as dependências entre os pacotes do projeto, o framework, as bibliotecas de terceiros e os serviços externos.

![Diagrama de pacotes](6.%20DiagramaPacotes/DiagramaPacotes.png)

### Diagrama de arquitetura de implantação

Distribuição física da solução: dispositivo do usuário, plataforma de nuvem com o container da aplicação, banco gerenciado, armazenamento de mídia e os serviços externos, com os protocolos de comunicação de cada caminho.

![Diagrama de implantação](7.%20DiagramaImplantacao/DiagramaImplantacao.png)

### Diagrama de arquitetura DevOps

Esteira completa de integração e entrega contínuas, do planejamento ao monitoramento em produção, com o ciclo de realimentação.

![Diagrama DevOps](8.%20DiagramaDevOps/DiagramaDevOps.png)

## Infraestrutura de publicação

A solução é publicada em nuvem no modelo **PaaS**: aplicação em Web Service com Gunicorn, banco **PostgreSQL gerenciado**, arquivos estáticos servidos pelo WhiteNoise e HTTPS emitido e renovado pela plataforma. O código vive no GitHub, que dispara o deploy automático a cada push aprovado na branch `main`.

A descrição completa, o comparativo com as alternativas avaliadas (self-host, IaaS, serverless e outras PaaS), a configuração ativada na plataforma e as limitações conhecidas estão em:

**[9. Infraestrutura/JustificativaInfraestrutura.md](9.%20Infraestrutura/JustificativaInfraestrutura.md)**

O script de build executado pela plataforma é o [build.sh](build.sh):

```bash
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
```

Em produção, nenhuma credencial fica no repositório — `SECRET_KEY`, `DEBUG` e `DATABASE_URL` são lidas de variáveis de ambiente em `codigo/biblioteca/settings.py`.

## Integração contínua

O repositório tem uma esteira de CI no GitHub Actions ([.github/workflows/ci.yml](.github/workflows/ci.yml)) que roda a cada push e a cada pull request na branch `main`:

1. Instala as dependências com Python 3.12
2. Executa `python manage.py check`
3. Confere se há migrações pendentes não versionadas
4. Executa os 16 testes automatizados

Um teste reprovado interrompe a esteira antes da publicação.

## Modelagem

O modelo relacional do banco de dados e os demais diagramas estruturais do projeto estão nas pastas numeradas do repositório:

| Artefato | Localização |
|---|---|
| Script SQL do banco | [0. Banco/banco.sql](0.%20Banco/banco.sql) |
| Modelo relacional | [1. Modelagem/Modelo.jpeg](1.%20Modelagem/Modelo.jpeg) |
| Diagrama de classes | [2. DiagramaClasses/DiagramaClasses.png](2.%20DiagramaClasses/DiagramaClasses.png) |
| Diagrama de casos de uso | [3. DiagramaCasoUsoGeral/DiagramaUsoGeral.png](3.%20DiagramaCasoUsoGeral/DiagramaUsoGeral.png) |
| Diagrama de sequência | [4. DiagramaSequencia/Diagrama_de_sequencia.png](4.%20DiagramaSequencia/Diagrama_de_sequencia.png) |
| Diagrama de atividades | [5. DiaramasAtividades/diagramaDeAtividade.png](5.%20DiaramasAtividades/diagramaDeAtividade.png) |
| Diagrama de pacotes | [6. DiagramaPacotes/DiagramaPacotes.png](6.%20DiagramaPacotes/DiagramaPacotes.png) |
| Diagrama de implantação | [7. DiagramaImplantacao/DiagramaImplantacao.png](7.%20DiagramaImplantacao/DiagramaImplantacao.png) |
| Diagrama DevOps | [8. DiagramaDevOps/DiagramaDevOps.png](8.%20DiagramaDevOps/DiagramaDevOps.png) |
| Justificativa da infraestrutura | [9. Infraestrutura/JustificativaInfraestrutura.md](9.%20Infraestrutura/JustificativaInfraestrutura.md) |

As entidades do banco estão implementadas como modelos do Django em [codigo/core/models.py](codigo/core/models.py). Além das entidades originais (Usuario, Livro, Autor, Emprestimo), o sistema conta com Categoria, InteracaoLivro (estante e avaliações dos leitores) e ConfiguracaoBiblioteca (personalização visual).

## Estrutura do código

O código fonte está na pasta [codigo/](codigo/):

- `codigo/biblioteca/`: configuração do projeto Django
- `codigo/core/models.py`: modelos do domínio
- `codigo/core/views.py`: views e formulários
- `codigo/core/templates/core/`: templates das telas
- `codigo/core/management/commands/`: comandos de carga do acervo (`seed_acervo` e `importar_livros`)
- `codigo/core/tests.py`: testes automatizados de navegação, permissões, estante do leitor, avaliações e personalização
- `codigo/db.sqlite3`: banco de dados já populado
- `.github/workflows/ci.yml`: esteira de integração contínua
- `build.sh`: script de build executado na publicação
