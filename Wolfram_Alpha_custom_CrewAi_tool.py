import os
import wolframalpha
from typing import Type, Any
from pydantic.v1 import BaseModel, Field
from crewai_tools.tools.base_tool import BaseTool
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the API keys from the environment
WOLFRAM_APP_ID = os.getenv('APP_ID')

if not WOLFRAM_APP_ID:
    raise ValueError("API key not found in environment variables.")


# Define the input schema for the WolframAlphaTool
class WolframAlphaToolSchema(BaseModel):
    """Input schema for WolframAlphaTool."""
    query: str = Field(..., description="The query to search in Wolfram Alpha")


# The Wolfram Alpha tool function
class WolframAlphaTool(BaseTool):
    name: str = "Wolfram Alpha Tool"
    description: str = "Queries Wolfram Alpha for information."
    args_schema: Type[BaseModel] = WolframAlphaToolSchema

    def _run(self, query: str) -> str:
        try:
            # Initialize Wolfram Alpha client
            client = wolframalpha.Client(WOLFRAM_APP_ID)

            # Query Wolfram Alpha
            res = client.query(query)

            # Extract and return the result
            if not res['@success']:
                return "Query failed. Please check your query syntax."

            result = next(res.results).text if res.results else "No results found."
            return result

        except Exception as e:
            return f"An error occurred: {str(e)}"
