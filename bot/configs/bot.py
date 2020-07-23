from pydantic import BaseSettings, Field, SecretStr


class BotConfig(BaseSettings):
    api_token: SecretStr = Field(..., env='API_TOKEN')
