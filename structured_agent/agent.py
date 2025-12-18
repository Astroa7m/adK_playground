from typing import List
#melivs (vector db)
from google.adk.agents import SequentialAgent
from google.adk.agents.llm_agent import Agent

from structured_agent.models import AgentConfig
from structured_agent.tools import structure_the_output

STRUCTURED_OUTPUT_PROMPT = """
You are an expert of extracting different configs from a large dataset of conversations.

You are going to be provided with a list of input/output of conversations between a client and a customer support employee in a particular domain.

Your job is to understand the patterns, behaviour, character, tone, and everything related to the customer support, and based on your extraction, You should output a JSON structure of the configurations based on the provided schema.

Extra Instructions: 
- Some fields within the provided schema might not be clear to extract from the conversation, for that you can use the default value as required.
"""


structured_output_agent = Agent(
    model='gemini-2.5-flash',
    name="structured_output_agent_with_tool_only",
    description='A helpful agent that structure output in JSON format',
    instruction=STRUCTURED_OUTPUT_PROMPT,
    include_contents='none'
)

# way 1, works directly
root_agent = SequentialAgent(
    # model='gemini-2.5-flash',
    name='root_agent',
    # description='A helpful assistant for user questions.',
    # instruction=MAIN_AGENT_PROMPT,
    sub_agents=[structured_output_agent]
)

# way 2, works as tool (didn't like it)
# root_agent = Agent(
#     model='gemini-2.5-flash-lite',
#     name='root_agent',
#     description='A helpful assistant for user questions.',
#     instruction="You are a helpful assistant",
#     tools=[structure_the_output]
# )




