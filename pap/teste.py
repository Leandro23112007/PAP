import os 
import mysql.connector
from datetime import datetime, timedelta
from decimal import Decimal

# Configuração do banco de dados
db_config = {
    'host': 'localhost',  # Endereço do servidor
    'user': 'root',       # Usuário do banco de dados
    'password': 'leandro',  # Senha do banco de dados
    'database': 'loja'  # Nome do banco de dados
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

# Função para ler código de barras e registrar vendas
def ler_codigo_barras(codigo):
    preco_compra = float(input("Digite o preço de compra: € "))
    data_venda = datetime.now().date()

    # Verifica se o código já existe no inventário
    if codigo in inventario:
        inventario[codigo]["vendas"] += 1
        inventario[codigo]["quantidade"] += 1  # Incrementa a quantidade ao registrar uma nova venda
        inventario[codigo]["data_venda"] = data_venda
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

        # Adiciona o novo produto ao inventário
        inventario[codigo] = {
            "nome": nome_produto,
            "vendas": 0,
            "preco_venda": preco_medio,
            "preco_compra": preco_compra,
            "data_venda": "N/A",
            "quantidade": 0,
            "ultima_adicao": datetime.now().isoformat()
        }

    salvar_inventario_bd()
    imprimir_fatura(inventario[codigo])

    input("Pressione Enter para continuar.")

def processar_preco(preco):
    """
    Função para processar o preço, garantindo que seja um número decimal válido.
    Pode ser ajustada conforme as necessidades, como arredondamentos ou formatação de strings.
    """
    try:
        preco_decimal = Decimal(preco)  # Converte o preço para um número decimal
        return preco_decimal
    except (ValueError, TypeError) as e:
        print(f"Erro ao processar o preço: {e}")
        return Decimal(0)  # Retorna 0 se houver um erro

# Função para garantir a pasta de faturas
def garantir_pasta_faturas():
    pasta_faturas = 'faturas'
    if not os.path.exists(pasta_faturas):
        os.makedirs(pasta_faturas)

# Função para limpar a tela
def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

# Função para exibir o menu
def menu():
    limpar_tela()
    print("\nMenu de Controle de Vendas")
    print("1. Digitar código de barras (Automação de Vendas)")
    print("2. Consultar Inventário de Vendas")
    print("3. Ver Ganhos das Vendas Confirmadas (0 = Ganhos Totais)")
    print("4. Confirmar Venda")
    print("5. Salvar e Sair")

# Dicionário para armazenar o inventário de vendas
inventario = {}

# Carregar inventário do banco de dados
def carregar_inventario_bd():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM inventario")
        inventario_bd = cursor.fetchall()

        # Carrega cada produto no inventário
        for produto in inventario_bd:
            inventario[produto['codigo']] = {
                "nome": produto['nome'],
                "vendas": produto['vendas'],
                "preco_venda": produto['preco_venda'],
                "preco_compra": produto['preco_compra'],
                "data_venda": produto['data_venda'],
                "quantidade": produto.get('quantidade', 0),  # Atribui quantidade, se disponível
                "ultima_adicao": produto['ultima_adicao']
            }
    except mysql.connector.Error as erro:
        print(f"Erro ao acessar o banco de dados: {erro}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Salva inventário no banco de dados
def salvar_inventario_bd():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        for codigo, dados in inventario.items():
            cursor.execute("""
                INSERT INTO inventario (codigo, nome, vendas, preco_venda, preco_compra, data_venda, ultima_adicao, quantidade)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                nome = VALUES(nome),
                vendas = VALUES(vendas),
                preco_venda = VALUES(preco_venda),
                preco_compra = VALUES(preco_compra),
                data_venda = VALUES(data_venda),
                ultima_adicao = VALUES(ultima_adicao),
                quantidade = VALUES(quantidade)
            """, (
                codigo,
                dados['nome'],
                dados['vendas'],
                dados['preco_venda'],
                dados['preco_compra'],
                dados['data_venda'],
                dados['ultima_adicao'],
                dados['quantidade']
            ))

        conn.commit()
        print("Inventário salvo com sucesso no banco de dados!")
    except mysql.connector.Error as erro:
        print(f"Erro ao salvar inventário no banco de dados: {erro}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# Função para calcular os ganhos dos últimos dias
def calcular_ganhos_ultimos_dias():
    try:
        # Estabelece a conexão com o banco de dados
        conexao = mysql.connector.connect(**db_config)
        cursor = conexao.cursor()
        
        # Definir o número de dias para a consulta (por exemplo, 7 dias)
        dias_anteriores = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        # Consulta para somar os ganhos dos últimos 7 dias
        query = f"""
        SELECT SUM(valor_venda) FROM vendas
        WHERE data_venda >= '{dias_anteriores}'
        """
        cursor.execute(query)
        resultado = cursor.fetchone()
        
        # Exibe o total de ganhos
        if resultado[0] is not None:
            print(f"Ganhos nos últimos 7 dias: €{resultado[0]:.2f}")
        else:
            print("Não há vendas nos últimos 7 dias.")
        
        cursor.close()
        conexao.close()
    
    except mysql.connector.Error as erro:
        print(f"Erro ao calcular ganhos: {erro}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao calcular ganhos: {e}")


# Função para confirmar a venda e atualizar o inventário
def confirmar_venda():
    try:
        # Recebe o código de barras e a quantidade a ser vendida
        codigo_produto = input("Digite o código do produto: ")
        quantidade = int(input("Digite a quantidade: "))
        
        # Estabelece a conexão com o banco de dados
        conexao = mysql.connector.connect(**db_config)
        cursor = conexao.cursor()
        
        # Verifica o estoque do produto
        query_estoque = f"""
        SELECT product_estado, product_preco FROM produtos
        WHERE product_name = '{codigo_produto}'
        """
        cursor.execute(query_estoque)
        produto = cursor.fetchone()

        if produto:
            estoque_atual = produto[0]
            preco_produto = produto[1]

            if estoque_atual >= quantidade:
                # Atualiza o estoque
                novo_estoque = estoque_atual - quantidade
                query_atualizar_estoque = f"""
                UPDATE produtos
                SET product_estado = {novo_estoque}
                WHERE product_name = '{codigo_produto}'
                """
                cursor.execute(query_atualizar_estoque)
                conexao.commit()

                # Registra a venda
                valor_total = preco_produto * quantidade
                data_venda = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                query_registrar_venda = f"""
                INSERT INTO vendas (product_name, quantidade, valor_venda, data_venda)
                VALUES ('{codigo_produto}', {quantidade}, {valor_total}, '{data_venda}')
                """
                cursor.execute(query_registrar_venda)
                conexao.commit()

                print(f"Venda confirmada: {quantidade} unidades de {codigo_produto} vendidas por €{valor_total:.2f}")
            else:
                print("Estoque insuficiente para a venda.")
        else:
            print("Produto não encontrado no inventário.")
        
        cursor.close()
        conexao.close()
    
    except mysql.connector.Error as erro:
        print(f"Erro ao confirmar a venda: {erro}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao confirmar a venda: {e}")

# Exibe o inventário do banco de dados
def exibir_inventario_bd():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM inventario")
        inventario_bd = cursor.fetchall()

        print("Inventário atual de vendas:")
        for linha in inventario_bd:
            print(f"{linha['codigo']} - {linha['nome']} - Vendas: {linha['vendas']} - Preço Venda: € {linha['preco_venda']:.2f}")
    except mysql.connector.Error as erro:
        print(f"Erro ao acessar o banco de dados: {erro}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

    input("Pressione Enter para voltar ao menu.")

# Função para imprimir a fatura
def imprimir_fatura(produto):
    garantir_pasta_faturas()

    if produto['data_venda'] == 'N/A':
        nome_arquivo = f"faturas/{produto['nome'].replace(' ', '_').replace('-', '_')}_N_A.txt"
    else:
        nome_arquivo = f"faturas/{produto['nome'].replace(' ', '_').replace('-', '_')}_{produto['data_venda']}.txt"

    iva_percentual = Decimal(0.23)
    valor_iva = produto['preco_venda'] * iva_percentual
    custo_envio = produto.get('custo_envio', Decimal(0.0))

    total_com_iva = float(produto['preco_venda']) + float(valor_iva) + float(custo_envio)

    with open(nome_arquivo, "w", encoding="utf-8") as fatura:
        fatura.write(f"Data da Venda: {produto['data_venda']}\n\n")
        fatura.write(f"{produto['nome']}{'.' * (20 - len(produto['nome']))}{produto['preco_venda']:.2f} €\n")
        fatura.write(f"Envio{'.' * 15}{custo_envio:.2f} €\n")
        fatura.write(f"Garantia{'.' * 12}{produto.get('garantia', '1')} mês\n")
        fatura.write(f"IVA{'.' * 17}{int(iva_percentual * 100)} %\n\n")
        fatura.write(f"Total:{'.' * (20 - len('Total:'))}{total_com_iva:.2f} €\n")
        fatura.write(f"Preço Unitário:{'.' * (17 - len('Preço Unitário:'))}{produto['preco_venda']:.2f} €\n")
        fatura.write(f"Produto Garantido por: {produto['garantia']} meses\n\n")
        fatura.write("Obrigado pela sua compra!\n")

    print(f"Fatura para o produto '{produto['nome']}' gerada com sucesso!")

# Exemplo de uso
carregar_inventario_bd()
menu()

def executar():
    try:
        # Estabelece a conexão usando a configuração
        conexao = mysql.connector.connect(**db_config)

       
        
        carregar_inventario_bd()  # Carrega o inventário do banco de dados

        while True:
            print("\nIniciando o menu...")  # Log de depuração
            menu()
            escolha = input("Escolha uma opção: ")

            if escolha == '1':
                codigo = input("Digite o código de barras: ")
                ler_codigo_barras(codigo)
            elif escolha == '2':
                exibir_inventario_bd()  # Exibe o inventário a partir do banco
            elif escolha == '3':
                calcular_ganhos_ultimos_dias()
            elif escolha == '4':
                confirmar_venda()
            elif escolha == '5':
                salvar_inventario_bd()  # Salva o inventário no banco antes de sair
                print("Saindo...")
                break
            else:
                print("Opção inválida! Tente novamente.")
    
    except mysql.connector.Error as erro:
        print(f"Erro na conexão com o banco de dados: {erro}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
    finally:
        print("Programa finalizado.")

# Chama a função principal para iniciar o programa
executar()
