# GDS - Gestor de Stocks

**GDS - Gestor de Stocks** é um sistema simples desenvolvido em Python, com o objetivo de gerir o inventário de uma loja, permitindo registar, adicionar e consultar produtos. O script permite também fazer o acompanhamento do estado dos produtos em estoque, o que facilita o controle das operações da loja. Este sistema foi desenvolvido como parte da Prova de Aptidão Profissional (PAP).

## Funcionalidades

- **Registo de produtos**: Permite adicionar novos produtos ao inventário.
- **Consulta de produtos**: Permite pesquisar por produtos existentes no sistema.
- **Gestão de estados de produtos**: Permite alterar o estado dos produtos (por exemplo, se está disponível ou esgotado).
- **Relatórios e faturas**: O sistema pode gerar relatórios sobre o estado do inventário e faturas de vendas (apenas após confirmação de venda).

## Tecnologias Utilizadas

- **Python**: Linguagem de programação principal utilizada para o desenvolvimento do sistema.
- **MySQL**: Base de dados utilizada para armazenar as informações sobre os produtos.
- **Bibliotecas Python**:
  - `mysql.connector`: Para conectar ao banco de dados MySQL.
  - `os`: Para manipulação de arquivos e sistema.
  - `csv`: Para leitura e escrita de arquivos CSV.
  - `datetime` e `timedelta`: Para manipulação de datas e horas.
  - `decimal`: Para lidar com valores monetários.

## Como Configurar o Projeto

1. **Abrir o arquivo `setup.bat`**:
   - Abrir `setup.bat` (executar como admnistrador) para iniciar o processo de instalação.

2. **Aguardar o fim das instalações**:
   - O `setup.bat` irá instalar automaticamente todas as dependências necessárias para o funcionamento do GDS.

3. **GDS pronto para usar**:
   - Após o processo de instalação, o sistema estará pronto para ser utilizado.

## Como Usar

- **Adicionar um Novo Produto**: Escolha a opção para adicionar novos produtos ao inventário.
- **Consultar Produtos**: Pesquise por nome, preço ou estado do produto.
- **Alterar Estado do Produto**: Modifique o estado dos produtos, como "disponível" ou "esgotado".
- **Gerar Relatórios e Faturas**: Após a confirmação de venda, o sistema gera relatórios e faturas automaticamente.

Agora o GDS está pronto para ser utilizado de forma eficiente no gerenciamento de inventário da sua loja!
