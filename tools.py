from langchain_core.tools import tool
import pandas as pd
import os

@tool
def add_data_to_df(
    risco: str,
    fonte_geradora:str,
    agente: str,
    medidas_de_controle: str,
    severidade: str,
    probabilidade: str,
    nivel_de_Risco: str
    ) -> str:
    
    """Adiciona dados ao dataframe"""
    path_data = os.path.join(os.path.dirname(__file__), "data.csv")
    
    # Specify encoding when reading the CSV
    df = pd.read_csv(path_data)

    # Criar um dicionário com os dados
    new_data = {
        "Risco": risco,
        "Fonte_Geradora": fonte_geradora,
        "Agente": agente,
        "Medidas_de_Controle": medidas_de_controle,
        "Severidade": severidade,
        "Probabilidade": probabilidade,
        "Nivel_de_Risco": nivel_de_Risco
    }

    # Adicionar os dados ao dataframe
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)

    # Salvar o dataframe
    df.to_csv(path_data, index=False)

    # Salvar o dataframe
    return "Dados adicionados com sucesso!"

tools = [add_data_to_df]