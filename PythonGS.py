import os
import json
import oracledb
import pandas as pd
from datetime import datetime

# Váriavel que armazena o ID do funcionário após um login bem sucedido
id_funcionario_logado = None
usuario_logado = ""

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
    
def pegar_usuario_logado() -> str:
    global usuario_logado
    return usuario_logado

def pegar_id_funcionario_logado() -> int:
    global id_funcionario_logado
    return id_funcionario_logado


# Cria um novo funcionário no banco de dados
def criar_usuario() -> None:
    while True:
        limpar_tela()
        nome = solicitar_nome_funcionario() 
        if nome is None:
            return  # Usuário optou por voltar
        idade = solicitar_idade()
        if idade is None:
            return
        modelo = solicitar_modelo_trabalho()
        if modelo is None:
            return
        setor = solicitar_setor()
        if setor is None:
            return
        
        limpar_tela()
        pedir_confirmacao_cadastro(nome, idade, modelo, setor)
        confirmacao = confirmar()
        if confirmacao == False:
            continue # Usuário decidiu refazer seu cadastro
        
        # Insere no banco de dados
        sucesso = inserir_funcionario_bd(nome, idade, modelo, setor)
        if sucesso:
            input("\nFuncionário cadastrado com sucesso! Pressione ENTER para continuar...\n")
            break
        else:
            input("\nErro ao cadastrar funcionário. Pressione ENTER para tentar novamente...\n")

# Solicita nome do funcionário
def solicitar_nome_funcionario() -> str | None:
    while True:
        limpar_tela()
        nome = input("Digite o nome do funcionário ou pressione 0 para voltar: ").strip().upper()
        if nome == "0":
            return None
        elif nome == "":
            print("É obrigatório escrever o nome do funcionário\n")
            input("Pressione ENTER para continuar...")
        else:
            return nome

# Solicita idade
def solicitar_idade() -> int | None:
    while True:
        try:
            limpar_tela()
            idade_input = input("Digite a idade (18-70) ou 0 para voltar: ").strip()
            if idade_input == "0":
                return None
            idade = int(idade_input)
            if 18 <= idade <= 70:
                return idade
            else:
                print("A idade deve estar entre 18 e 70 anos.\n")
                input("Pressione ENTER para continuar...")
        except ValueError:
            print("Digite um número válido para a idade.\n")
            input("Pressione ENTER para continuar...")

# Solicita modelo de trabalho
def solicitar_modelo_trabalho() -> int | None:
    while True:
        limpar_tela()
        print("Selecione o modelo de trabalho:")
        print("1 - Presencial")
        print("2 - Remoto")
        print("3 - Híbrido")
        print("Digite '0' para voltar")
        
        try:
            opcao = int(input("Opção: ").strip())
            if opcao == 0:
                return None
            elif opcao in {1, 2, 3}:
                return opcao - 1
        except ValueError:
            print("Opção inválida. Tente novamente.\n")
            input("Pressione ENTER para continuar...")

# Solicita setor
def solicitar_setor() -> str | None:
    while True:
        limpar_tela()
        setor = input("Digite o setor (ex: TI, Marketing, RH) ou 0 para voltar: ").strip().upper()
        if setor == "0":
            return None
        elif setor == "":
            limpar_tela()
            print("É obrigatório informar o setor.\n")
            input("Pressione ENTER para continuar...")
        else:
            return setor

# Mostra os dados para confirmação
def pedir_confirmacao_cadastro(nome: str, idade: int, modelo: int, setor: str) -> None:
    tipos_modelos = {0: "Presencial", 1: "Remoto", 2: "Híbrido"}
    print("\nConfira os dados antes de registrar:")
    print(f"Nome: {nome}")
    print(f"Idade: {idade}")
    print(f"Modelo de Trabalho: {tipos_modelos[modelo]}")
    print(f"Setor: {setor}\n")
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

# Insere funcionário no banco de dados
def inserir_funcionario_bd(nome: str, idade: int, modelo: int, setor: str) -> bool:
    try:
        # Insere o funcionário no banco de dados
        sql = """INSERT INTO T_ABTG_FUNCIONARIO (nm_funcionario, idade, modelo_trabalho, setor) 
                 VALUES (:1, :2, :3, :4)"""
        inst_cadastro.execute(sql, (nome, idade, modelo, setor))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao inserir funcionário: {e}")
        return False

