import os
from crewai import Agent, Task, Crew
from wolfram_alpha_tool import wolfram_alpha_tool

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


# Define a custom tool using the wolfram_alpha_tool function
class WolframAlphaTool:
    name = "Wolfram Alpha Tool"
    description = "Queries Wolfram Alpha for information."

    def _run(self, query):
        return wolfram_alpha_tool(query)


wolfram_tool = WolframAlphaTool()

# Define the Researcher Agent
researcher = Agent(
    role='Researcher',
    goal='Fetch and analyze data from Wolfram Alpha.',
    backstory='An expert in computational knowledge.',
    tools=[wolfram_tool],
    verbose=True
)

# Define the Writer Agent
writer = Agent(
    role='Writer',
    goal='Create a report based on the analysis.',
    backstory='A skilled writer with a knack for simplifying complex data.',
    verbose=True
)

# Define the Research Task
research_task = Task(
    description='Query Wolfram Alpha for information on the specified topic.',
    expected_output='Analysis report',
    agent=researcher,
    arguments={'query': 'What are the applications of AI in healthcare?'}
)

# Define the Writing Task
write_task = Task(
    description='Write a report based on the analysis from the Researcher.',
    expected_output='Formatted report',
    agent=writer
)

# Create the Crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    verbose=True
)

# Kickoff the process
result = crew.kickoff()
print(result)
