# Escolha, descrição e justificativa da infraestrutura de deploy

Sistema de Gestão de Biblioteca — Práticas Extensionistas IV

---

## 1. Infraestrutura escolhida

A solução é publicada em **nuvem, no modelo PaaS (Platform as a Service)**, com a seguinte composição:

| Elemento | Serviço escolhido | Papel na solução |
|---|---|---|
| Hospedagem da aplicação | **Render — Web Service** | Executa o container Linux com Gunicorn servindo a aplicação Django |
| Banco de dados | **Render PostgreSQL** (DBaaS) | Armazena o acervo, usuários, empréstimos, avaliações e a personalização |
| Código-fonte e versionamento | **GitHub** | Repositório remoto, revisão de código e gatilho do deploy |
| Integração contínua | **GitHub Actions** | Executa verificação e os 16 testes automatizados a cada push |
| Arquivos estáticos | **WhiteNoise** (dentro da aplicação) | Serve CSS e imagens comprimidos, sem servidor web adicional |
| Certificado HTTPS | **TLS gerenciado pelo Render** | Emissão e renovação automáticas, sem intervenção da equipe |

O fluxo completo é: `git push` na branch `main` → GitHub Actions valida → Render recebe o webhook →
`build.sh` instala dependências, coleta estáticos e aplica migrações → Gunicorn é reiniciado → aplicação no ar em HTTPS.

---

## 2. Alternativas avaliadas

Antes da decisão, o grupo comparou quatro caminhos possíveis para publicar a solução.

### 2.1 Self-host (servidor próprio / on-premise)

Instalar a aplicação em um servidor físico da própria instituição ou em um computador dedicado.

- **A favor:** controle total do hardware e dos dados; custo marginal zero se a máquina já existe.
- **Contra:** exige administrar sistema operacional, firewall, atualizações de segurança, backup,
  IP fixo, certificado TLS e energia/refrigeração. Não há garantia de disponibilidade fora do horário
  de expediente e a responsabilidade pela recuperação em caso de falha é inteiramente da equipe.
- **Por que foi descartado:** o grupo é formado por estudantes, sem turno de plantão nem acesso a um
  datacenter institucional. O esforço de operação superaria o esforço de desenvolvimento do produto.

### 2.2 IaaS — máquina virtual em nuvem (AWS EC2, Azure VM, Google Compute Engine)

Alugar uma VM e instalar manualmente Python, PostgreSQL, Nginx, Gunicorn e Certbot.

- **A favor:** flexibilidade máxima; possibilidade de ajuste fino de desempenho e custo em escala.
- **Contra:** a equipe continua responsável por todo o software do servidor — a nuvem entrega apenas
  a máquina. Configuração inicial estimada em várias horas, com risco alto de erro de segurança
  (porta aberta, banco exposto, certificado expirado). Os créditos gratuitos são temporários e a
  cobrança por hora de VM continua mesmo com o sistema ocioso.
- **Por que foi descartado:** transfere para a equipe justamente o trabalho que não agrega valor ao
  objetivo da disciplina, que é entregar o sistema funcionando para a biblioteca.

### 2.3 Serverless (AWS Lambda, Google Cloud Run, Vercel Functions)

Executar a aplicação em funções sob demanda, sem servidor permanente.

- **A favor:** paga-se apenas pelo tempo de execução; escala automaticamente até zero.
- **Contra:** o Django é uma aplicação com estado de sessão, arquivos de mídia e conexões
  persistentes ao banco — adaptá-lo ao modelo serverless exigiria empacotamento em container,
  camada de conexão gerenciada (pooling) e armazenamento externo obrigatório para mídia.
  A latência de inicialização a frio também prejudica a navegação do leitor no acervo.
- **Por que foi descartado:** a complexidade adicional não se justifica para o porte do sistema.

### 2.4 PaaS — plataforma gerenciada (Render, Railway, Heroku, PythonAnywhere, Fly.io)

A plataforma recebe o código do repositório, monta o ambiente e executa a aplicação.

- **A favor:** o time cuida do código e a plataforma cuida do restante — sistema operacional,
  HTTPS, reinício em caso de falha, logs, métricas e banco gerenciado com backup.
- **Contra:** menos controle sobre o ambiente e dependência do fornecedor.
- **Por que foi escolhido:** é o melhor equilíbrio entre esforço, custo e confiabilidade para o
  perfil do projeto.

---

## 3. Comparativo resumido

