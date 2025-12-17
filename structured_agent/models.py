from pydantic import BaseModel


class AgentConfig(BaseModel):
    agent_name: str
    