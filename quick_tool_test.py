import os
from dotenv import load_dotenv
from wolfram_alpha_CrewAi_tool import WolframAlphaTool

load_dotenv()
WOLFRAM_APP_ID = os.getenv('APP_ID')

# Initialize the custom tool
wolfram_tool = WolframAlphaTool()

question = "What is the minimum distance from the earth to mars?"

# Run the tool
try:
    result = wolfram_tool._run(query=question)
    print("Query Result:")
    print(result)
except ValueError as e:
    print(f"Error: {e}")
