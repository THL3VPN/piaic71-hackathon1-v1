"""
LLM service for the RAG system that supports multiple providers.
"""
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate a response from the LLM."""
        pass


class OpenAILLMProvider(LLMProvider):
    """OpenAI LLM provider."""

    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        try:
            import httpx
            from openai import OpenAI
        except ImportError as e:
            if "openai" in str(e):
                raise ImportError("Please install openai: pip install openai")
            else:
                raise e

        # Use provided API key or fall back to environment variable
        actual_api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not actual_api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        # Create an HTTP client without proxy settings to avoid the 'proxies' issue
        http_client = httpx.Client(
            timeout=60.0,  # Set appropriate timeout
        )

        # Initialize OpenAI client with the custom HTTP client
        self.client = OpenAI(
            api_key=actual_api_key,
            http_client=http_client
        )
        self.model = model

    def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate response using OpenAI API."""
        system_message = (
            "You are a helpful assistant that answers questions based only on the provided context. "
            "If the context doesn't contain information to answer the question, say so explicitly. "
            "Always provide accurate information based solely on the context provided."
        )

        if context:
            user_message = f"Context: {context}\n\nQuestion: {prompt}"
        else:
            user_message = prompt

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,
            max_tokens=1000
        )

        return response.choices[0].message.content


class AnthropicLLMProvider(LLMProvider):
    """Anthropic LLM provider."""

    def __init__(self, api_key: str = None, model: str = "claude-3-haiku-20240307"):
        try:
            import anthropic
        except ImportError:
            raise ImportError("Please install anthropic: pip install anthropic")

        self.client = anthropic.Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.model = model

    def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate response using Anthropic API."""
        system_message = (
            "You are a helpful assistant that answers questions based only on the provided context. "
            "If the context doesn't contain information to answer the question, say so explicitly. "
            "Always provide accurate information based solely on the context provided."
        )

        if context:
            user_message = f"Context: {context}\n\nQuestion: {prompt}"
        else:
            user_message = prompt

        response = self.client.messages.create(
            model=self.model,
            system=system_message,
            messages=[{"role": "user", "content": user_message}],
            max_tokens=1000,
            temperature=0.3
        )

        return response.content[0].text


class GoogleLLMProvider(LLMProvider):
    """Google Gemini LLM provider."""

    def __init__(self, api_key: str = None, model: str = "gemini-pro"):
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("Please install google-generativeai: pip install google-generativeai")

        api_key = api_key or os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

    def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate response using Google Gemini API."""
        if context:
            full_prompt = (
                "You are a helpful assistant that answers questions based only on the provided context. "
                "If the context doesn't contain information to answer the question, say so explicitly. "
                "Always provide accurate information based solely on the context provided.\n\n"
                f"Context: {context}\n\n"
                f"Question: {prompt}\n\n"
                "Answer:"
            )
        else:
            full_prompt = (
                "You are a helpful assistant. Answer the following question:\n\n"
                f"Question: {prompt}\n\n"
                "Answer:"
            )

        response = self.model.generate_content(full_prompt)
        return response.text


class LLMService:
    """Service that manages LLM providers and provides a unified interface."""

    def __init__(self, provider_type: str = "openai", api_key: str = None, model: str = None):
        """
        Initialize the LLM service.

        Args:
            provider_type: Type of LLM provider ('openai', 'anthropic', 'google', etc.)
            api_key: API key for the provider (if not provided, will use environment variable)
            model: Model name to use (default depends on provider)
        """
        self.provider = self._create_provider(provider_type, api_key, model)

    def _create_provider(self, provider_type: str, api_key: str, model: str) -> LLMProvider:
        """Create the appropriate LLM provider based on the type."""
        if provider_type.lower() == "openai":
            model = model or os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
            return OpenAILLMProvider(api_key=api_key, model=model)
        elif provider_type.lower() == "anthropic":
            model = model or os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
            return AnthropicLLMProvider(api_key=api_key, model=model)
        elif provider_type.lower() == "google":
            model = model or os.getenv("GOOGLE_MODEL", "gemini-pro")
            return GoogleLLMProvider(api_key=api_key, model=model)
        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")

    def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate a response from the configured LLM provider."""
        return self.provider.generate_response(prompt, context)

    def generate_answer_with_context(self, question: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate an answer based on question and retrieved context chunks.

        Args:
            question: The user's question
            context_chunks: List of context chunks with metadata

        Returns:
            Dictionary with 'answer' and 'citations'
        """
        # Build context from chunks
        context_parts = []
        citations = []

        for chunk in context_chunks:
            content = chunk.get('content', '')
            metadata = chunk.get('metadata', {})

            context_parts.append(content)

            # Create citation from chunk metadata
            citation = {
                'source_path': metadata.get('source_path', ''),
                'title': metadata.get('title', ''),
                'chunk_index': metadata.get('chunk_index', 0),
                'snippet': content[:200] + "..." if len(content) > 200 else content
            }
            citations.append(citation)

        full_context = "\n\n".join(context_parts)

        # Generate response using the LLM
        answer = self.generate_response(question, full_context)

        return {
            'answer': answer,
            'citations': citations
        }