# Autenticação baseada no banco de dados
def autenticacao() -> bool:
    while True:
        limpar_tela()
        print("Digite o nome do funcionário cadastrado ou digite 0 para cancelar:\n")
        nome = input("Nome: ").strip().upper()
        if nome == "0":
            return False
        
        # Verifica se o funcionário existe no banco
        id_funcionario = procurar_id_funcionario_db(nome)
        if id_funcionario is None:
            limpar_tela()
            print("Funcionário não foi registrado! Realize o cadastro primeiro.")
            input("Pressione ENTER para tentar novamente...")
            continue
        else:
            # Atribui o nome e ID às variáveis globais
            global usuario_logado, id_funcionario_logado
            usuario_logado = nome
            id_funcionario_logado = id_funcionario
            limpar_tela()
            input("Login realizado com sucesso, pressione ENTER para continuar...")
            return True

# Busca funcionário por nome no banco e retorna o ID
def procurar_id_funcionario_db(nome: str) -> int | None:
    try:
        sql = "SELECT id_funcionario FROM T_ABTG_FUNCIONARIO WHERE UPPER(nm_funcionario) = :1"
        inst_consulta.execute(sql, (nome,))
        resultado = inst_consulta.fetchone()
        if resultado:
            return resultado[0]
        return None
    except Exception as e:
        print(f"Erro! Não foi possível encontrar funcionário: {e}")
        return None

# ================= Tela de Login =================
def login():
    while True:
        limpar_tela()
        print("-"*10, "Bem Vindo", "-"*10)
        print()
        print("1. Fazer Login")
        print("2. Não possui cadastro ainda? Digite 2 para Criar um funcionário!")
        print()
        print("0. SAIR")

        opcao = input("Digite uma das opções: ")
        match opcao:
            case "0":
                limpar_tela()
                print("Finalizando o código...")
                return False
            case "1": 
                liberar = autenticacao()
                if liberar:
                    return True
            case "2":
                criar_usuario()
            case _:
                limpar_tela()
                input("Selecione uma opção válida! Pressione ENTER para continuar...")

# ================= Menu Principal =================
def menu():
    while True:
        limpar_tela()
        print("-"*10, "Menu Principal", "-"*10)
        print()
        print("1. Realizar avaliação diária de estresse")
        print("2. Ver histórico de registros")
        print("3. Ver sua análise de estresse")
        print("4. Ver sugestões da IA")
        print("5. Gravar informações em arquivo JSON")
        print()
        print("0. SAIR")

        opcao = input("\nDigite uma das opções: ")
        match opcao:
            case "0":
                sair()
                break
            case "1":
                realizar_avaliacao_diaria()
            case "2":
                ver_historico_registros()
            case "3":
                ver_analise_estresse()
            case "4":
                ver_sugestoes_ia()
            case "5":
                gravar_informacoes_json()

        input("Pressione ENTER para continuar...")

# ================ Submenu Gravar JSON ================
def gravar_informacoes_json():
    while True:
        limpar_tela()
        print("="*20, "Gravar Informações em JSON", "="*20)
        print("1. Gravar histórico de registros em JSON")
        print("2. Gravar análise de estresse em JSON")
        print("3. Gravar dicas em JSON")
        print()
        print("0. Voltar ao menu principal")

        opcao = input("\nDigite uma das opções: ")

        match opcao:
            case "0":
                break
            case "1":
                df = listar_historico()
                gravar_df_json(df)
                break
            case "2":
                df = listar_analise_estresse()
                gravar_df_json(df)
                break
            case "3":
                df = listar_sugestoes_ia()
                gravar_df_json(df)
                break
            case _:
                limpar_tela()
                print("Selecione uma opção válida!")

        input("Pressione ENTER para continuar...")

# ================= Avaliação Diária de Estresse =================

