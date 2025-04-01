from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from tools import tools
from prompts import sys_messsage
from analyze_video import analyze_video
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro-exp-03-25",
    google_api_key=os.getenv("GEMINI_API_KEY")
    )

llm_with_tools = llm.bind_tools(tools)

# example
video_file_name = "C:\\Users\\diham\\segurança-trabalho\\project\\video.mp4"

def analyze_node(state: MessagesState):
    video = state["messages"]
    return {"messages": analyze_video(video)}

def call_llm(state: MessagesState):
    return {"messages": [llm_with_tools.invoke([sys_messsage] + state["messages"])]}

builder = StateGraph(MessagesState)

builder.add_node("call_llm", call_llm)
builder.add_node("tools", ToolNode(tools=tools))
builder.add_node("analyze_node", analyze_node)

builder.add_edge(START, "analyze_node")
builder.add_edge("analyze_node", "call_llm")
builder.add_conditional_edges("call_llm", tools_condition)
builder.add_edge("tools", END)

graph = builder.compile()

if __name__ == "__main__":
    output = graph.invoke({"messages": [video_file_name]})
    for message in output["messages"]:
        message.pretty_print()