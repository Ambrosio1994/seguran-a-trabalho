from agents import Agent, Runner
from tools import add_data_to_df
from prompts import PROMPT_SYS_MESSAGE
from analyze_video import analyze_video
import os
import asyncio

from dotenv import load_dotenv

load_dotenv()

agent = Agent(
    name="Assistant",
    instructions=PROMPT_SYS_MESSAGE,
    tools=[add_data_to_df],
    )

async def main():
    path_video = os.path.join(os.path.dirname(__file__), "video.mp4")
    analysis = analyze_video(path_video)
    print(analysis)
    result = await Runner.run(agent, analysis)
    return result

if __name__ == "__main__":
    asyncio.run(main())
