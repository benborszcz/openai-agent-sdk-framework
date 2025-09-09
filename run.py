"""
Run the FastAPI app using uvicorn.
"""

if __name__ == "__main__":
	import uvicorn

	# Use the src.api:app ASGI app. Host and port match typical local dev defaults.
	uvicorn.run("src.api:app", host="127.0.0.1", port=8000, reload=True)
