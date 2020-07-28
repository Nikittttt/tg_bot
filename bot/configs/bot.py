from enum import Enum

from pydantic import BaseSettings, Field, SecretStr


class RunMode(str, Enum):
    dev = 'dev'
    prod = 'prod'


class BotConfig(BaseSettings):
    api_token: SecretStr = Field(..., env='API_TOKEN')
    run_mode: RunMode = Field(RunMode.prod, env='RUN_MODE')
    webhook_url: SecretStr = Field(..., env='WEBHOOK_URL')
    webapp_host: str = Field(..., env='WEBAPP_HOST')
    webapp_port: str = Field(..., env='WEBAPP_PORT')

    @property
    def is_prod(self):
        return self.run_mode == RunMode.prod
