import streamlit as st
import pandas as pd
import os
import tempfile
from uuid import uuid4
from graph import graph_builder 

# Constantes
DATA_CSV_PATH = os.path.join(os.path.dirname(__file__), "data.csv")
ALLOWED_VIDEO_FORMATS = ["mp4", "mov", "avi", "mkv"]

#seta o tema e layout da página
st.set_page_config(page_title="Análise de Risco em Vídeo", layout="wide")
st.title("🤖 Análise de Risco Ocupacional em Vídeo")
st.write("""
    Carregue um vídeo para identificar riscos ocupacionais (físicos, químicos, biológicos, 
    de acidentes, ergonômicos e psicossociais) e gerar um inventário de riscos.
""")

st.title("Inventário de Riscos Atual")

def load_risk_inventory():
    df = pd.read_csv(DATA_CSV_PATH)
    if df.empty:
        st.warning("O inventário de riscos está vazio.")
        return None
    return df

df_initial = load_risk_inventory()
if df_initial is not None:
    st.dataframe(df_initial)

# envia o arquivo
uploaded_files = st.sidebar.file_uploader(
    "Escolha um arquivo de vídeo", 
    type=ALLOWED_VIDEO_FORMATS, 
    help="Faça o upload do vídeo que deseja analisar.",
    accept_multiple_files=True)

if not uploaded_files:
    st.info("👈 Aguardando o upload de um arquivo de vídeo.")
else:
    for uploaded_file in uploaded_files:
        st.sidebar.video(uploaded_file)
        if st.button("Analisar Vídeo", key=f"analyze_button_{uploaded_file.name}"):
            
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_video_path = os.path.join(temp_dir, uploaded_file.name)
                
                with open(temp_video_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                st.info(f"Vídeo salvo temporariamente em: {temp_video_path}")
                with st.spinner("Analisando o vídeo... Isso pode levar alguns minutos."):
                    thread_id = str(uuid4())
                    config = {"configurable": {"thread_id": thread_id, "user_id": thread_id}}
                    
                    graph = graph_builder()
                    # A execução do grafo pode chamar ferramentas internas que atualizam o data.csv
                    final_state = None
                    try:
                        # Iterar sobre os resultados do stream para obter o estado final
                        # O stream_mode="values" retorna cada estado atualizado.
                        # O valor final retornado por invoke nesse modo pode não ser o último estado completo.
                        # Uma abordagem mais robusta seria capturar o último valor do stream.
                        # Para simplificar por agora, vamos assumir que a invoke retorna o estado final se não houver erro.
                        # TODO: Implementar um tratamento mais robusto para capturar o último estado do stream.
                        result_stream = graph.stream({"messages": [temp_video_path]}, config, stream_mode="values")
                        for value in result_stream:
                             final_state = value # Keep track of the latest state

                        if final_state and "messages" in final_state:
                            # Exibe a última mensagem do assistente (resultado da análise)
                            last_message = final_state["messages"][-1]
                            if hasattr(last_message, 'content'):
                                st.subheader("📝 Resumo da Análise:")
                                st.markdown(last_message.content)
                            else:
                                # Caso a última mensagem não seja um objeto esperado (ex: AIMessage)
                                st.write("Resultado da análise:", last_message)

                            st.subheader("📊 Inventário de Riscos Atualizado")
                        else:
                             st.warning("A análise foi concluída, mas não retornou um estado final esperado.")

                    except Exception as e:
                        st.error(f"Erro ao analisar o vídeo: {e}")
                        st.stop()

            # Recarrega o inventário de riscos após a análise (que pode ter modificado o CSV)
            updated_df = load_risk_inventory()
            if updated_df is not None:
                st.dataframe(updated_df)
            else:
                st.warning("Não foi possível recarregar o inventário de riscos atualizado.")
            