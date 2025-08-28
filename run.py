import asyncio
from pyexpat.errors import messages
from src.utils.chat import get_response

async def main():
    messages = []
    while True:
        message = input("User: ")
        if message == "exit":
            break
        messages.append({"role": "user", "content": message})
        result = await get_response(messages)
        print(f"Agent: {result.final_output}")
        messages = result.to_input_list()

asyncio.run(main())
