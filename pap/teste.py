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

def codigo_existe_bd(codigo):
    """ Verifica se o código de barras já existe na base de dados """
    try:
        conexao = mysql.connector.connect(**db_config)
        cursor = conexao.cursor()
        query = "SELECT COUNT(*) FROM inventario WHERE codigo = %s"
        cursor.execute(query, (codigo,))
        resultado = cursor.fetchone()[0]
        return resultado > 0  # Retorna True se o código já existir
    except mysql.connector.Error as erro:
        print(f"Erro ao verificar o código no banco de dados: {erro}")
        return False
    finally:
        if conexao.is_connected():
            cursor.close()
            conexao.close()

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
    preco_compra_novo = Decimal(input("Digite o preço de compra: € "))  # Converte o preço para Decimal
    data_venda = datetime.now().date()

    if codigo in inventario:
        # Pega o preço de compra atual do produto e converte para Decimal
        preco_compra_atual = Decimal(inventario[codigo]["preco_compra"])
        
        # Calcula a média dos preços de compra
        preco_compra_medio = (preco_compra_atual + preco_compra_novo) / 2
        
        # Atualiza o preço de compra no inventário
        inventario[codigo]["preco_compra"] = preco_compra_medio
        
        # Pergunta quantas unidades adicionar
        unidades = int(input(f"Quantas unidades deseja adicionar? "))
        if unidades > 0:
            inventario[codigo]["quantidade"] += unidades
            print(f"Unidade(s) adicionada(s)! Total de unidades para {inventario[codigo]['nome']}: {inventario[codigo]['quantidade']}")
        else:
            print("Por favor, insira um número válido de unidades para adicionar.")
        
    else:
        nome_produto = input("Produto novo! Digite o nome do produto: ")
        produtos_encontrados = buscar_produtos_por_nome(nome_produto)

        if produtos_encontrados:
            produto_selecionado = produtos_encontrados[0]
            preco_medio = processar_preco(produto_selecionado['product_preco'])
            print(f"Preço predefinido: €{preco_medio:.2f}.")
        else:
            preco_medio = Decimal(input("Digite o preço estimado de venda: € "))  # Garantir que o preço seja Decimal
            print("Produto não encontrado no banco de dados.")

        inventario[codigo] = {
            "nome": nome_produto,
            "vendas": 0,
            "quantidade": 1,
            "preco_venda": preco_medio,
            "preco_compra": preco_compra_novo,  # Preço de compra inicial
            "data_venda": "N/A",
            "ultima_adicao": datetime.now().isoformat()
        }

    salvar_inventario_bd()
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
        for item in inventario_bd:
            inventario[item['codigo']] = {
                "nome": item['nome'],
                "vendas": item['vendas'],
                "quantidade": item['quantidade'],
                "preco_venda": item['preco_venda'],
                "preco_compra": item['preco_compra'],
                "data_venda": item['data_venda'],
                "ultima_adicao": item['ultima_adicao']
            }
    except mysql.connector.Error as erro:
        print(f"Erro ao acessar o banco de dados: {erro}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()



def salvar_inventario_bd():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        for codigo, dados in inventario.items():
            # Primeiro, apagar o registo existente com o mesmo código
            cursor.execute("DELETE FROM inventario WHERE codigo = %s", (codigo,))

            # Agora, inserir o novo registo atualizado
            cursor.execute(""" 
                INSERT INTO inventario (codigo, nome, vendas, quantidade, preco_venda, preco_compra, data_venda, ultima_adicao)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                codigo,
                dados['nome'],
                dados['vendas'],
                dados['quantidade'],
                dados['preco_venda'],
                dados['preco_compra'],
                dados['data_venda'],
                dados['ultima_adicao']
            ))

        conn.commit()
        print("Inventário atualizado com sucesso!")
    except mysql.connector.Error as erro:
        print(f"Erro ao salvar inventário: {erro}")
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
    os.system('cls' if os.name == 'nt' else 'clear')  # Limpa a tela antes de mostrar o inventário
    
    termo_pesquisa = input("Digite o nome do produto para pesquisar (ou pressione Enter para voltar): ").strip().lower()
    
    if termo_pesquisa == "":  # Se o usuário pressionar Enter sem digitar nada, retorna ao menu
        return

    produtos_encontrados = [produto for produto in inventario.values() if termo_pesquisa in produto['nome'].lower()]
    
    if produtos_encontrados:
        print("\nProdutos encontrados:")
        for produto in produtos_encontrados:
            preco_venda = float(produto['preco_venda'])  # Converte o preço para float
            print(f"Nome: {produto['nome']}, Quantidade: {produto['quantidade']}, Preço: €{preco_venda:.2f}")
    else:
        print("\nNenhum produto encontrado com esse nome.")

    input("\nPressione Enter para voltar ao menu...")


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
        inventario[codigo]["vendas"] += 1  # Incrementa a quantidade de vendas
        inventario[codigo]["data_venda"] = datetime.now().date()  # Atualiza a data da última venda
        
        # Subtrai 1 unidade da quantidade no inventário
        if inventario[codigo]["quantidade"] > 0:
            inventario[codigo]["quantidade"] -= 1
        else:
            print("⚠️ Erro: Estoque insuficiente para venda!")

        # Pergunta sobre a garantia
        garantia = input("Digite o período de garantia (em meses) para o produto: ")
        print(f"Venda confirmada! Garantia de {garantia} meses para o produto {inventario[codigo]['nome']}.")
        
        # Registra a venda no histórico
        preco_compra = inventario[codigo]["preco_compra"]
        data_compra = inventario[codigo]["data_venda"]  # Ou a data original de compra do inventário
        
        # Conexão com o banco de dados
        conn = mysql.connector.connect(user='root', password='leandro', host='localhost', database='loja')
        cursor = conn.cursor()

        # Adiciona o histórico de preços
        cursor.execute("""
            INSERT INTO historico_precos_venda (codigo_produto, preco_venda, data_venda, preco_compra, data_compra)
            VALUES (%s, %s, %s, %s, %s)
        """, (codigo, preco_venda, datetime.now().date(), preco_compra, data_compra))

        # Confirma a alteração e fecha a conexão
        conn.commit()
        cursor.close()
        conn.close()

        print("Histórico de venda atualizado com sucesso!")
        
        # Atualiza o inventário no banco de dados
        salvar_inventario_bd()
        input("Pressione Enter para voltar ao menu.")
    else:
        print("Produto não encontrado no inventário.")
        input("Pressione Enter para voltar ao menu.")

def calcular_ganhos_ultimos_dias():
    dias = int(input("Digite o número de dias para calcular os ganhos das vendas confirmadas (0 para ganhos totais): "))
    total_ganhos = Decimal(0.0)  # Altere para Decimal

    if dias == 0:  # Calcula os ganhos totais
        for dados in inventario.values():
            if dados["vendas"] > 0:  # Só considera as vendas confirmadas
                # Converte ambos os valores para Decimal
                preco_venda = Decimal(dados["preco_venda"])
                preco_compra = Decimal(dados["preco_compra"])
                ganho_unitario = preco_venda - preco_compra
                total_ganhos += ganho_unitario * Decimal(dados["vendas"])  # Converte vendas para Decimal
        print(f"Ganho total das vendas confirmadas: € {total_ganhos:.2f}")
    else:  # Calcula os ganhos dos últimos X dias
        data_limite = datetime.now() - timedelta(days=dias)
        for dados in inventario.values():
            if dados["vendas"] > 0 and dados["data_venda"] >= data_limite.replace(hour=0, minute=0, second=0, microsecond=0):
                # Converte ambos os valores para Decimal
                preco_venda = Decimal(dados["preco_venda"])
                preco_compra = Decimal(dados["preco_compra"])
                ganho_unitario = preco_venda - preco_compra
                total_ganhos += ganho_unitario * Decimal(dados["vendas"])  # Converte vendas para Decimal
        print(f"Ganho total das vendas confirmadas nos últimos {dias} dias: € {total_ganhos:.2f}")

    input("Pressione Enter para voltar ao menu.")

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
    valor_iva = float(produto['preco_venda']) * float(iva_percentual)

    custo_envio = produto.get('custo_envio', Decimal(0.0))  # Usa 0.0 como valor padrão se 'custo_envio' não estiver presente

    total_com_iva = float(produto['preco_venda']) + float(valor_iva) + float(custo_envio)

    # Abre o arquivo para escrever a fatura
    with open(nome_arquivo, "w", encoding="utf-8") as fatura:
        fatura.write(f"Data da Venda: {produto['data_venda']}\n\n")
        fatura.write(f"{produto['nome']}{'.' * (20 - len(produto['nome']))}{float(produto['preco_venda']):.2f} €\n")
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
    # Carregar inventário antes de iniciar o loop
    carregar_inventario_bd()

    while True:
        exibir_menu()
        opcao = input("\nEscolha uma opção: ")

        if opcao == '1':
            codigo = input("Digite o código de barras: ")
            ler_codigo_barras(codigo)

        elif opcao == '2':
            exibir_inventario_bd()

        elif opcao == '3':
            calcular_ganhos_ultimos_dias()

        elif opcao == '4':
            confirmar_venda()

        elif opcao == '5':
            print("Saindo...")
            break

        else:
            print("Opção inválida! Tente novamente.")


# Executa o menu
if __name__ == "__main__":
    executar()
