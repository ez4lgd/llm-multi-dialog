from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, ConfigDict
from typing import Literal, Optional

class Settings(BaseSettings):
    APP_NAME: str = Field("ChatAgent", description="应用程序名称")
    HOST: str = Field("0.0.0.0", description="服务监听地址")
    PORT: int = Field(5000, description="服务监听端口")
    DEBUG: bool = Field(False, description="调试模式")
    DATA_PATH: str = Field("./data", description="数据存储路径")
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field("INFO", description="日志级别")
    JWT_SECRET: str = Field(..., description="JWT密钥", min_length=32)
    JWT_ALGORITHM: str = Field("HS256", description="JWT算法")
    OPENAI_API_KEY: Optional[str] = Field(None, description="OpenAI API密钥")
    AZURE_OPENAI_API_KEY: str = Field("", description="Azure OpenAI API密钥")
    AZURE_OPENAI_ENDPOINT: str = Field("", description="Azure OpenAI端点")
    AZURE_OPENAI_API_VERSION: str = Field("", description="Azure OpenAI API版本")

    @field_validator("JWT_SECRET")
    @classmethod
    def validate_jwt_secret(cls, v):
        if len(v) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters long")
        return v

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

settings = Settings()
