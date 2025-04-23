from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from trustcall import create_extractor
import streamlit as st
from analyze_video import analyze_video
from tools import add_data_to_df
from prompts import PROMPT_SYS_MESSAGE

import os
from dotenv import load_dotenv

load_dotenv()

# MODULO NÃO SERA MAIS UTILIZADO
# Arquivo main.py irá chamar o analyze_video
video_file_name = os.path.join(os.path.dirname(__file__), "video.mp4")

def analyze_node(state: MessagesState):
    """Analisa o vídeo enviado"""
    video_path = state["messages"][-1].content  
    
    # Chama a função de análise de vídeo
    video_analysis = analyze_video(video_path)
    st.success("Vídeo analisado com sucesso!")
    
    # Retorna o resultado
    return {"messages": [video_analysis]}

def assistant(state: MessagesState):
    """Processa a mensagem de análise e extrai informações"""

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"))
    
    trustcall_extractor = create_extractor( 
        llm=llm,
        tools=[add_data_to_df],
        tool_choice="add_data_to_df")
    result = trustcall_extractor.invoke(
        {"messages": [SystemMessage(content=PROMPT_SYS_MESSAGE)]+state["messages"]})
    
    return {"messages": result["messages"]} 

def should_continue_after_tools(state: MessagesState):
    """Decide se termina ou volta para o assistente após a execução das ferramentas."""
    last_message = state["messages"][-1]
    error_message = "Registro já existe no inventário de riscos. Dados não adicionados."
    if last_message.content == error_message:
        return END 
    else:
        return "assistant"

def graph_builder():
    builder = StateGraph(MessagesState)

    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(tools=[add_data_to_df]))
    builder.add_node("analyze_node", analyze_node)

    builder.add_edge(START, "analyze_node")
    builder.add_edge("analyze_node", "assistant")
    builder.add_edge("assistant", "tools")

    builder.add_conditional_edges("tools", should_continue_after_tools,
        {"assistant": "assistant", END: END}
    )

    return builder.compile(checkpointer=MemorySaver())