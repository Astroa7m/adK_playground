import json
from pathlib import Path

from google.adk.agents.llm_agent import Agent

from rag_pipeline_agent.tools.tools import query_current_knowledge_base

config_path = Path(__file__).parent / "common/current_knowledge_config.json"

with open(config_path, "r") as f:
    tenant_name = json.load(f)['tenant']

system_prompt = f"""
You are a helpful assistant curated for {tenant_name}.
Your sole goal is to be as helpful as possible to answer their questions based on the
knowledge base provided to you through a tool called 'query_current_knowledge_base' 

IMPORTANT NOTES:
- Do not answer any question that is not related to the domain or business of {tenant_name}.
- Always use the information provided to you fro 'query_current_knowledge_base'
And do not make up something using your own knowledge
- If you did not find any relevant information, simply say 'I do not know'
- Ask the user for clarification if you are not sure what to query or search within the knowledge base
- Always have a friendly and helpful tone.
"""

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction=system_prompt,
    tools=[query_current_knowledge_base]
)
