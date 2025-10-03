from src.utils.chat import get_response

async def main() -> None:
    messages = []
    while True:
        try:
            message = input("User: ")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if message.strip().lower() == "exit":
            break
        messages.append({"role": "user", "content": message})
        try:
            result = await get_response(messages)
        except Exception as e:
            print(f"Error: {e}")
            continue
        print(f"Agent: {getattr(result, 'final_output', '')}")
        messages = result.to_input_list()
