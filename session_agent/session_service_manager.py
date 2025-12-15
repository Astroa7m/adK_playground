from google.adk.sessions.database_session_service import DatabaseSessionService

# this must be called once
print("Defining the global instance of session state")
db_url = "sqlite+aiosqlite:///./session_manager.db"
session_service = DatabaseSessionService(db_url=db_url)
