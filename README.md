# StockFlow

Sistema web para controle e gestão de estoque, desenvolvido com Python e Flask.

## Sobre o projeto

O StockFlow surgiu a partir de um problema real de controle de materiais em estoque, onde produtos eram armazenados sem um acompanhamento adequado das entradas e saídas.

O sistema foi desenvolvido para centralizar o controle de produtos, movimentações, inventário, usuários, auditoria e relatórios, permitindo maior organização e rastreabilidade das operações.

## Funcionalidades principais

- Dashboard com visão geral do estoque
- Cadastro, edição, ativação e desativação de produtos
- Controle de estoque mínimo e produtos sem estoque
- Categorias de produtos
- Movimentações de entrada, saída e ajuste
- Histórico de movimentações por produto
- Estorno de movimentações
- Inventário físico
- Controle de usuários e níveis de acesso
- Auditoria das operações
- Relatórios com filtros por produto, tipo e período
- Exportação de relatórios em PDF

## Tecnologias utilizadas

### Back-end
- Python
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-Login
- Flask-WTF
- WTForms

### Banco de dados
- SQLite no ambiente de desenvolvimento
- PostgreSQL em produção

### Front-end
- HTML
- CSS
- Bootstrap 5
- Bootstrap Icons
- Jinja2

### Testes
- pytest

### Produção
- Gunicorn
- Railway
- GitHub

## Segurança

O StockFlow possui medidas de segurança para proteger o acesso e as operações do sistema:

- autenticação de usuários com Flask-Login;
- senhas armazenadas com hash;
- controle de acesso por nível de usuário;
- proteção CSRF nos formulários;
- cookies seguros em produção;
- `SECRET_KEY` armazenada em variável de ambiente;
- credenciais do banco de dados fora do código-fonte;
- arquivo `.env` ignorado pelo Git;
- tratamento de erros e registro de logs;
- auditoria das principais operações.

## Testes automatizados

O projeto possui testes automatizados para as principais regras de negócio.

Atualmente:

- 15 testes automatizados;
- 15 testes passando.

Entre os cenários testados estão:

- login válido e inválido;
- entrada de estoque;
- saída de estoque;
- bloqueio de saída maior que o estoque disponível;
- ajuste de estoque;
- estorno de movimentações;
- bloqueio de estorno duplicado;
- permissões de usuários;
- criação e edição de produtos.

## Estrutura do projeto

```text
stockflow/
│
├── app/
│   ├── forms/
│   ├── models/
│   ├── routes/
│   ├── static/
│   ├── templates/
│   ├── utils/
│   ├── commands.py
│   ├── extensions.py
│   └── __init__.py
│
├── migrations/
├── tests/
├── config.py
├── run.py
├── requirements.txt
└── README.md

## Ambiente de produção

O StockFlow está publicado em produção utilizando Railway, Gunicorn e PostgreSQL.

A aplicação pode ser acessada em:

https://stockflow-production-75ac.up.railway.app

No ambiente de produção:

- o Flask é executado pelo Gunicorn;
- o banco de dados utilizado é PostgreSQL;
- as migrations são executadas antes da inicialização da aplicação;
- configurações sensíveis são armazenadas em variáveis de ambiente.

## Status do projeto

Projeto funcional, testado e publicado em produção.

Principais etapas concluídas:

- autenticação e controle de acesso;
- gestão de produtos e categorias;
- movimentações de estoque;
- inventário físico;
- auditoria;
- relatórios em PDF;
- testes automatizados;
- PostgreSQL em produção;
- deploy com Railway.

## Autor

Desenvolvido por Ryan Kael.

Projeto desenvolvido para estudo, aplicação prática de desenvolvimento web e composição de portfólio profissional.