import streamlit as st
import pandas as pd
import os
import tempfile
from main import assistant
import asyncio

# Constantes
DATA_CSV_PATH = os.path.join(os.path.dirname(__file__), "data.csv")
ALLOWED_VIDEO_FORMATS = ["mp4", "mov", "avi", "mkv"]

# seta o tema e layout da página
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
                
                with st.spinner("Analisando o vídeo... Isso pode levar alguns minutos."):
                    result = asyncio.run(assistant(temp_video_path))
                    if result:
                        st.success("Inventário atualizado com sucesso!")
                    else:
                        st.error("Erro ao atualizar o inventário")

                st.subheader("📊 Inventário de Riscos Atualizado")

            # Recarrega o inventário de riscos após a análise
            updated_df = load_risk_inventory()
            if updated_df is not None:
                st.dataframe(updated_df)
            else:
                st.warning("Não foi possível recarregar o inventário de riscos atualizado.")
            