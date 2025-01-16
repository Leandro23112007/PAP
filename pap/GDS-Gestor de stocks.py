import os 
import csv
import mysql.connector
from datetime import datetime, timedelta
from decimal import Decimal
    
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'leandro',
    'database': 'loja'  
}

# Função para buscar produtos por nome no banco de dados
def buscar_produtos_por_nome(termo_pesquisa):
    conexao = None
    try:
        conexao = mysql.connector.connect(**db_config)
        cursor = conexao.cursor(dictionary=True)
        query = "SELECT * FROM produtos WHERE LOWER(product_name) LIKE %s"
        cursor.execute(query, (f"%{termo_pesquisa.lower()}%",))
        resultados = cursor.fetchall()
        return resultados
    except mysql.connector.Error as erro:
        print(f"Erro ao acessar a base de dados: {erro}")
        return []
    finally:
        if conexao and conexao.is_connected():
            cursor.close()
            conexao.close()

# Função para processar o código de barras e buscar produto no banco de dados
def ler_codigo_barras(codigo):
    preco_compra = float(input("Digite o preço de compra: € "))
    data_venda = datetime.now().date()

    if codigo in inventario:
        # Incrementa a quantidade do produto no estoque, não as vendas
        inventario[codigo]["quantidade"] += 1  # Adiciona 1 à quantidade no estoque
        inventario[codigo]["vendas"] += 1  # Incrementa as vendas (caso seja uma venda)
        inventario[codigo]["data_venda"] = data_venda  # Atualiza a data de venda
        print(f"Venda registrada! Total de vendas para {inventario[codigo]['nome']}: {inventario[codigo]['vendas']}")
    else:
        nome_produto = input("Produto novo! Digite o nome do produto: ")
        produtos_encontrados = buscar_produtos_por_nome(nome_produto)

        if produtos_encontrados:
            print("Produto(s) encontrado(s):")
            for idx, produto in enumerate(produtos_encontrados):
                preco_convertido = processar_preco(produto['product_preco'])
                print(f"{idx + 1}. {produto['product_name']} - Preço: € {preco_convertido:.2f}")

            # Seleciona automaticamente o primeiro produto da lista
            produto_selecionado = produtos_encontrados[0]
            preco_medio = processar_preco(produto_selecionado['product_preco'])
            print(f"Produto '{produto_selecionado['product_name']}' selecionado automaticamente.")
        else:
            preco_medio = float(input("Digite o preço estimado de venda: € "))
            print("Produto não encontrado no banco de dados.")

        # Adiciona o novo produto ao inventário com a chave 'quantidade' inicializada em 1
        inventario[codigo] = {
            "nome": nome_produto,
            "vendas": 0,  # Não adiciona vendas para produtos novos
            "quantidade": 1,  # Inicializa a quantidade com 1 ao adicionar um novo produto
            "preco_venda": preco_medio,
            "preco_compra": preco_compra,
            "data_venda": "N/A",  # Define "N/A" como a data de venda para novos produtos
            "ultima_adicao": datetime.now().isoformat()  # Adiciona o timestamp atual
        }

    salvar_inventario_bd()
    imprimir_fatura(inventario[codigo])

    input("Pressione Enter para continuar.")

def garantir_pasta_faturas():
    pasta_faturas = 'faturas'
    if not os.path.exists(pasta_faturas):
        os.makedirs(pasta_faturas)

# Função para limpar a tela (depende do sistema operacional)
def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

# Função para exibir o menu
def exibir_menu():
    limpar_tela()
    print("\nEscolha uma opção:")
    print("1. Digitar código de barras (Automação de Vendas)")
    print("2. Consultar Inventário de Vendas")
    print("3. Ver Ganhos das Vendas Confirmadas (0 = Ganhos Totais)")
    print("4. Confirmar Venda")
    print("5. Salvar e Sair")

# Dicionário para armazenar o inventário de vendas
inventario = {}

