# Documentação do Projeto

## Infraestrutura de Deploy/Publicação

Para a publicação da aplicação foi escolhida uma infraestrutura de cloud computing, utilizando a plataforma Render, por meio de um Web Service para execução da aplicação desenvolvida em Python com o framework Django e um banco de dados PostgreSQL.

O código-fonte da aplicação permanece armazenado no GitHub e está integrado ao Render, permitindo que alterações realizadas no repositório possam ser utilizadas no processo de publicação da aplicação.

### Infraestrutura utilizada

A infraestrutura é composta por:

- **GitHub:** armazenamento e versionamento do código-fonte;
- **Render Web Service:** execução da aplicação Django;
- **Render PostgreSQL:** armazenamento dos dados da aplicação;
- **Gunicorn/Uvicorn:** execução da aplicação Django em produção.

### Justificativa da escolha

A escolha de uma infraestrutura em nuvem ocorreu principalmente pela facilidade de configuração, disponibilidade da aplicação pela internet e redução da necessidade de manutenção de uma infraestrutura física própria.

Com a utilização do Render, não foi necessário disponibilizar um computador ou servidor físico para executar continuamente a aplicação, realizar configurações de rede ou manter o equipamento ligado para que o sistema pudesse ser acessado pelos usuários.

Uma infraestrutura self-hosted também poderia ser utilizada, porém exigiria maior responsabilidade com configuração e manutenção do equipamento, disponibilidade, rede, segurança, atualizações e consumo de energia. Para o objetivo acadêmico do projeto, a infraestrutura em nuvem apresentou uma alternativa mais simples para publicação e demonstração da aplicação.

Também foi considerada a utilização de plataformas de hospedagem de conteúdo estático, como o GitHub Pages. Essa alternativa não atende às necessidades do projeto, pois a aplicação utiliza Django e necessita de processamento no servidor e conexão com um banco de dados PostgreSQL.

### Arquitetura

A infraestrutura representada da seguinte forma:

GitHub
↓
Render Web Service
↓
Aplicação Django
↓
Render PostgreSQL
↓
Dados da aplicação

### Aplicação publicada

A aplicação está disponível publicamente através do Render:

**https://praticasextensionistas3biblioteca.onrender.com/**

### Limitações

A aplicação encontra-se hospedada na plataforma Render. Por utilizar a infraestrutura gratuita, o serviço pode entrar em estado de inatividade após períodos sem acesso. Nesse caso, o primeiro acesso pode apresentar um tempo maior de carregamento enquanto a aplicação é reativada.