| Critério | Self-host | IaaS (VM) | Serverless | **PaaS (escolhido)** |
|---|---|---|---|---|
| Esforço de configuração inicial | Alto | Alto | Médio/Alto | **Baixo** |
| Manutenção de SO e segurança | Da equipe | Da equipe | Do provedor | **Do provedor** |
| HTTPS/TLS | Manual | Manual | Automático | **Automático** |
| Deploy contínuo a partir do Git | Manual | Manual/script | Nativo | **Nativo** |
| Banco gerenciado com backup | Não | Opcional (pago) | Externo | **Sim** |
| Custo para o projeto acadêmico | Energia + hardware | Cobrança por hora | Por execução | **Plano gratuito** |
| Adequação ao Django | Total | Total | Baixa | **Total** |

---

## 4. Por que Render entre as opções de PaaS

1. **Suporte nativo a Python e Django** — reconhece `requirements.txt`, aceita script de build
   próprio (`build.sh`) e executa Gunicorn como processo web, exatamente o que a aplicação usa.
2. **Banco PostgreSQL gerenciado na mesma plataforma** — comunicação pela rede interna do provedor,
   sem expor o banco à internet, e backup automático incluído.
3. **Deploy contínuo a partir do GitHub sem configuração extra** — o serviço observa a branch `main`
   e reconstrói a aplicação a cada push aprovado.
4. **Plano gratuito adequado à fase de validação** — permite demonstrar o sistema à biblioteca
   parceira sem custo, com caminho de migração para plano pago sem alterar o código.
5. **HTTPS automático com domínio próprio da plataforma** — importante porque o sistema trata dados
   de leitores (nome, e-mail, CPF) e autenticação por senha.
6. **Independência de fornecedor preservada** — a aplicação usa `dj-database-url` e variáveis de
   ambiente, portanto migrar para outra plataforma exige apenas apontar a variável `DATABASE_URL`.

---

## 5. Usuário e estrutura ativados na plataforma

Conforme exigido pelo enunciado, a conta e os recursos de nuvem já estão ativos e configurados:

| Item | Situação |
|---|---|
| Conta no provedor (Render) | Criada e vinculada ao GitHub do grupo |
| Web Service | Criado, apontando para a branch `main` do repositório |
| Comando de build | `./build.sh` (instala dependências, coleta estáticos e aplica migrações) |
| Comando de start | `gunicorn biblioteca.wsgi:application` |
| Banco PostgreSQL | Provisionado e vinculado ao Web Service |
| Deploy automático | Habilitado para a branch `main` |

### Variáveis de ambiente configuradas

| Variável | Finalidade |
|---|---|
| `SECRET_KEY` | Chave criptográfica da aplicação, fora do código-fonte |
| `DEBUG` | Mantida como `False` em produção |
| `DATABASE_URL` | String de conexão do PostgreSQL, injetada pela plataforma |
| `RENDER_EXTERNAL_HOSTNAME` | Domínio público liberado em `ALLOWED_HOSTS` |

As três primeiras são lidas em `codigo/biblioteca/settings.py`; nenhum segredo fica versionado no
repositório.

---

## 6. Limitações conhecidas e plano de evolução

O grupo registra, de forma transparente, o que o plano gratuito **não** entrega e como isso será
tratado quando o sistema for adotado de fato por uma biblioteca:

| Limitação no plano gratuito | Impacto | Encaminhamento |
|---|---|---|
| O serviço hiberna após período sem acesso | Primeira requisição após ociosidade demora alguns segundos | Migração para o plano pago mantém o serviço sempre ativo |
| Sistema de arquivos efêmero (sem disco persistente) | Capas e logo enviados por upload se perdem a cada novo deploy | As capas do acervo de demonstração usam URL da Open Library; na adoção real, contratar disco persistente ou usar armazenamento de objetos |
| Banco gratuito com validade limitada | Necessidade de recriar a base periodicamente | Plano pago do PostgreSQL, com backup e retenção contínuos |
| Região do servidor fora do Brasil | Latência um pouco maior para o usuário final | Selecionar região mais próxima no plano pago |

Nenhuma dessas limitações exige mudança no código da aplicação — todas são resolvidas por
configuração ou contratação de plano, o que confirma o acerto da escolha arquitetural.

---

## 7. Conclusão

A combinação **GitHub (código e CI) + Render (aplicação e banco gerenciados)** foi escolhida porque
entrega automaticamente aquilo que, nas demais opções, seria trabalho manual e recorrente da equipe:
provisionamento, HTTPS, deploy contínuo, reinício em falha, monitoramento e backup. Isso permitiu
que o esforço do grupo permanecesse concentrado no produto entregue à biblioteca parceira, mantendo
ainda assim uma arquitetura profissional, segura e com caminho claro de crescimento.
