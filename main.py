from agents import Agent, Runner
from tools import add_data_to_df
from analyze_video import analyze_video
from prompts import PROMPT_SYS_MESSAGE
import os
import asyncio

from dotenv import load_dotenv

load_dotenv()

agent_csv = Agent(
    name="assistant_csv",
    instructions=PROMPT_SYS_MESSAGE,
    tools=[add_data_to_df],
    )

async def assistant(path_video):
    analysis = analyze_video(path_video)
    result = await Runner.run(agent_csv, analysis)
    return result

if __name__ == "__main__":
    path_video = os.path.join(os.path.dirname(__file__), "video.mp4")
    result = asyncio.run(assistant(path_video))
    print(result)