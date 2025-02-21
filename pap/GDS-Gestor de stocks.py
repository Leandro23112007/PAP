import os
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
            print("Produto não encontrado no banco de dados.")
            preco_medio = Decimal(input("Digite o preço estimado de venda: € "))  # Garantir que o preço seja Decimal
            
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

def exibir_inventario_bd(cliente=True):
    while True:  # Inicia o loop para o cliente
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

        if not cliente:  # Se não for cliente, o loop vai parar após mostrar os resultados
            break

        input("\nPressione Enter para continuar pesquisando ou voltar ao menu ...")


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
    while True:
        codigo = input("Digite o código de barras do produto para confirmar a venda (ou 0 para voltar ao menu): ")

        if codigo == "0":
            return  # Sai da função e volta ao menu

        if codigo not in inventario:
            print("⚠️ Erro: Produto não encontrado no inventário!")
            continue  # Pede um novo código de barras

        produto = inventario[codigo]

        if produto["quantidade"] <= 0:
            print("⚠️ Erro: Estoque insuficiente para venda! Tente outro produto.")
            continue  # Pede um novo código de barras

        try:
            preco_venda = Decimal(input(f"Digite o preço de venda para o produto {produto['nome']}: € "))
        except:
            print("⚠️ Erro: Insira um valor válido para o preço de venda.")
            continue

        try:
            garantia = int(input("Digite o período de garantia (em meses) para o produto: "))
        except:
            print("⚠️ Erro: Insira um número válido para a garantia.")
            continue

        try:
            conexao = mysql.connector.connect(**db_config)
            cursor = conexao.cursor()
            data_venda = datetime.now().date()
            cursor.execute(
                """
                INSERT INTO historico_precos_venda (codigo_produto, nome_produto, preco_venda, data_venda, preco_compra, data_compra)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (codigo, produto["nome"], preco_venda, data_venda, produto["preco_compra"], produto.get("data_compra", data_venda))
            )
            
            # Atualizar inventário no dicionário e no banco de dados
            produto["quantidade"] -= 1
            produto["vendas"] = produto.get("vendas", 0) + 1
            
            cursor.execute(
                """
                UPDATE inventario
                SET quantidade = %s, vendas = %s
                WHERE codigo = %s
                """,
                (produto["quantidade"], produto["vendas"], codigo)
            )
            
            conexao.commit()

            print(f"✅ Venda confirmada! Garantia de {garantia} meses para o produto {produto['nome']}.")
            print("✅ Histórico de venda atualizado com sucesso!")
            print("✅ Inventário atualizado com sucesso!")

            produto_fatura = {
                "nome": produto["nome"],
                "preco_venda": preco_venda,
                "data_venda": data_venda.strftime("%Y-%m-%d"),
                "garantia": garantia,
                "custo_envio": Decimal(0.0)
            }
            imprimir_fatura(produto_fatura)

            break

        except mysql.connector.Error as erro:
            print(f"❌ Erro ao registrar a venda no banco de dados: {erro}")

        finally:
            cursor.close()
            conexao.close()
    
    input("Pressione Enter para voltar ao menu.")

def calcular_ganhos_ultimos_dias():
    dias = int(input("Digite o número de dias para calcular os ganhos das vendas confirmadas (0 para ganhos totais): "))

    # Conectar ao banco de dados
    conexao = mysql.connector.connect(**db_config)
    cursor = conexao.cursor()

    if dias == 0:  # Calcula os ganhos totais
        cursor.execute("SELECT SUM(preco_venda) FROM historico_precos_venda")
        total_ganhos = cursor.fetchone()[0]  # Pega o resultado da soma

        if total_ganhos is None:  # Se não houver vendas, evitar erro de NoneType
            total_ganhos = 0.0

        print(f"\nGanho total das vendas confirmadas: € {total_ganhos:.2f}")

    else:  # Calcula os ganhos dos últimos X dias
        data_limite = (datetime.now() - timedelta(days=dias)).date()
        cursor.execute("""
            SELECT SUM(preco_venda) FROM historico_precos_venda WHERE data_venda >= %s
        """, (data_limite,))
        total_ganhos = cursor.fetchone()[0]  # Pega o resultado da soma

        if total_ganhos is None:  # Se não houver vendas, evitar erro de NoneType
            total_ganhos = 0.0

        print(f"\nGanho total das vendas confirmadas nos últimos {dias} dias: € {total_ganhos:.2f}")

    # Fecha a conexão
    cursor.close()
    conexao.close()
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

    total_com_iva = float(produto['preco_venda']) + valor_iva + float(custo_envio)

    # Abre o arquivo para escrever a fatura
    with open(nome_arquivo, "w", encoding="utf-8") as fatura:
        fatura.write(f"Data da Venda: {produto['data_venda']}\n\n")
        fatura.write(f"{produto['nome']}{'.' * (20 - len(produto['nome']))}{float(produto['preco_venda']):.2f} €\n")
        fatura.write(f"Envio{'.' * 15}{float(custo_envio):.2f} €\n")
        fatura.write(f"Garantia{'.' * 12}{produto.get('garantia', '1')} mês\n")
        fatura.write(f"IVA{'.' * 17}{int(iva_percentual * 100)} %\n\n")
        fatura.write(f"Total:{'.' * 14}{total_com_iva:.2f} €\n")
        fatura.write(f"{'-' * 28}\n")
        fatura.write(f"{'-' * 28}\n")
        fatura.write("Obrigado pela sua compra!\n")

    print(f"✅ Fatura oficial para o produto '{produto['nome']}' gerada com sucesso!")

def login():

    print("Bem-vindo ao GDS!")
    print("Escolha uma opção:")
    print("1. Entrar como Cliente (apenas consultar inventário)")
    print("2. Entrar como Administrador (acesso completo)")

    escolha = input("Digite sua opção (1 ou 2): ")

    if escolha == '1':
        # Acesso como cliente, só pode ver o inventário
        return "cliente"

    elif escolha == '2':
        # Acesso como administrador, precisa da senha
        senha = input("Digite a senha de administrador: ")
        
        # Verifique a senha. Pode ser uma senha fixa ou consultada de outro lugar.
        if senha == "leandro":  # Altere para a senha desejada
            return "administrador"
        else:
            print("Senha incorreta. Acesso negado.")
            return "negado"

    else:
        print("Opção inválida. Saindo...")
        return "negado"


def executar():
    limpar_tela()
    # Login inicial
    perfil = login()

    if perfil == "negado":
        return  # Encerra o programa em caso de falha no login

    # Carregar inventário antes de iniciar o loop
    carregar_inventario_bd()

    if perfil == "cliente":
        # Se for cliente, vai direto para a opção de consultar o inventário
        exibir_inventario_bd()
        return  # Finaliza o programa após exibir o inventário

    while True:
        exibir_menu()
        opcao = input("\nEscolha uma opção: ")

        if perfil == "administrador":  # Admin pode acessar todas as opções
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
