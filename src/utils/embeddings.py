import asyncio
from pydantic import BaseModel
from openai import OpenAI
from openai import AsyncOpenAI
import os

from src.config import config


openai_client: OpenAI | None = None
async_openai_client: AsyncOpenAI | None = None

default_embedding_model = "text-embedding-3-small"

### Helper functions for OpenAI embeddings ###

def get_openai_client() -> OpenAI:
    """
    Create and return an OpenAI client instance.
    This function is used to initialize the OpenAI client with the API key.
    """
    global openai_client
    if openai_client is None:
        openai_client = OpenAI(api_key=config.openai_api_key if config.openai_api_key else os.getenv("OPENAI_API_KEY"))
    return openai_client

async def get_async_openai_client() -> AsyncOpenAI:
    """
    Create and return an asynchronous OpenAI client instance.
    This function is used to initialize the OpenAI client with the API key.
    """
    global async_openai_client
    if async_openai_client is None:
        async_openai_client = AsyncOpenAI(api_key=config.openai_api_key if config.openai_api_key else os.getenv("OPENAI_API_KEY"))
    return async_openai_client


### Exported functions ###
def get_embedding(text: str, model: str = default_embedding_model) -> list[float]:
    """
    Get the embedding for a given text using OpenAI's API.

    Args:
        text (str): The text to embed.
        model (str): The model to use for embedding. Defaults to default_embedding_model.

    Returns:
        list[float]: The embedding vector as a list of floats.
    """
    client = get_openai_client()
    response = client.embeddings.create(
        input=text,
        model=model
    )
    return response.data[0].embedding

def get_embeddings(texts: list[str], model: str = default_embedding_model) -> list[list[float]]:
    """
    Get embeddings for a list of texts using OpenAI's API.
    Args:
        texts (list[str]): The list of texts to embed.
        model (str): The model to use for embedding. Defaults to default_embedding_model.
    Returns:
        list[list[float]]: A list of embedding vectors, each as a list of floats.
    """
    client = get_openai_client()
    response = client.embeddings.create(
        input=texts,
        model=model
    )
    return [data.embedding for data in response.data]

async def async_get_embedding(text: str, model: str = default_embedding_model) -> list[float]:
    """
    Asynchronously get the embedding for a given text using OpenAI's API.

    Args:
        text (str): The text to embed.
        model (str): The model to use for embedding. Defaults to default_embedding_model.

    Returns:
        list[float]: The embedding vector as a list of floats.
    """
    client = await get_async_openai_client()
    response = await client.embeddings.create(
        input=text,
        model=model
    )
    return response.data[0].embedding
async def async_get_embeddings(texts: list[str], model: str = default_embedding_model) -> list[list[float]]:
    """
    Asynchronously get embeddings for a list of texts using OpenAI's API.
    Args:
        texts (list[str]): The list of texts to embed.
        model (str): The model to use for embedding. Defaults to default_embedding_model.
    Returns:
        list[list[float]]: A list of embedding vectors, each as a list of floats.
    """
    client = await get_async_openai_client()
    response = await client.embeddings.create(
        input=texts,
        model=model
    )
    return [data.embedding for data in response.data]

class EmbeddingChunk(BaseModel):
    chunk: str
    embedding: list[float]

def chunk_and_embed(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 100,
    model: str = default_embedding_model
) -> list[EmbeddingChunk]:
    """
    Chunk a text and get embeddings for each chunk.

    Args:
        text (str): The text to chunk and embed.
        chunk_size (int): The size of each chunk. Defaults to 1000.
        overlap (int): The number of overlapping characters between chunks. Defaults to 100.
        model (str): The model to use for embedding. Defaults to default_embedding_model.

    Returns:
        list[dict]: A list of dictionaries containing the chunk and its embedding.
    """
    # Chunk the text
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    
    # Get embeddings for each chunk
    embeddings = get_embeddings(chunks, model=model)
    
    return [EmbeddingChunk(chunk=chunk, embedding=embedding) for chunk, embedding in zip(chunks, embeddings)]


async def async_chunk_and_embed(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 100,
    model: str = default_embedding_model
) -> list[EmbeddingChunk]:
    """
    Asynchronously chunk a text and get embeddings for each chunk.

    Args:
        text (str): The text to chunk and embed.
        chunk_size (int): The size of each chunk. Defaults to 1000.
        overlap (int): The number of overlapping characters between chunks. Defaults to 100.
        model (str): The model to use for embedding. Defaults to default_embedding_model.

    Returns:
        list[dict]: A list of dictionaries containing the chunk and its embedding.
    """

    # Chunk the text
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    
    # Get embeddings for each chunk
    embeddings = await async_get_embeddings(chunks, model=model)
    
    return [EmbeddingChunk(chunk=chunk, embedding=embedding) for chunk, embedding in zip(chunks, embeddings)]

async def async_chunk_and_embed_list(
    texts: list[str],
    chunk_size: int = 1000,
    overlap: int = 100,
    model: str = default_embedding_model
) -> list[list[EmbeddingChunk]]:
    """
    Asynchronously chunk a list of texts and get embeddings for each chunk.

    Args:
        texts (list[str]): The list of texts to chunk and embed.
        chunk_size (int): The size of each chunk. Defaults to 1000.
        overlap (int): The number of overlapping characters between chunks. Defaults to 100.
        model (str): The model to use for embedding. Defaults to default_embedding_model.

    Returns:
        list[list[dict]]: A list of lists, each containing dictionaries with the chunk and its embedding.
    """
    return await asyncio.gather(
        *(async_chunk_and_embed(text, chunk_size, overlap, model) for text in texts)
    )