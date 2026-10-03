# Demonstração do StockFlow

Este roteiro apresenta uma sequência simples para demonstrar as principais funcionalidades do sistema.

## 1. Login

- acessar a aplicação;
- realizar login com um usuário válido;
- mostrar que o sistema possui autenticação;
- explicar rapidamente os níveis de acesso: ADMIN, MANAGER e USER.

## 2. Dashboard

- apresentar os indicadores principais do estoque;
- mostrar a quantidade de produtos ativos;
- destacar produtos com estoque baixo e sem estoque;
- mostrar o resumo de entradas e saídas do dia;
- apresentar as últimas movimentações registradas.

## 3. Produtos

- abrir a listagem de produtos;
- mostrar os indicadores de estoque;
- apresentar a busca e os filtros por situação e categoria;
- mostrar as informações de código, categoria, quantidade, estoque mínimo, localização e status;
- explicar as ações de entrada, saída e edição do produto;
- destacar que produtos com histórico de movimentação não podem ser excluídos diretamente.

## 4. Movimentações

- abrir o histórico de movimentações;
- mostrar os tipos Entrada, Saída e Ajuste;
- destacar a quantidade anterior e a quantidade atual;
- mostrar o motivo da movimentação;
- identificar o usuário responsável;
- apresentar a opção de estorno;
- explicar que o sistema impede estornos duplicados.

## 5. Inventário físico

- abrir a tela de inventário;
- comparar a quantidade registrada no sistema com a quantidade física;
- registrar uma divergência de estoque;
- mostrar que o sistema gera um ajuste controlado;
- destacar que o usuário responsável fica registrado;
- explicar que a operação também aparece na auditoria.

## 6. Auditoria

- abrir a tela de auditoria;
- mostrar os filtros por ação, entidade, usuário e período;
- destacar que o sistema registra quem realizou cada operação;
- mostrar data, ação, entidade, ID e descrição;
- explicar que alterações importantes permanecem registradas para rastreabilidade;
- apresentar exemplos de criação, atualização, estorno e inventário.

## 7. Relatórios

- abrir a tela de relatórios;
- mostrar os indicadores de movimentações, entradas, saídas e ajustes;
- apresentar os filtros por produto, tipo e período;
- mostrar a listagem dos registros encontrados;
- gerar um relatório em PDF;
- explicar que os filtros respeitam o período selecionado no horário local.

## 8. Encerramento

Ao final da demonstração, destacar que o StockFlow reúne em um único sistema:

- controle de produtos e categorias;
- movimentações de estoque;
- inventário físico;
- controle de usuários e permissões;
- auditoria;
- relatórios em PDF;
- testes automatizados;
- PostgreSQL em produção;
- deploy com Railway;
- integração contínua com GitHub Actions.