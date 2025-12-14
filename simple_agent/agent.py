from google.adk.agents.llm_agent import Agent

# to launch
# adk run simple_agent
# adk web

def summary(summary_value: str) -> str:
    """
    Use this tool whenever you are sure that the conversation has ended, when the user doesn't any further assistance
    :param summary_value: summary text that you will generate
    :return: summary_value
    """
    return summary_value

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
    tools=[summary]
)
