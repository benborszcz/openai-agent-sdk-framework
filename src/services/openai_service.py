"""
src/services/openai.py
Code for interacting with OpenAI API
"""

import os
import json
from typing import (
    Dict,
    List,
    TypeVar,
    Type,
    Union,
)
from pydantic import BaseModel
from openai import AsyncOpenAI
import dotenv

T = TypeVar("T", bound=BaseModel)

# Using dotenv to load environment variables
dotenv.load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=api_key)


async def get_chat_completion(
    messages: List[Dict[str, str]], model: str = "gpt-5-nano", **kwargs
) -> str:
    """Get a plain-text chat completion response from OpenAI."""

    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        **kwargs,
    )

    try:
        message = response.choices[0].message
        if not message or message.content is None:
            raise ValueError("OpenAI response contained no message content")
        # In the unlikely case content is a list of parts, join them.
        if isinstance(message.content, list):
            return "".join(
                part.get("text", "")
                for part in message.content
                if isinstance(part, dict)
            )
        return message.content
    except IndexError as e:
        raise ValueError("OpenAI response contained no choices") from e
    except Exception as e:
        raise ValueError(f"Failed to extract chat completion content: {e}") from e


async def get_structured_chat_completion(
    messages: List[Dict[str, str]],
    output_schema: Type[T],
    model: str = "gpt-5-nano",
    **kwargs,
) -> T:
    """
    Get a structured output from OpenAI based on a Pydantic model

    Args:
        messages: List of message dictionaries
        output_schema: Pydantic model class defining the expected output structure
        model: OpenAI model to use
        temperature: Sampling temperature
        api_key: Optional API key to use

    Returns:
        Instance of the provided Pydantic model
    """
    # Use function calling for more reliable JSON responses
    response = await client.beta.chat.completions.parse(
        model=model,
        messages=messages,
        response_format=output_schema,
        seed=420,
        **kwargs,
    )

    try:
        return response.choices[0].message.parsed
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse response JSON: {e}") from e
    except Exception as e:
        raise ValueError(f"Failed to validate response against schema: {e}") from e


async def get_embedding(
    input_text: Union[str, List[str]],
    model: str = "text-embedding-3-large",
    **kwargs,
) -> Union[List[float], List[List[float]]]:
    """Generate embeddings for the provided text."""

    response = await client.embeddings.create(
        model=model,
        input=input_text,
        **kwargs,
    )

    embeddings = [item.embedding for item in response.data]

    if isinstance(input_text, str):
        if not embeddings:
            raise ValueError("OpenAI embedding response contained no data")
        return embeddings[0]

    return embeddings


async def get_embeddings(
    input_texts: List[str],
    model: str = "text-embedding-3-large",
    **kwargs,
) -> List[List[float]]:
    """Generate embeddings for a list of texts."""

    response = await client.embeddings.create(
        model=model,
        input=input_texts,
        **kwargs,
    )

    embeddings = [item.embedding for item in response.data]

    if len(embeddings) != len(input_texts):
        raise ValueError("Mismatch between number of inputs and embeddings returned")

    return embeddings