# Carrega o inventário do arquivo TXT, se existir
def carregar_inventario_bd():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM inventario")
        inventario_bd = cursor.fetchall()
        return inventario_bd if inventario_bd else []
    except mysql.connector.Error as erro:
        print(f"Erro ao acessar o banco de dados: {erro}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def salvar_inventario_bd():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        for codigo, dados in inventario.items():
            cursor.execute(""" 
                INSERT INTO inventario (codigo, nome, vendas, preco_venda, preco_compra, data_venda, ultima_adicao)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                nome = VALUES(nome),
                vendas = VALUES(vendas),
                preco_venda = VALUES(preco_venda),
                preco_compra = VALUES(preco_compra),
                data_venda = VALUES(data_venda),
                ultima_adicao = VALUES(ultima_adicao)
            """, (
                codigo,
                dados['nome'],
                dados['vendas'],
                dados['preco_venda'],
                dados['preco_compra'],
                dados['data_venda'],
                dados['ultima_adicao']
            ))
        conn.commit()
        print("Inventário salvo com sucesso no banco de dados!")
    except mysql.connector.Error as erro:
        print(f"Erro ao salvar inventário no banco de dados: {erro}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


    
def processar_preco(preco_str):
    # Remove o símbolo '$' e a vírgula, e converte para float
    preco_str = preco_str.replace('$', '').replace(',', '').strip()

    # Verifica se o preço é um intervalo (ex: "144.99 to 257.99")
    if 'to' in preco_str:
        preco_intervalo = preco_str.split(' to ')
        try:
            preco_minimo = float(preco_intervalo[0])  # Pega o valor mais baixo
            return preco_minimo * 0.94  # Converte para euros
        except ValueError:
            print(f"Erro ao processar o preço do intervalo: {preco_str}")
            return 0.0  # Retorna 0 em caso de erro no valor do intervalo
    else:
        try:
            return float(preco_str) * 0.94  # Converte para euros
        except ValueError:
            print(f"Erro ao processar o preço: {preco_str}")
            return 0.0  # Retorna 0 se o preço não for válido

def exibir_inventario_bd():
    try:
        # Estabelece a conexão com o banco de dados usando o dicionário db_config
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Consulta SQL para buscar todos os produtos no inventário
        query = "SELECT product_name, product_estado, product_preco FROM produtos"
        cursor.execute(query)

        # Exibe os produtos encontrados
        print("\nInventário de Produtos:")
        for produto in cursor.fetchall():
            print(f"Produto: {produto[0]}, Estoque: {produto[1]}, Preço: €{produto[2]:.2f}")
        print("\nPressione qualquer tecla para voltar ao menu...")

        cursor.close()
        conn.close()

        # Aguarda a interação do usuário para retornar ao menu
        input()  # Aguarda a interação do usuário para continuar

    except mysql.connector.Error as erro:
        print(f"Erro ao consultar inventário: {erro}")
    except Exception as e:
        print(f"Ocorreu um erro ao consultar o inventário: {e}")
    finally:
        print("\nFim da função exibir_inventario_bd.")

def garantir_tabela_inventario(conexao):
    try:
        cursor = conexao.cursor()
        cursor.execute("""  
            CREATE TABLE IF NOT EXISTS inventario (
                id INT AUTO_INCREMENT PRIMARY KEY,
                codigo VARCHAR(255) NOT NULL,
                nome VARCHAR(255) NOT NULL,
                vendas INT DEFAULT 0,
                preco_venda DECIMAL(10,2),
                preco_compra DECIMAL(10,2),
                data_venda DATE
            )
        """)
        conexao.commit()
        print("Tabela 'inventario' garantida no banco de dados.")
    except mysql.connector.Error as err:
        print(f"Erro ao garantir tabela: {err}")

def confirmar_venda():
    codigo = input("Digite o código de barras do produto para confirmar a venda: ")
    
    if codigo in inventario:
        preco_venda = float(input(f"Digite o preço de venda para o produto {inventario[codigo]['nome']}: € "))
        inventario[codigo]["preco_venda"] = preco_venda  # Atualiza o preço de venda do produto
        inventario[codigo]["vendas"] += 1  # Incrementa as vendas do produto
        inventario[codigo]["data_venda"] = datetime.now().date()  # Atualiza a data da última venda
        
        # Pergunta sobre a garantia
        garantia = input("Digite o período de garantia (em meses) para o produto: ")
        print(f"Venda confirmada! Garantia de {garantia} anos para o produto {inventario[codigo]['nome']}.")
        
        # Atualiza a fatura do produto
        imprimir_fatura(inventario[codigo])
        
        # Atualiza o inventário com o novo preço de venda
        salvar_inventario_bd()
        input("Pressione Enter para voltar ao menu.")
    else:
        print("Produto não encontrado no inventário.")
        input("Pressione Enter para voltar ao menu.")

def calcular_ganhos_ultimos_dias():
    dias = int(input("Digite o número de dias para calcular os ganhos das vendas confirmadas (0 para ganhos totais): "))
    total_ganhos = 0.0

    if dias == 0:  # Calcula os ganhos totais
        for dados in inventario.values():
            if dados["vendas"] > 0:  # Só considera as vendas confirmadas
                ganho_unitario = dados["preco_venda"] - dados["preco_compra"]
                total_ganhos += ganho_unitario * dados["vendas"]
        print(f"Ganho total das vendas confirmadas: € {total_ganhos:.2f}")
    else:  # Calcula os ganhos dos últimos X dias
        data_limite = datetime.now() - timedelta(days=dias)
        for dados in inventario.values():
            if dados["vendas"] > 0 and dados["data_venda"] >= data_limite.replace(hour=0, minute=0, second=0, microsecond=0):
                ganho_unitario = dados["preco_venda"] - dados["preco_compra"]
                total_ganhos += ganho_unitario * dados["vendas"]
        print(f"Ganho total das vendas confirmadas nos últimos {dias} dias: € {total_ganhos:.2f}")
        input("Pressione Enter para voltar ao menu.")
# Função para imprimir a fatura do produto
def imprimir_fatura(produto):
    # Garante que a pasta de faturas exista
    garantir_pasta_faturas()

    # Verifica se a data de venda é 'N/A' ou uma data válida
    if produto['data_venda'] == 'N/A':
        nome_arquivo = f"faturas/{produto['nome'].replace(' ', '_').replace('-', '_')}_N_A.txt"
    else:
        nome_arquivo = f"faturas/{produto['nome'].replace(' ', '_').replace('-', '_')}_{produto['data_venda']}.txt"

    # Calcula o IVA
    iva_percentual = Decimal(0.23)  # 23%, convertido para Decimal
    valor_iva = produto['preco_venda'] * float(iva_percentual)
    custo_envio = produto.get('custo_envio', Decimal(0.0))  # Usa 0.0 como valor padrão se 'custo_envio' não estiver presente

    total_com_iva = float(produto['preco_venda']) + float(valor_iva) + float(custo_envio)

    # Abre o arquivo para escrever a fatura
    with open(nome_arquivo, "w", encoding="utf-8") as fatura:
        fatura.write(f"Data da Venda: {produto['data_venda']}\n\n")
        fatura.write(f"{produto['nome']}{'.' * (20 - len(produto['nome']))}{produto['preco_venda']:.2f} €\n")
        fatura.write(f"Envio{'.' * 15}{custo_envio:.2f} €\n")
        fatura.write(f"Garantia{'.' * 12}{produto.get('garantia', '1')} mês\n")
        fatura.write(f"IVA{'.' * 17}{int(iva_percentual * 100)} %\n\n")
        fatura.write(f"Total:{'.' * 14}{total_com_iva:.2f} €\n")
        fatura.write(f"{'-' * 28}\n")
        fatura.write(f"{'-' * 28}\n")
        fatura.write("Obrigado pela sua compra!\n")

    print(f"Fatura oficial para o produto '{produto['nome']}' gerada com sucesso!")

# Exemplo de chamada:
produto = {'nome': 'iphone se', 'preco_venda': 499.99, 'data_venda': 'N/A'}
imprimir_fatura(produto)

def executar():
    while True:
        exibir_menu()
        opcao = input("\nEscolha uma opção: ")

        if opcao == '1':
            # Função para digitar código de barras (Automação de Vendas)
            ler_codigo_barras(input("Digite o código de barras: "))  # Chama a função de automação de vendas

        elif opcao == '2':
            exibir_inventario_bd()  # Exibe o inventário a partir do banco

        elif opcao == '3':
            # Função para ver os ganhos das vendas confirmadas
            calcular_ganhos_ultimos_dias()

        elif opcao == '4':
            # Função para confirmar venda
            confirmar_venda()

        elif opcao == '5':
            print("Saindo...")
            break

        else:
            print("Opção inválida! Tente novamente.")
            # O loop continuará sem chamar novamente a função 'executar()'

# Executa o menu
if __name__ == "__main__":
    executar()