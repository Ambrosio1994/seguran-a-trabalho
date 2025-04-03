from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from trustcall import create_extractor
import uuid
from tools import add_data_to_df
from prompts import PROMPT_SYS_MESSAGE
from analyze_video import analyze_video

import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GEMINI_API_KEY")
    )

# Example
video_file_name = os.path.join(os.path.dirname(__file__), "video.mp4")

def analyze_node(state: MessagesState):
    """Analisa o vídeo enviado e retorna o resultado da análise como uma mensagem AI"""
    # Obtém o caminho do arquivo de vídeo a partir da mensagem do usuário
    video_path = state["messages"]
    
    # Chama a função de análise de vídeo
    video_analysis = analyze_video(video_path)
    
    # Retorna o resultado como uma mensagem AI
    return {"messages": [video_analysis]}

def assistant(state: MessagesState):
    """Processa a mensagem de análise e extrai informações usando o Gemini"""
    # Configura o modelo LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"))
    
    # Cria o extrator de chamadas de ferramentas
    trustcall_extractor = create_extractor(
        llm=llm,
        tools=[add_data_to_df],
        tool_choice="add_data_to_df")
    
    # Invoca o extrator e retorna o resultado
    result = trustcall_extractor.invoke(
        {"messages": [SystemMessage(content=PROMPT_SYS_MESSAGE)]+state["messages"]})
    
    return {"messages": result["messages"]}

def graph_builder():
    builder = StateGraph(MessagesState)

    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(tools=[add_data_to_df]))
    builder.add_node("analyze_node", analyze_node)

    builder.add_edge(START, "analyze_node")
    builder.add_edge("analyze_node", "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")
    builder.add_edge("assistant", END)

    return builder.compile(checkpointer=MemorySaver())

if __name__ == "__main__":
    id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": id, "user_id": id}}
    graph = graph_builder()
    input = HumanMessage(content=video_file_name)
    for chunk in graph.stream({"messages": [input]}, config, stream_mode="values"):
        chunk["messages"][-1].pretty_print()