def realizar_avaliacao_diaria():
    # 1. Mostra as perguntas do questionário

    perguntas = perguntas_avaliacao()
    respostas = {}

    for tipo, pergunta in perguntas.items():
        while True:
            limpar_tela()
            try:
                print("="*20,"Medidor de estresse", "="*20)
                print("Responda as perguntas do questionário a seguir.")

                print(f"\n{pergunta}\n")
                # Adiciona instruções para perguntas de concordancia/qualidade
                if tipo in ["sono", "humor", "tensao", "energia", "motivacao"]:
                    print("Responda com um número de 1 a 5, sendo:")
                    print("1 = Muito ruim/baixo | 2 = Ruim/baixo | 3 = Regular")
                    print("4 = Bom/alto | 5 = Muito bom/alto\n")
                # Caso não seja uma avaliação de concordancia/qualidade
                else:
                    pass
                entrada = input("Resposta (ou pressione ENTER para cancelar): ").strip()
                if not entrada:
                    limpar_tela()
                    print("Avaliação cancelada. Retornando ao menu principal...")
                    return
                resposta = int(entrada)
                # Validação específica para perguntas que não são de 1-5
                if tipo == "horas_trabalho":
                    if 4 <= resposta <= 10:
                        respostas[tipo] = resposta
                        break
                    else:
                        limpar_tela()
                        print("Digite um número entre 4 e 10!")
                elif tipo == "pausas_diarias":
                    if 0 <= resposta <= 5:
                        respostas[tipo] = resposta
                        break
                    else:
                        limpar_tela()
                        print("Digite um número entre 0 e 5!")
                elif tipo == "exercicio_semana":
                    if 0 <= resposta <= 7:
                        respostas[tipo] = resposta
                        break
                    else:
                        limpar_tela()
                        print("Digite um número entre 0 e 7!")
                # Validação padrão para perguntas de 1-5
                else:
                    if 1 <= resposta <= 5:
                        respostas[tipo] = resposta
                        break
                    else:
                        limpar_tela()
                        print("Digite um número entre 1 e 5!")
            except ValueError:
                limpar_tela()
                input("Digite um número válido. Pressione ENTER para continuar...")
                continue
    
    # 2. Após a resposta. Calcula o nível médio de estresse, o tipo com o pior valor e a categoria de estresse
    estresse_medio = calculadora_estresse(respostas)
    pior_tipo = pegar_pior_tipo(respostas)
    categoria_estresse_valor = categoria_estresse(estresse_medio)

    # 3. Mostra o resultado
    limpar_tela()
    print("="*20,"Resultado","="*20)
    print(f"Seu nível médio de estresse é: {estresse_medio:.2f}")
    print(f"Sua categoria de estresse é: {categoria_estresse_valor}")
    print()

    # 4. Armazena os dados no banco de dados
    gravado = guardar_avaliacao(respostas, estresse_medio, categoria_estresse_valor, pior_tipo)
    if not gravado:
        print("Houve algum erro com a conexão com o banco de dados, contate o moderador.")
    else:
        print("Avaliação concluída!")

# Dicionário com as perguntas do questionário
def perguntas_avaliacao() -> dict:

    # Cada chave representa o tipo de pergunta e o valor é a pergunta em si
    perguntas = {
        "sono": "Como foi a qualidade do seu sono? (1-5): ",
        "humor": "Como está seu humor hoje? (1-5): ",
        "tensao": "Qual seu nível de tensão? (1-5): ",
        "energia": "Qual seu nível de energia? (1-5): ",
        "motivacao": "Qual seu nível de motivação? (1-5): ",
        "horas_trabalho": "Quantas horas trabalhou hoje? (4-10): ",
        "pausas_diarias": "Quantas pausas fez durante o dia? (0-5): ",
        "exercicio_semana": "Quantos dias se exercitou esta semana (0-7): "
    }


    return perguntas

