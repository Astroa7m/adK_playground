from structured_agent.models import AgentConfig, AgentResponseLength, AgentSideTalkConfig, AgentEmojisConfig, \
    ConversationExample, AgentPersonality, AgentDialect

from typing import Optional, List, Literal


def structure_the_output(
        agent_name: str,
        personality: AgentPersonality = AgentPersonality.Casual_and_Down_To_Earth,
        dialect: AgentDialect = AgentDialect.Fusha,
        gender: Literal["Male", "Female"] = "Male",
        ai_self_disclosure: bool = False,
        split_long_messages: bool = False,
        response_length: AgentResponseLength = AgentResponseLength.Medium,
        side_talk_config: AgentSideTalkConfig = AgentSideTalkConfig.Diplomatic,
        emoji_config: AgentEmojisConfig = AgentEmojisConfig.Medium,
        interaction_steps: Optional[List[str]] = None,
        conversation_examples: Optional[List[ConversationExample]] = None,
        segmentations: Optional[List[str]] = None,
        general_instructions: str = ""
) -> str:
    """
    Extract different configs from a large dataset of conversations.

    You are going to be provided with a list of input/output of conversations between
    a client and a customer support employee in a particular domain.

    Your job is to understand the patterns, behaviour, character, tone, and everything
    related to the customer support, and based on your extraction, you should output
    a JSON structure of the configurations.

    Args:
        agent_name: The name of the AI agent
        personality: Personality of the AI agent
        dialect: The dialect that the AI agent has to use while interacting with users
        gender: The preferred gender defined for the AI agent
        ai_self_disclosure: Whether the AI agent has to disclose that it is an AI or not during interaction
        split_long_messages: Allows the AI agent to split long messages into chunks
        response_length: Preferred response length from the AI agent
        side_talk_config: Defines how much the AI agent can steer from the main topic
        emoji_config: Defines the degree the AI agent can use emojis
        interaction_steps: Specify the step‑by‑step actions the AI agent should follow during each customer interaction
        conversation_examples: Provide sample customer‑agent dialogues that capture the voice and wording
        segmentations: How the AI agent capture and handle different customer segments
        general_instructions: General instructions the AI agent has to follow

    Extra Instructions:
        - Some fields might not be clear to extract from the conversation, for that you can use the default value as required.

    Returns:
        JSON string of the configuration
    """
    # Handle mutable defaults
    if interaction_steps is None:
        interaction_steps = []
    if conversation_examples is None:
        conversation_examples = []
    if segmentations is None:
        segmentations = []

    # Create the config object
    config = AgentConfig(
        agent_name=agent_name,
        personality=personality,
        dialect=dialect,
        gender=gender,
        ai_self_disclosure=ai_self_disclosure,
        split_long_messages=split_long_messages,
        response_length=response_length,
        side_talk_config=side_talk_config,
        emoji_config=emoji_config,
        interaction_steps=interaction_steps,
        conversation_examples=conversation_examples,
        segmentations=segmentations,
        general_instructions=general_instructions
    )

    return config.model_dump_json()