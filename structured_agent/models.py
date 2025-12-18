from enum import Enum
from typing import List, Optional, Literal, Tuple

from pydantic import BaseModel, Field, conlist

"""
issues resolved:
- default values for lists params should be made with `default_factory=list` instead of `default=None` or `default=list` in Field param
- removed List[Tuple[str, str]] and made it a List[CustomClass] to avoid JSON/Pydantic errors
- removed `examples` Field params as it was causing an error

"""

class AgentPersonality(Enum):
    """Defines the personality of the AI agent and how it should behave"""
    Empathetic_and_Friendly = "Empathetic and Friendly"
    Formal_and_Professional = "Formal and Professional"
    Salesperson = "Salesperson"
    Fun_and_Humorous = "Fun and Humorous"
    Casual_and_Down_To_Earth = "Casual and Down-To-Earth"


class AgentDialect(Enum):
    """Used to define the dialect that the AI agent speaks in Arabic"""
    Omani = "Omani"
    Saudi = "Saudi"
    Bahraini = "Bahraini"
    Kuwaiti = "Kuwaiti"
    Qatari = "Qatari"
    Emirati = "Emirati"
    Fusha = "Fusha (MSA)"


class AgentResponseLength(Enum):
    """Defines the response length the AI agent has to respect"""
    Brief = "Brief"
    Medium = "Medium"
    Extended = "Extended"


class AgentSideTalkConfig(Enum):
    """AI agent conversation-steering degree"""
    NONE = "None"
    Talkative = "Talkative"
    Diplomatic = "Diplomatic"


class AgentEmojisConfig(Enum):
    """Roles of emojis usage for the AI agent"""
    No_Emoji = "No Emoji"
    Medium = "Medium"
    High = "High"


class ConversationExample(BaseModel):
    query: str
    response: str


class AgentConfig(BaseModel):
    agent_name: str = Field(
        description="The name of the AI agent",
        # examples=["Orki Sales Agent"]
    )
    personality: AgentPersonality = Field(
        description="Personality of the AI agent",
        default=AgentPersonality.Casual_and_Down_To_Earth
    )
    dialect: AgentDialect = Field(
        description="The dialect that the AI agent has to use while interacting with users",
        default=AgentDialect.Fusha
    )
    gender: Literal["Male", "Female"] = Field(
        description="The preferred gender defined for the AI agent",
        default="Male"
    )
    ai_self_disclosure: bool = Field(
        description="Whether the AI agent has to disclose that it is an AI or not during interaction",
        default=False
    )
    split_long_messages: bool = Field(
        description="Allows the AI agent to split long messages into chunks",
        default=False
    )
    response_length: AgentResponseLength = Field(
        description="Preferred response length from the AI agent",
        default=AgentResponseLength.Medium
    )
    side_talk_config: AgentSideTalkConfig = Field(
        description="Defines how much the AI agent can steer from the main topic",
        default=AgentSideTalkConfig.Diplomatic
    )
    emoji_config: AgentEmojisConfig = Field(
        description="Defines the degree the AI agent can use emojis",
        default=AgentEmojisConfig.Medium
    )
    interaction_steps: Optional[List[str]] = Field(
        description= "Specify the step‑by‑step actions the AI agent should follow during each customer interaction",
        default_factory=list,
        # examples=["Create a plan of tasks", "prepare the tools needed to complete the tasks", "solve each task separately", "ask for user feedback"]
    )
    conversation_examples: Optional[conlist(ConversationExample, max_length=2)] = Field(
        description="Provide sample customer‑agent dialogues that capture the voice and wording—the AI will mirror that tone in its responses.",
        # examples=[ConversationExample("Sup homie", "Hey! Seems like someone is chilling, what is in your mind today?")]
    )
    segmentations: Optional[List[str]] = Field(
        description="How the AI agent capture and handle different customer segments",
        default_factory=list
    )
    general_instructions: str = Field(
        description="General instructions the AI agent has to follow",
        default=""
    )
