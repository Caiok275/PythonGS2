-- DROP TABLES (ordem reversa das dependências)
DROP TABLE T_ABTG_SUGESTAO_IA CASCADE CONSTRAINTS;
DROP TABLE T_ABTG_ANALISE_ESTRESSE CASCADE CONSTRAINTS;
DROP TABLE T_ABTG_REGISTRO_DIARIO CASCADE CONSTRAINTS;
DROP TABLE T_ABTG_FUNCIONARIO CASCADE CONSTRAINTS;

-- TABELA FUNCIONARIO
CREATE TABLE T_ABTG_FUNCIONARIO (
    id_funcionario INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nm_funcionario VARCHAR2(80) NOT NULL,
    idade NUMBER NOT NULL,
    modelo_trabalho NUMBER NOT NULL,
    setor VARCHAR2(50) NOT NULL,
    CONSTRAINT ck_idade CHECK (idade BETWEEN 18 AND 70),
    CONSTRAINT ck_modelo CHECK (modelo_trabalho IN (0,1,2)) -- onde 0 = presencial, 1 = remoto e 2 = hibrido
);

-- TABELA REGISTRO
CREATE TABLE T_ABTG_REGISTRO_DIARIO (
    id_registro INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_funcionario INT NOT NULL,
    dt_registro DATE NOT NULL,
    sono NUMBER NOT NULL,
    humor NUMBER NOT NULL,
    tensao NUMBER NOT NULL,
    energia NUMBER NOT NULL,
    motivacao NUMBER NOT NULL,
    horas_trabalho NUMBER NOT NULL,
    pausas_diarias NUMBER NOT NULL,
    exercicio_semana NUMBER NOT NULL,
    CONSTRAINT fk_registro_funcionario FOREIGN KEY (id_funcionario)
        REFERENCES T_ABTG_FUNCIONARIO(id_funcionario),
    CONSTRAINT ck_sono CHECK (sono BETWEEN 1 AND 5),
    CONSTRAINT ck_humor CHECK (humor BETWEEN 1 AND 5),
    CONSTRAINT ck_tensao CHECK (tensao BETWEEN 1 AND 5),
    CONSTRAINT ck_energia CHECK (energia BETWEEN 1 AND 5),
    CONSTRAINT ck_motivacao CHECK (motivacao BETWEEN 1 AND 5),
    CONSTRAINT ck_horas_trabalho CHECK (horas_trabalho BETWEEN 4 AND 10),
    CONSTRAINT ck_pausas CHECK (pausas_diarias BETWEEN 0 AND 5),
    CONSTRAINT ck_exercicio CHECK (exercicio_semana BETWEEN 0 AND 7)  
);


-- TABELA ESTRESSE
CREATE TABLE T_ABTG_ANALISE_ESTRESSE (
    id_analise INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_registro INT UNIQUE NOT NULL,
    nivel_estresse NUMBER NOT NULL,
    categoria_estresse VARCHAR2(20) NOT NULL,
    dt_analise DATE NOT NULL,
    CONSTRAINT fk_analise_registro FOREIGN KEY (id_registro)
        REFERENCES T_ABTG_REGISTRO_DIARIO(id_registro),
    CONSTRAINT ck_estresse CHECK (nivel_estresse BETWEEN 0 AND 10),
    CONSTRAINT ck_categoria_estresse CHECK (categoria_estresse IN ('Baixo','Moderado','Alto'))
);

-- TABELA SUGESTAO IA
CREATE TABLE T_ABTG_SUGESTAO_IA (
    id_sugestao INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_analise INT NOT NULL,
    categoria VARCHAR(30) NOT NULL,
    mensagem_ia VARCHAR(300) NOT NULL,
    dt_sugestao DATE NOT NULL,
    CONSTRAINT fk_sugestao_analise FOREIGN KEY (id_analise)
        REFERENCES T_ABTG_ANALISE_ESTRESSE(id_analise)
);