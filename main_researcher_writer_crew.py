import os
from crewai import Agent, Task, Crew
from crewai_tools import BaseTool
from dotenv import load_dotenv
import wolframalpha

# Load environment variables from .env file
load_dotenv()

# Retrieve the API keys from the environment
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL_NAME = os.getenv('OPENAI_MODEL_NAME')
WOLFRAM_APP_ID = os.getenv('APP_ID')

if not OPENAI_API_KEY or not WOLFRAM_APP_ID:
    raise ValueError("API keys not found in environment variables.")


# The Wolfram Alpha tool function
def wolfram_alpha_tool(query: str) -> str:
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


# A custom tool using the wolfram_alpha_tool function
class WolframAlphaTool(BaseTool):
    name: str = "Wolfram Alpha Tool"
    description: str = "Queries Wolfram Alpha for information."

    def _run(self, query: str) -> str:
        result = wolfram_alpha_tool(query)
        if "error" in result.lower():
            raise ValueError(f"Wolfram Alpha Tool Error: {result}")
        return result


# Initialize the custom tool
wolfram_tool = WolframAlphaTool()


def execute_crew(question: str) -> str:
    """
    Execute the AI crew with a given question.

    Args:
    question (str): The question to be processed by the crew.

    Returns:
    str: The final report generated by the crew.
    """
    # The Researcher Agent
    researcher = Agent(
        role='Researcher',
        goal=f'Fetch and analyze data from Wolfram Alpha about the question: {question}',
        backstory='An expert in science and computational knowledge.',
        tools=[wolfram_tool],
        verbose=True
    )

    # The Writer Agent
    writer = Agent(
        role='Writer',
        goal=f'Create a report based on the analysis about the question: {question}.',
        backstory='A skilled writer with a knack for simplifying complex data.',
        verbose=True
    )

    # The Research Task
    research_task = Task(
        description=f'Query Wolfram Alpha for information on the specified question: {question}.',
        expected_output=f'Analysis report about the question: {question}',
        agent=researcher,
        arguments={'query': question}
    )

    # The Writing Task
    write_task = Task(
        description=f'Write a report based on the analysis from the Researcher about the question: {question}.',
        expected_output='Formatted report',
        agent=writer
    )

    # The Crew
    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, write_task],
        verbose=True
    )

    # Kickoff the process and get the result
    result = crew.kickoff()
    return result


if __name__ == "__main__":
    print("Welcome to the Wolfram Alpha query tool!")
    print("You can ask questions about mathematical calculations, unit conversions,")
    print("scientific data, date and time calculations, and more.")
    print("Enter your question below:")
    user_question = input("> ")

    final_report = execute_crew(user_question)
    print("\nFinal Report:")
    print(final_report)