def calculadora_estresse(respostas: dict) -> float:

    # Para realizar o cálculo da média de estresse, os fatores devem ser normalizados
    # em uma escala de 0 a 10

    # =========== Aumentam estresse ===========
    # formula: 10 * (valor - resposta_minima) / (resposta_maxima - resposta_minima)
    tensao = 10*(respostas["tensao"] - 1)/4
    horas_trabalho = 10*(respostas["horas_trabalho"] - 4)/6

    # ========== Diminuem estresse ===========
    # formula: 10 * (1 - (valor - resposta_minima) / (resposta_maxima - resposta_minima))
    sono = 10*(1 - (respostas["sono"] - 1)/4)
    humor = 10*(1 - (respostas["humor"] - 1)/4)
    energia = 10*(1 - (respostas["energia"] - 1)/4)
    motivacao = 10*(1 - (respostas["motivacao"] - 1)/4)
    pausas = 10*(1 - respostas["pausas_diarias"]/5)
    exercicio = 10*(1 - respostas["exercicio_semana"]/7)

    # ============ Nível de estresse (Média) ============
    estresse = (sono + humor + tensao + energia + motivacao + horas_trabalho + pausas + exercicio) / 8

    # Se algum dos items estiverem abaixo da média, identifica o pior tipo (caso haja empate, retorna o primeiro)
    return estresse

def pegar_pior_tipo(respostas: dict) -> str:
    # Se algum dos items estiverem abaixo da média, identifica o pior tipo (caso haja empate, retorna o primeiro)
    for tipo, valor in respostas.items():
        if valor <= 3:
            return next(tipo)
        else:
            return "Nenhum"

# Avalia a média calculada e retorna a categoria de estresse
def categoria_estresse(estresse: float) -> str:
    if estresse < 3:
        return "Baixo"
    elif estresse < 7:
        return "Moderado"
    else:
        return "Alto"

# Com base na avaliação, os dados serão armazenadas nas seguites tabelas:
# T_ABTG_REGISTRO_DIARIO, T_ABTG_ANALISE_ESTRESSE, T_ABTG_SUGESTAO_IA
def guardar_avaliacao(respostas: dict, estresse: float, categoria_estresse: str, pior_tipo: str) -> bool:
    try:
        id_funcionario = pegar_id_funcionario_logado()
        dt_registro = datetime.now()
        
        # Inserir avaliação na tabela de registros diários
        sql_registro = """INSERT INTO T_ABTG_REGISTRO_DIARIO 
                        (id_funcionario, dt_registro, sono, humor, tensao, 
                        energia, motivacao, horas_trabalho, pausas_diarias, exercicio_semana)
                        VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10)"""
        
        inst_cadastro.execute(sql_registro, (
            id_funcionario, dt_registro,
            respostas["sono"], respostas["humor"], respostas["tensao"],
            respostas["energia"], respostas["motivacao"], respostas["horas_trabalho"],
            respostas["pausas_diarias"], respostas["exercicio_semana"]
        ))
        
        # Recupera o ID do registro que acabou de ser inserido
        sql_id_registro = "SELECT id_registro FROM T_ABTG_REGISTRO_DIARIO WHERE id_funcionario = :1 AND dt_registro = :2"
        inst_consulta.execute(sql_id_registro, (id_funcionario, dt_registro))
        id_registro = inst_consulta.fetchone()[0]

        # Inserir análise de estresse na tabela de análise de estresse
        sql_analise = """INSERT INTO T_ABTG_ANALISE_ESTRESSE 
                 (id_registro, nivel_estresse, categoria_estresse, dt_analise)
                 VALUES (:1, :2, :3, :4)"""
        
        inst_cadastro.execute(sql_analise, (id_registro, estresse, categoria_estresse, dt_registro))

        # Recupera o ID da tabela de análise de estresse
        sql_get_analise = "SELECT id_analise FROM T_ABTG_ANALISE_ESTRESSE WHERE id_registro = :1"
        inst_consulta.execute(sql_get_analise, (id_registro,))
        id_analise = inst_consulta.fetchone()[0]

        # Gera sugestões baseadas na análise de estresse
        sugestao = sugestoes_ia(pior_tipo)

        # Insere a sugestão na tabela de sugestões da IA
        sql_sugestao = """INSERT INTO T_ABTG_SUGESTAO_IA 
                  (id_analise, categoria, mensagem_ia, dt_sugestao)
                  VALUES (:1, :2, :3, :4)"""
        
        inst_cadastro.execute(sql_sugestao, (id_analise, pior_tipo, sugestao, dt_registro))

        conn.commit()
        return True
    # Caso ocorra algum erro na conexão com o banco de dados
    except Exception as e:
        print(f"Erro ao guardar avaliação: {e}")
        return False
        
