from agents import Agent, Runner
import os
import dotenv

dotenv.load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

model = "gpt-5-mini"

agent = Agent(name="Assistant", instructions="You are a helpful assistant", model=model)

result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
print(result.final_output)

# Code within the code,
# Functions calling themselves,
# Infinite loop's dance.