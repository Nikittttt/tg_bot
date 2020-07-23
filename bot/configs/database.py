from pydantic import BaseSettings, Field, SecretStr


class DataBaseConfig(BaseSettings):
    host: str = Field(..., env='DB_HOST')
    name: str = Field(..., env='DB_NAME')
    user: str = Field(..., env='DB_USER')
    password: SecretStr = Field(..., env='DB_PASS')
    port: str = Field(..., env='DB_PORT')
    driver: str = Field(..., env='DB_DRIVER')

    @property
    def connection_url(self):
        return f'{self.driver}://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.name}'
