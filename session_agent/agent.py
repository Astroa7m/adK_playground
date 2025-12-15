import asyncio
import os
import uuid
from google.adk.models.lite_llm import LiteLlm
from google.adk import Runner
from google.adk.agents.llm_agent import Agent
from google.adk.sessions import DatabaseSessionService
from google.genai.types import Content, Part, FunctionResponse

from session_agent.session_service_manager import session_service
from session_agent.tools import summary
from dotenv import load_dotenv

"""to launch"""
# adk run session_agent
# adk web


# adding my supabase db into database session service


load_dotenv()
# db_url = os.getenv("DATABASE_URL")
app_name = "session_agent"


async def run_session(session_service, session_id, user_id):

    model = LiteLlm(model="groq/openai/gpt-oss-120b")

    root_agent = Agent(
        model='gemini-2.5-flash-lite',
        # model=model,
        name='root_agent',
        description='A helpful assistant for user questions.',
        instruction=f'Answer user questions to the best of your knowledge\nusername is:{user_id}',
        tools=[summary]
    )

    if session_id:
        session = await session_service.get_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
        )
    else:
        session_id = str(uuid.uuid4())
        session = await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
        )

    print(f"State created: SessionID: ({session.id})")

    runner = Runner(
        agent=root_agent,
        session_service=session_service,
        app_name=app_name,
    )

    while True:
        query = input("Enter your query: ")
        user_message = Content(
            role="user",
            parts=[
                Part(text=query)
            ]
        )

        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_message):
            if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
                for part in event.content.parts:
                    # getting the text
                    if hasattr(part, 'text') and part.text:
                        print(f"{part.text}")

                    # getting function res if found
                    if hasattr(part, 'function_response') and part.function_response:
                        print(f"{part.function_response.response}")

async def start_program():
    # we are going to simulate a passwordless login with a user id
    user_id = input("Please enter your username: ")


    # getting user's sessions
    sessions_res = await session_service.list_sessions(app_name=app_name, user_id=user_id)
    sessions = sessions_res.sessions
    if sessions:
        choices = ""
        for index, session in enumerate(sessions):
            choices += f"{index}: {session.id}\n"

        choice = int(input(f"\n{choices}\nPlease choose a session from above options (-1 to create a new one): (0-{len(sessions)-1}): "))
        if choice == -1:
            session_id = None
        else:
            session_id = sessions[choice].id
    else:
        print("You have no older conversations\nStarting a new one...\n")
        session_id = None

    await run_session(session_service, session_id, user_id)


asyncio.run(start_program())
