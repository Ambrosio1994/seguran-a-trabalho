import pandas as pd
import os
from typing_extensions import Annotated
from agents import function_tool
"""
Esta função adiciona novos registros de riscos ocupacionais a um arquivo CSV existente. 
Ela é decorada com @function_tool da OpenAI para ser usada como uma ferramenta dentro de aplicações 
que utilizam esse framework.
"""
# Função para adicionar dados ao DataFrame
@function_tool
def add_data_to_df(
    risco: Annotated[str, "Potencial de dano de cada risco"],
    fonte_geradora: Annotated[str, "Fonte geradora do risco"],
    agente: Annotated[str, "Qual tipo do risco (ex: Físico, Químico, Biológico, Acidente, Ergonômico, Psicossociais, etc.)"],
    medidas_de_controle: Annotated[str, "Ações preventivas ou corretivas para mitigar o risco"],
    severidade: Annotated[str, "Nível de gravidade do risco (ex: IRREVERSÍVEL SEVERO, LEVE, REVERSÍVEL SEVERO, INCAPACITANTE OU FATAL, ALTAMENTE CATASTRÓFICO)."],
    probabilidade: Annotated[str, "Chance de ocorrência do risco (ex: IMPROVÁVEL, POSSÍVEL, MUITO IMPROVÁVEL, MUITO PROVÁVEL, PROVÁVEL)."],
    nivel_de_risco: Annotated[str, "Classificação geral resultante da combinação de severidade e probabilidade (ex: RISCO MÉDIO, RISCO BAIXO, RISCO IRRELEVANTE, RISCO ALTO, RISCO CRÍTICO)"]
    ) -> str:
    """Adiciona dados ao dataframe"""
    
    # Validar se algum campo está vazio
    campos = {
        "risco": risco,
        "fonte_geradora": fonte_geradora,
        "agente": agente,
        "medidas_de_controle": medidas_de_controle,
        "severidade": severidade,
        "probabilidade": probabilidade,
        "nivel_de_risco": nivel_de_risco
    }
    
    # Validações adicionais para garantir que os valores estão dentro de opções válidas
    opcoes_validas = {
        "agente": ["Físico", "Químico", "Biológico", "Acidente", "Ergonômico", "Psicossociais"],
        "severidade": ["IRREVERSÍVEL SEVERO", "LEVE", "REVERSÍVEL SEVERO", "INCAPACITANTE OU FATAL", "ALTAMENTE CATASTRÓFICO"],
        "probabilidade": ["IMPROVÁVEL", "POSSÍVEL", "MUITO IMPROVÁVEL", "MUITO PROVÁVEL", "PROVÁVEL"],
        "nivel_de_risco": ["RISCO MÉDIO", "RISCO BAIXO", "RISCO IRRELEVANTE", "RISCO ALTO", "RISCO CRÍTICO"]
    }
    
    for campo, opcoes in opcoes_validas.items():
        valor = campos[campo].upper()
        # Verificação flexível para permitir variações comuns
        if not any(opcao.upper() in valor for opcao in opcoes):
            return f"Erro: O valor '{campos[campo]}' para o campo '{campo}' não é válido. Valores aceitos: {', '.join(opcoes)}."
    
    path_data = os.path.join(os.path.dirname(__file__), "data.csv")

    # Ler o CSV existente com tratamento de erros de codificação
    df = pd.read_csv(path_data, encoding='utf-8', on_bad_lines='skip')
    
    # Limpar linhas inválidas (com menos campos preenchidos que o esperado)
    campos_esperados = ["Risco", "Fonte_Geradora", "Agente", "Medidas_de_Controle", 
                        "Severidade", "Probabilidade", "Nivel_de_Risco"]
    
    # Identificar linhas com dados incompletos
    linhas_validas = df.notna().sum(axis=1) >= len(campos_esperados) - 1 
    if not all(linhas_validas):
        df = df[linhas_validas]
        # Salvar o dataframe limpo
        df.to_csv(path_data, index=False, encoding='utf-8')
        

        df = pd.read_csv(path_data, encoding='latin1', on_bad_lines='skip')
        # Aplicar limpeza também neste caso
        linhas_validas = df.notna().sum(axis=1) >= len(campos_esperados) - 1
        if not all(linhas_validas):
            df = df[linhas_validas]
            df.to_csv(path_data, index=False, encoding='utf-8')
        # Se ainda falhar, criar um dataframe vazio com as colunas necessárias
        df = pd.DataFrame(columns=["Risco", "Fonte_Geradora", "Agente", "Medidas_de_Controle", 
                                  "Severidade", "Probabilidade", "Nivel_de_Risco"])

    # Criar um dicionário com os dados
    new_data = {
        "Risco": risco,
        "Fonte_Geradora": fonte_geradora,
        "Agente": agente,
        "Medidas_de_Controle": medidas_de_controle,
        "Severidade": severidade,
        "Probabilidade": probabilidade,
        "Nivel_de_Risco": nivel_de_risco
    }
    
    # Adicionar os dados ao dataframe
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)

    # Salvar o dataframe
    df.to_csv(path_data, index=False, encoding='utf-8')
    return f"Dados adicionados com sucesso! {new_data}"

@function_tool
def head_df():
    """Retorna as primeiras linhas do dataframe"""
    path_data = os.path.join(os.path.dirname(__file__), "data.csv")
    df = pd.read_csv(path_data, encoding='utf-8', on_bad_lines='skip')
    return df.head()

@function_tool
def tail_df():
    """Retorna as últimas linhas do dataframe"""
    path_data = os.path.join(os.path.dirname(__file__), "data.csv")
    df = pd.read_csv(path_data, encoding='utf-8', on_bad_lines='skip')
    return df.tail()

tools = [add_data_to_df, head_df, tail_df]