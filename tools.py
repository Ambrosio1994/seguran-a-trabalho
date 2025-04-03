from langchain_core.tools import tool
import pandas as pd
import os
"""
Esta função adiciona novos registros de riscos ocupacionais a um arquivo CSV existente. 
Ela é decorada com @tool da LangChain para ser usada como uma ferramenta dentro de aplicações 
que utilizam esse framework.
"""
# Função para adicionar dados ao DataFrame
@tool
def add_data_to_df(
    risco: str,
    fonte_geradora: str,
    agente: str,
    medidas_de_controle: str,
    severidade: str,
    probabilidade: str,
    nivel_de_risco: str
    ) -> str:
    """Adiciona dados ao dataframe
      Parameters:
      risco (str): Potencial de dano de cada risco
      fonte_geradora (str): Origem ou fonte que gera o risco no ambiente, qual material ou produto que está gerando o risco.
      agente (str): Qual tipo do risco (ex: Físico, Químico, Biológico, Acidente, Ergonômico, Psicossociais, etc.).
      medidas_de_controle (str): Ações preventivas ou corretivas para mitigar o risco.
      severidade (str): Nível de gravidade do risco (ex: IRREVERSÍVEL SEVERO, LEVE, REVERSÍVEL SEVERO, INCAPACITANTE OU FATAL, ALTAMENTE CATASTRÓFICO).
      probabilidade (str): Chance de ocorrência do risco (ex: IMPROVÁVEL, POSSÍVEL, MUITO IMPROVÁVEL, MUITO PROVÁVEL, PROVÁVEL).
      nivel_de_risco (str): Classificação geral resultante da combinação de severidade e probabilidade (ex: RISCO MÉDIO, RISCO BAIXO, RISCO IRRELEVANTE, RISCO ALTO, RISCO CRÍTICO)
    """
    path_data = os.path.join(os.path.dirname(__file__), "data.csv")

    # Ler o CSV existente
    df = pd.read_csv(path_data)

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
    df.to_csv(path_data, index=False)

    return f"Dados adicionados com sucesso! {new_data}"