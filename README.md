# Projeto de Controle de Vendas com Preços Automatizados

Este projeto realiza o controle de inventário e vendas de produtos, com a funcionalidade adicional de automatizar a consulta de preços de smartphones no eBay, utilizando dados extraídos via ParseHub. Ele é desenvolvido em Python e inclui gerenciamento de inventário, cálculo de ganhos, geração de faturas e leitura de código de barras para automatizar as vendas.

## Estrutura do Projeto

`controle_vendas.py`**: Script principal para controle de vendas e inventário.
`run_results.csv`**: Arquivo CSV gerado pelo ParseHub com os preços dos smartphones do eBay.
`parsehub_project`**: Contém o projeto ParseHub responsável pelo web scraping dos preços de smartphones.
`faturas/`**: Pasta onde são armazenadas as faturas geradas automaticamente após cada venda.
`inventario_vendas.txt`**: Arquivo onde o inventário é salvo entre sessões.
`venv/`**: Ambiente virtual com as dependências do projeto, incluindo scripts, bibliotecas e binários.

## Funcionalidades

1. **Controle de Vendas**: Registra vendas, consulta inventário, calcula ganhos e confirmações de vendas.
2. **Automação de Preços**: 
   - Realiza scraping de preços de smartphones no eBay para atualizar o preço médio de venda automaticamente.
   - Gera uma média de preços quando múltiplos resultados são encontrados, ou permite a inserção manual para produtos não listados.
3. **Geração de Faturas**: Após cada venda, uma fatura é gerada e salva na pasta `faturas/`.
4. **Consulta de Inventário**: Permite visualizar o inventário atualizado com quantidade de vendas e preços de cada item.

## Instalação e Configuração

1. **Clone o repositório**:
   ```bash
   git clone <url_do_repositorio>
   cd <nome_da_pasta>