# Retorna a mensagem de sugestão que condiz com o pior tipo identificado
def sugestoes_ia(pior_tipo: str) -> None:

    sugestoes = {
        "sono": "Tente estabelecer uma rotina de sono consistente, evitando eletrônicos antes de dormir.",
        "humor": "Pratique atividades que você gosta e que elevem seu ânimo, como hobbies ou exercícios.",
        "tensao": "Incorpore técnicas de relaxamento, como meditação ou respiração profunda, em sua rotina diária.",
        "energia": "Mantenha uma alimentação equilibrada e faça pausas regulares para recarregar suas energias.",
        "motivacao": "Defina metas claras e alcançáveis para manter o foco e a motivação no trabalho.",
        "horas_trabalho": "Tente limitar suas horas de trabalho diárias para evitar sobrecarga e burnout.",
        "pausas_diarias": "Faça pausas curtas e frequentes durante o dia para melhorar a concentração e reduzir o estresse.",
        "exercicio_semana": "Incorpore exercícios físicos regulares em sua rotina semanal para melhorar o bem-estar geral.",
        "Nenhum": "Parabéns! Seu nível de estresse está equilibrado. Continue mantendo hábitos saudáveis."
    }

    for tipo, sugestao in sugestoes.items():
        if tipo == pior_tipo:
            return sugestao

# ================ Ver Histórico de Registros =================
def ver_historico_registros():
    df = listar_historico()
    limpar_tela()
    print("="*20, "Histórico de Registros", "="*20)
    if df is None:
        print("Nenhum registro encontrado.")
    else:
        print(df)
        
# funcao que lista todos os itens da tabela
def listar_historico() -> pd.DataFrame | None:  
    id_funcionario = pegar_id_funcionario_logado()
    lista_dados = []  # Lista para captura de dados do Banco
    try:
        # Instrução SQL com base no que foi selecinado na tela de menu
        inst_consulta.execute("""SELECT f.id_funcionario, f.nm_funcionario, a.nivel_estresse, r.dt_registro FROM T_ABTG_FUNCIONARIO f
        JOIN T_ABTG_REGISTRO_DIARIO r ON f.id_funcionario = r.id_funcionario
        JOIN T_ABTG_ANALISE_ESTRESSE a ON r.id_registro = a.id_registro WHERE f.id_funcionario = :1""", (id_funcionario,))

        # Captura todos os registros da tabela e armazena no objeto data
        data = inst_consulta.fetchall()

        # Insere os valores da tabela na Lista
        for dt in data:
            lista_dados.append(dt)

        # ordena a lista
        lista_dados = sorted(lista_dados)

        # Gera um DataFrame com os dados da lista utilizando o Pandas
        dados_df = pd.DataFrame.from_records(
            lista_dados, columns=['id_funcionario', 'nm_funcionario', 'nivel_estresse', 'dt_registro'], index='id_funcionario')
        
        # Verifica se não há registro através do dataframe
        if dados_df.empty:
            return None
        else:
            return dados_df 
    except Exception as e:
        print(f"Erro na transação do BD: {e}")
        return None
    
# ================= Ver Análise de Estresse =================
def ver_analise_estresse():
    limpar_tela()
    df = listar_analise_estresse()
    print("="*20, "Análise de Estresse", "="*20)
    if df is None:
        print("Nenhum registro encontrado.")
    else:
        print(df)

def listar_analise_estresse() -> pd.DataFrame | None:
    id_funcionario = pegar_id_funcionario_logado()
    lista_analises = []  # Lista para captura de dados do Banco
    try:
        # Instrução SQL para buscar análises de estresse do funcionário logado
        inst_consulta.execute("""SELECT a.id_analise, a.nivel_estresse, a.categoria_estresse, a.dt_analise 
                                 FROM T_ABTG_ANALISE_ESTRESSE a
                                 JOIN T_ABTG_REGISTRO_DIARIO r ON a.id_registro = r.id_registro
                                 WHERE r.id_funcionario = :1""", (id_funcionario,))

        # Captura todos os registros da tabela e armazena no objeto data
        data = inst_consulta.fetchall()

        # Insere os valores da tabela na Lista
        for dt in data:
            lista_analises.append(dt)

        # ordena a lista
        lista_analises = sorted(lista_analises)

        # Gera um DataFrame com os dados da lista utilizando o Pandas
        dados_df = pd.DataFrame.from_records(
            lista_analises, columns=['id_analise', 'nivel_estresse', 'categoria_estresse', 'dt_analise'], index='id_analise')
        
        # Verifica se não há registro através do dataframe
        if dados_df.empty:
            return None
        else:
            return dados_df 
    except Exception as e:
        print(f"Erro na transação do BD: {e}")
        return None

