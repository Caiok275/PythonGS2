import os

import json
import oracledb
import pandas as pd
from datetime import datetime

# Váriavel que armazena o nome do usuário após um login bem sucedido
usuario_logado = ""
# Exames, doutores e horas disponíveis

# ================= Funções =================

# Apaga o terminal independente do sistema operacional
def limpar_tela() -> None:
    os.system("cls" if os.name == "nt" else "clear")

# Lê um arquivo .txt e retorna um dicionário
def ler_txt(nm_arq: str) -> dict:
    dados = {}
    try:
        with open(nm_arq, "r", encoding="utf-8") as f:
            for linha in f:
                key, value = linha.strip().split(":")
                dados[key] = value
    except FileNotFoundError:
        pass  # Se não houver arquivo, apenas retorna vazio
    return dados    

def gravar_json(nome_arquivo: str, dados: list) -> bool:
    try:
        with open(nome_arquivo, "x", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
        return True
    except FileExistsError:
        return False
    except:
        return False

def ler_json(nome_arquivo: str) -> list | None:
    try:
        with open(nome_arquivo, "r", encoding="utf-8") as f:
            dados = json.load(f)
        return dados
    except FileNotFoundError:
        return None
    
def pegar_usuario_logado() -> str:
    global usuario_logado
    return usuario_logado

# Recebe o nome do usuário e senha e o implementa no dicionario "usuario"
def criar_usuario(arq_usuario: str ,usuario: dict) -> None:
    while True:
        limpar_tela()
        nome = solicitar_usuario(usuario) 
        if nome is None:
            return  # Usuário optou por voltar
        senha = solicitar_senha()
        if senha is None:
            return # Usuário optou por voltar
        pedir_confirmacao(nome, senha)
        confirmacao = confirmar()
        if confirmacao == False:
            continue # Usuário decidiu refazer seu cadastro
        usuario[nome] = senha
        input("\nUsuário cadastrado com sucesso! Pressione ENTER para continuar...\n")
        dicionario_para_txt(arq_usuario,usuario)
        break

# Pergunta ao usuário seu nome e checa se o nome colocado já foi cadastrado antes
def solicitar_usuario(usuario: dict) -> str | None:
    while True:
        nome = input("Digite seu nome ou pressione 0 para voltar: ").strip().upper()
        if nome == "0":
            return
        elif nome in usuario:
            limpar_tela()
            print("\nEste nome já está cadastrado. Tente novamente.\n")
        elif nome == "":
            limpar_tela()
            print("É obrigatorio escrever o seu nome")
        else:
            return nome
        
# Pergunta o usuário uma senha e recusa senha "vazia"
def solicitar_senha() -> str:
    while True:
        senha = input("Digite uma senha:").strip()
        if senha == "0":
            return
        elif senha == "":
            limpar_tela()
            print("É necessario digitar uma senha para se dastrar\n")
            continue
        else:
            return senha

# Pergunta se todos os dados inseridos estão de acordo
def pedir_confirmacao(nome: str, senha:str):
    print("\nConfira os dados antes de registrar:")
    print(f"Nome: {nome}")
    print(f"Senha: {senha}\n")
    print("Os dados estão corretos?")

# Pergunta se todos os dados estão corretos e retorna um valor boolean dependendo da resposta
def confirmar() -> bool:
    while True:
        confirmacao = input("Digite 'Sim' ou 'Não': ").strip().lower()
        if confirmacao in ("sim", "s"):
            return True
        elif confirmacao in ("não", "nao", "n"):
            input("\nOK, pressione ENTER para tentar novamente...\n")
            return False
        else:
            print("Resposta inválida. Digite 'sim' ou 'não'.")

# Grava um dicionário em um arquivo .txt
def dicionario_para_txt(nm_arq: str, dicionario: dict) -> None:
    with open(nm_arq, "a", encoding="utf-8") as f:
        for key, value in dicionario.items():
            f.write(f"{key}:{value}\n")

# Verifica se o nome e senha condizem
def autentificacao(usuario: dict) -> bool:
    while True:
        print("Digite seu nome e sua senha ou digite 0 para cancelar:\n")
        nome = input("Nome:").upper()
        if nome == "0":
            break # Usuário optou por voltar
        senha = input("Senha:")
        if senha == "0":
            break # Usuário optou por voltar
        liberado = conferir_credencial(usuario, nome, senha)
        if liberado == False:
            limpar_tela()
            print("Senha ou nome incorreto!!!")
            continue # nome ou senha incorretos
        else:
            # Atribui o nome autentificado na variável global usuario_logado e retorna o valor "True"
            global usuario_logado
            usuario_logado = nome
            limpar_tela()
            input("Login realizado com sucesso, pressione ENTER para continuar...")
            return True

# Confere se a senha e o email está correto
def conferir_credencial(usuario: dict, nome: str, senha: str) -> bool:
    for nome_correto, senha_correta in usuario.items():
        if nome == nome_correto and senha == senha_correta:
            return True
    return False

# ================= Tela de Login =================
def login():

    arq_usuario = "usuario.txt"
    while True:
        # lê o arquivo usuario.txt e retorna em um dicionário usuario
        usuario = ler_txt(arq_usuario) 
        limpar_tela()
        print("-"*10, "Bem Vindo", "-"*10)
        print()
        print("1.Fazer Login")
        print("2.Não possui cadastro ainda? Digite 2 para Criar um usuário!")
        print()
        print("0.SAIR")

        # Estrutar match/case
        opcao = input("Digite uma das opções:")
        match opcao:
            case "0":
                limpar_tela()
                print("Finalizando o código...")
                break
            case "1": 
                limpar_tela()
                liberar = autentificacao(usuario)
                if liberar == True:
                    return True
            case "2":
                criar_usuario(arq_usuario,usuario)
            case _:
                limpar_tela()
                input("Selecione uma opção valida! Pressione ENTER para continuar...")

# ================= Menu Principal =================
def menu():
    while True:
        limpar_tela()
        print("-"*10, "Menu Principal", "-"*10)
        print()
        print("1.Medir seu nível de estresse")
        print("2.Ver seu histórico de estresse")
        print("3.Gravar seu histórico em um arquivo json")
        print()
        print("0.SAIR")

        opcao = input("Digite uma das opções:")
        match opcao:
            case "0":
                sair()
                break
            case "1":
                medidor_estresse()
            case "2":
                historico_completo = sql_historico()
                mostrar_historico(historico_completo)
            case "3":
                gravar_historico_json()
            case _:
                limpar_tela()
                print("Opção inválida")

        input("Pressione ENTER para continuar...")

# ================= Funções do Menu =================
def medidor_estresse():
    limpar_tela()
    print("="*20,"Medidor de estresse", "="*20)
    print("Responda as perguntas do questionário a seguir com números")
    print("de 1 a 5 sendo:")
    print("1 = Muito ruim/baixo | 2 = Ruim/baixo | 3 = Regular")
    print("4 = Bom/alto | 5 = Muito bom/alto\n")

    perguntas = ler_json("Perguntas.json")
    if not perguntas:
        return
    
    respostas = []
    for pergunta in perguntas:
        while True:
            try:
                print(f"{pergunta} (Responda entre 1-5 ou 0 para retornar):")
                escolha = int(input("Resposta:"))
                if escolha == 0:
                    print("Voltando para o menu principal...")
                    return
                elif escolha < 1 or escolha > 5:
                    limpar_tela()
                    input("Digite um número entre 1-5! Pressione ENTER para continuar...")
                    continue
                else:
                    respostas.append(escolha)
                    break
            except ValueError:
                limpar_tela()
                input("Digite um número entre 1-5! Pressione ENTER para continuar...")
                continue

    estresse_medio = calculador_estresse(respostas)
    nivel = nivel_estresse(estresse_medio)
    limpar_tela()
    print("="*20,"Resultado","="*20)
    print(f"Seu nível médio de estresse é: {estresse_medio:.2f}")
    print(f"Seu nível de estresse é: {nivel}")
    print()
    gravado = guardar_avaliacao(estresse_medio)
    if not gravado:
        print("Houve algum erro com a conexão com o banco de dados, contate o moderador.")
    else:
        print("Avaliação concluída!")

def calculador_estresse(respostas: list) -> float:
    soma = sum(respostas)
    media = soma / len(respostas)
    return media

def nivel_estresse(media: float) -> str:
    if media < 4.0:
        return "\033[34mBaixo\033[m"
    elif media < 3.0:
        return "\033[33mModerado\033[m"
    else:
        return "\033[31mAlto\033[m"
def guardar_avaliacao(nivel_estresse: float) -> bool:
    nm_funcionario = pegar_usuario_logado()
    dt_avaliacao = datetime.now().strftime("%d/%m/%Y")

    sql = """INSERT INTO T_FUNCIONARIO (nm_funcionario, nivel_estresse, dt_avaliacao) VALUES (:1, :2, TO_DATE(:3, 'DD/MM/YYYY'))"""

    try:
        inst_cadastro.execute(sql, (nm_funcionario, nivel_estresse, dt_avaliacao))
        conn.commit()
        return True
    except:
        return False
        pass

def mostrar_historico(df_historico: pd.DataFrame = None):
    limpar_tela()
    print("="*20, "Seu Histórico de Estresse", "="*20)
    if df_historico is None:
        print("Nenhum funcionário foi registrado ainda, tente novamente mais tarde.")
    else:
        print(df_historico)
        print()

def sql_historico():
    nm_funcionario = pegar_usuario_logado()
    sql = "SELECT * FROM T_FUNCIONARIO WHERE nm_funcionario = :1"
    df_historico = listar_funcionario(sql, nm_funcionario)
    return df_historico

# funcao que lista todos os itens da tabela
def listar_funcionario(sql: str, parametro: str = None) -> pd.DataFrame | None:  
    lista_doutores = []  # Lista para captura de dados do Banco
    try:
        # Instrução SQL com base no que foi selecinado na tela de menu
        if not parametro:
            inst_consulta.execute(sql)
        else:
            inst_consulta.execute(sql, (parametro,))

        # Captura todos os registros da tabela e armazena no objeto data
        data = inst_consulta.fetchall()

        # Insere os valores da tabela na Lista
        for dt in data:
            lista_doutores.append(dt)

        # ordena a lista
        lista_doutores = sorted(lista_doutores)

        # Gera um DataFrame com os dados da lista utilizando o Pandas
        dados_df = pd.DataFrame.from_records(
            lista_doutores, columns=['id_funcionario', 'nm_funcionario', 'nivel_estresse', 'dt_avaliacao'], index='id_funcionario')
        
        # Verifica se não há registro através do dataframe
        if dados_df.empty:
            return None
        else:
            return dados_df 
    except:
        print("Erro na transação do BD")
        return None

def trasformar_df_dicionario(df: pd.DataFrame) -> dict:
    dicionario = {}
    for i, coluna in df.iterrows():
        dicionario[i] = {
            "id_funcionario": i,
            "nm_funcionario": coluna["nm_funcionario"],
            "nivel_estresse": coluna["nivel_estresse"],
            "dt_avaliacao": coluna["dt_avaliacao"].strftime("%d/%m/%Y"),
        }

    return dicionario

def gravar_historico_json():
    limpar_tela()
    df_historico = sql_historico()
    if df_historico is None:
        print("Nenhum resultado encontrado.")
        return
    mostrar_historico(df_historico)
    
    df_dict = trasformar_df_dicionario(df_historico)
    nome_json = input("Digite o nome do arquivo json (sem extensão): ").strip()
    gravado = gravar_json(nome_json + ".json", df_dict)
    if gravado:
        print(f"Histórico salvo com sucesso!")
    else:
        print("Arquivo já existe ou houve um erro ao salvar.")

def sair():
    global conexao
    conexao = False
    limpar_tela()
    print("Finalizando o código...")


# ================= Conexão =================
try :
    conn = oracledb.connect(user = "rm562979",password = "251004",dsn = "oracle.fiap.com.br:1521/ORCL")
    inst_cadastro = conn.cursor()
    inst_consulta = conn.cursor()
    inst_alteracao = conn.cursor()
    inst_exclusao= conn.cursor()

except Exception as e:
    print(e)
    conexao=False
else:
    conexao=True

while conexao:
    login = login()
    if login == True:
        menu()