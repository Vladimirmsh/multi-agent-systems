from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GOOGLE_API_KEY: str = ""
    MAX_SEARCH_RESULTS: int = 5
    MAX_URL_TEXT_LENGTH: int = 8000 
    
    # Налаштування серверів
    SEARCH_MCP_PORT: int = 8901
    REPORT_MCP_PORT: int = 8902
    ACP_PORT: int = 8903
    SEARCH_MCP_URL: str = "http://localhost:8901/sse"
    REPORT_MCP_URL: str = "http://localhost:8902/sse"
    ACP_URL: str = "http://localhost:8903"
    
    # Langfuse налаштування
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""
    LANGFUSE_BASE_URL: str = "https://us.cloud.langfuse.com"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

#Всі промпти (PLANNER_PROMPT, RESEARCHER_PROMPT, CRITIC_PROMPT, SUPERVISOR_PROMPT) перенесені в Langfuse Prompt Management!