# ================= Ver Sugestões da IA =================
def ver_sugestoes_ia():
    limpar_tela()
    df = listar_sugestoes_ia()
    print("="*20, "Sugestões da IA", "="*20)
    if df is None:
        print("Nenhum registro encontrado.")
    else:
        print(df)

def listar_sugestoes_ia() -> pd.DataFrame | None:
    id_funcionario = pegar_id_funcionario_logado()
    lista_sugestoes = []  # Lista para captura de dados do Banco
    try:
        # Instrução SQL para buscar sugestões da IA do funcionário logado
        inst_consulta.execute("""SELECT s.id_sugestao, s.categoria, s.mensagem_ia, s.dt_sugestao 
                                 FROM T_ABTG_SUGESTAO_IA s
                                 JOIN T_ABTG_ANALISE_ESTRESSE a ON s.id_analise = a.id_analise
                                 JOIN T_ABTG_REGISTRO_DIARIO r ON a.id_registro = r.id_registro
                                 WHERE r.id_funcionario = :1""", (id_funcionario,))

        # Captura todos os registros da tabela e armazena no objeto data
        data = inst_consulta.fetchall()

        # Insere os valores da tabela na Lista
        for dt in data:
            lista_sugestoes.append(dt)

        # ordena a lista
        lista_sugestoes = sorted(lista_sugestoes)

        # Gera um DataFrame com os dados da lista utilizando o Pandas
        dados_df = pd.DataFrame.from_records(
            lista_sugestoes, columns=['id_sugestao', 'categoria', 'mensagem_ia', 'dt_sugestao'], index='id_sugestao')
        
        # Verifica se não há registro através do dataframe
        if dados_df.empty:
            return None
        else:
            return dados_df 
    except Exception as e:
        print(f"Erro na transação do BD: {e}")
        return None

# ================= Gravar em JSON =================
def gravar_json(nome_arquivo: str, dados: dict) -> bool:
    try:
        with open(nome_arquivo, "x", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
        return True
    except FileExistsError:
        print("Arquivo com este nome já existe.")
        return False
    except:
        print("Erro ao gravar o arquivo JSON.")
        return False
    
def nome_arquivo_json(tipo: str) -> str | None:
    nm_arquivo = input("Digite o nome do arquivo (sem extensão) ou 0 para cancelar: ").strip()
    if nm_arquivo == "0":
        return None
    return f"{nm_arquivo}.json"

def gravar_df_json(df: pd.DataFrame = None):
    nm_arquivo = nome_arquivo_json()
    if nm_arquivo is None:
        return
    if df is None:
        print("Nenhum registro encontrado para salvar.")
        return
    dados = trasformar_df_dicionario(df)
    gravado = gravar_json(nm_arquivo, dados)
    if gravado:
        print("Histórico salvo com sucesso!")   
    
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


# ================= Finalizar Código =================
def sair():
    limpar_tela()
    global conexao
    conexao = False
    print("Finalizando o código...")

# ================= Conexão =================
try:
    conn = oracledb.connect(user="rm562979", password="251004", dsn="oracle.fiap.com.br:1521/ORCL")
    inst_cadastro = conn.cursor()
    inst_consulta = conn.cursor()
    inst_alteracao = conn.cursor()
    inst_exclusao = conn.cursor()
except Exception as e:
    print(f"Erro na conexão: {e}")
    conexao = False
else:
    conexao = True
    
while conexao:
    logado = login()
    if logado:
        menu()

# TODO Fazer grava JSON funcionar corretamente com os dataframes, atualmente está com erro na função trasformar_df_dicionario e fazer a mensagem da IA funcionar corretamente.