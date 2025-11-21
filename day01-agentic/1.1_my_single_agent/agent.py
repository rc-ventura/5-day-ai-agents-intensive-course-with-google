import asyncio

from google.adk.agents.llm_agent import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.genai import types

from dotenv import load_dotenv

load_dotenv()


retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1, # Initial delay before first retry (in seconds)
    http_status_codes=[429, 500, 503, 504] # Retry on these HTTP errors
)


root_agent = Agent(
    name= "helpful_assistant",
    model=Gemini(
        model='gemini-2.5-flash',
        retry_options=retry_config,
    ),
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
    tools=[google_search],
)

if __name__ == "__main__":
   
   
    print("✅ Root Agent defined.")

    runner = InMemoryRunner(agent=root_agent)

    print("✅ Runner created.")

    response = asyncio.run(runner.run_debug("What is the meaning of life?"))

    print("✅ Response:", response)

