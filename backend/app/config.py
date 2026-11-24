from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm_base_url: str = "http://host.docker.internal:1234/v1"
    llm_api_key: str = "lm-studio"
    llm_model: str = "qwen2.5-7b-instruct"
    llm_temperature: float = 0.2
    llm_timeout_s: int = 120
    agent_max_iterations: int = 6
    database_url: str = "postgresql+psycopg://chatbot:chatbot@postgres:5432/chatbot"
    mcp_server_url: str = "http://mcp_server:8001/mcp"


settings = Settings()
