from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from tools import tools
from prompts import PROMPT_SYS_MESSAGE
from analyze_video import analyze_video

import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GEMINI_API_KEY")
    )

llm_with_tools = llm.bind_tools(tools)

# Example
video_file_name = os.path.join(os.path.dirname(__file__), "video.mp4")

def analyze_node(state: MessagesState):
    video = state["messages"]
    return {"messages": analyze_video(video)}

def assistant(state: MessagesState):
    return {"messages": [llm_with_tools.invoke([PROMPT_SYS_MESSAGE] + state["messages"])]}

def graph_builder():
    builder = StateGraph(MessagesState)

    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(tools=tools))
    builder.add_node("analyze_node", analyze_node)

    builder.add_edge(START, "analyze_node")
    builder.add_edge("analyze_node", "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")
    builder.add_edge("assistant", END)

    return builder.compile(checkpointer=MemorySaver())