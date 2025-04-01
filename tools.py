from langchain_core.tools import tool
import pandas as pd

# criar dataframe 


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
    path_data = "C:\\Users\\diham\\segurança-trabalho\\project\\data.csv"
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

    df.to_csv("./data.csv", index=False)

    # Salvar o dataframe
    return "Dados adicionados com sucesso!"

tools = [add_data_to_df]