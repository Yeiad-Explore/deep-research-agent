"""
Azure OpenAI Client for backup and specialized LLM tasks
"""
import logging
from typing import List, Dict, Any, AsyncIterator
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class AzureOpenAIClient:
    """
    Azure OpenAI client for complex synthesis and backup LLM operations
    Uses GPT-5.1 via Azure OpenAI endpoint
    """

    def __init__(
        self,
        api_key: str,
        endpoint: str,
        deployment_name: str
    ):
        """
        Initialize Azure OpenAI client

        Args:
            api_key: Azure OpenAI API key
            endpoint: Azure OpenAI endpoint URL (with /v1 path)
            deployment_name: Deployment name (e.g., gpt-5.1-chat)
        """
        self.client = AsyncOpenAI(
            base_url=endpoint,
            api_key=api_key
        )
        self.deployment_name = deployment_name

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        max_completion_tokens: int = 2000,
        stream: bool = False
    ) -> str:
        """
        Generate chat completion

        Args:
            messages: List of message dictionaries
            max_completion_tokens: Maximum tokens in response
            stream: Whether to stream the response

        Returns:
            Generated text
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                max_completion_tokens=max_completion_tokens,
                stream=stream
            )

            if stream:
                # Return the streaming response object
                return response
            else:
                content = response.choices[0].message.content
                logger.info(f"Azure OpenAI completion: {len(content)} characters")
                return content

        except Exception as e:
            logger.error(f"Error in Azure OpenAI completion: {e}")
            raise

    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        max_completion_tokens: int = 2000
    ) -> AsyncIterator[str]:
        """
        Stream chat completion chunks

        Args:
            messages: List of message dictionaries
            max_completion_tokens: Maximum tokens in response

        Yields:
            Text chunks as they're generated
        """
        try:
            stream = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                max_completion_tokens=max_completion_tokens,
                stream=True
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Error in Azure OpenAI streaming: {e}")
            raise

    async def generate_answer(
        self,
        query: str,
        all_content: str,
        sources: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a simple, conversational answer to the query using gathered research

        Args:
            query: Original research query
            all_content: Combined content from all sources
            sources: All source references for citations

        Returns:
            Single AI-generated answer
        """
        # Create sources list for reference
        sources_text = "\n".join([
            f"[{i+1}] {s.get('title', 'Unknown')} - {s.get('url', '')}"
            for i, s in enumerate(sources[:20])  # Limit to 20 sources
        ])

        messages = [
            {
                "role": "system",
                "content": """You are a helpful AI research assistant. Answer the user's question using the provided research material.

Guidelines:
- Provide a clear, conversational answer
- Use information from the sources provided
- Include inline citations like [1], [2] when referencing sources
- Be concise but comprehensive
- If sources disagree, mention different perspectives
- If information is limited, acknowledge it
- Don't create a structured report, just answer the question naturally"""
            },
            {
                "role": "user",
                "content": f"""Question: {query}

Research Material:
{all_content[:15000]}

Available Sources:
{sources_text}

Please answer the question using the research material above. Include citations [N] when referencing specific information."""
            }
        ]

        return await self.chat_completion(
            messages,
            max_completion_tokens=2000
        )

    async def analyze_gaps(
        self,
        query: str,
        current_findings: str,
        sources: List[str]
    ) -> List[str]:
        """
        Identify gaps in research that need additional investigation

        Args:
            query: Original query
            current_findings: Current research findings
            sources: Sources already consulted

        Returns:
            List of refined search queries to fill gaps
        """
        messages = [
            {
                "role": "system",
                "content": "You are a research gap analyst. Identify missing information and suggest targeted searches."
            },
            {
                "role": "user",
                "content": f"""Original Query: {query}

Current Findings:
{current_findings}

Sources Consulted: {', '.join(sources)}

Identify 3-5 specific gaps in the research and suggest targeted search queries to address them. Return as a JSON list of strings."""
            }
        ]

        response = await self.chat_completion(messages, max_completion_tokens=500)

        try:
            import json
            gaps = json.loads(response)
            return gaps if isinstance(gaps, list) else []
        except:
            return []

    async def extract_expert_opinions(
        self,
        comments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Identify and extract expert opinions from Reddit comments

        Args:
            comments: List of Reddit comments

        Returns:
            List of identified expert opinions with metadata
        """
        # Filter high-value comments
        high_value_comments = [
            c for c in comments
            if c.get('score', 0) > 10 and len(c.get('body', '')) > 100
        ]

        if not high_value_comments:
            return []

        comments_text = "\n\n---\n\n".join([
            f"[Score: {c.get('score')}] {c.get('body')}"
            for c in high_value_comments[:10]
        ])

        messages = [
            {
                "role": "system",
                "content": "You identify expert opinions in discussions based on depth, technical accuracy, and insight."
            },
            {
                "role": "user",
                "content": f"""Analyze these Reddit comments and identify which appear to be from experts or highly knowledgeable individuals. For each expert comment, extract:
1. Key insights
2. Why it appears expert-level
3. Main argument

Comments:
{comments_text}

Return as JSON array with: [{{\"insight\": \"...\", \"expertise_indicator\": \"...\", \"argument\": \"...\"}}]"""
            }
        ]

        response = await self.chat_completion(messages, max_completion_tokens=1000)

        try:
            import json
            return json.loads(response)
        except:
            return []
