from agents import Agent, Runner
from dotenv import load_dotenv

from tools import tools
from analyze_video import analyze_video
from prompts import PROMPT_SYS_MESSAGE

load_dotenv()

agent_csv = Agent(
    name="assistant_csv",
    model="gpt-4o",
    instructions=PROMPT_SYS_MESSAGE,
    tools=tools,
    )

async def assistant(path_video):
    analysis = analyze_video(path_video)
    result = await Runner.run(agent_csv, analysis)
    return result