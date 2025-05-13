# 大模型调用封装，支持多引擎（OpenAI/Azure等）
import os
import time
from langchain_openai import AzureChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler
from core.config import settings

class CustomAzureCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0

    def on_llm_start(self, serialized, prompts, **kwargs):
        self.start_time = time.time()
        print("AzureChatOpenAI 调用开始...")
        for prompt in prompts:
            print("Prompt:", prompt)

    def on_llm_new_token(self, token, **kwargs):
        # 若采用流式输出，可逐个打印token
        print(token, end="", flush=True)

    def on_llm_end(self, response, **kwargs):
        self.end_time = time.time()
        print(f"response is {response}")
        usage = response.llm_output.get("token_usage")
        self.prompt_tokens = usage.get("prompt_tokens", 0)
        self.completion_tokens = usage.get("completion_tokens", 0)
        self.total_tokens = usage.get("total_tokens", 0)
        elapsed = self.end_time - self.start_time if self.start_time else None

        print("\nAzureChatOpenAI 调用结束")
        if elapsed is not None:
            print(f"调用耗时：{elapsed:.2f} 秒")
        print(f"Token 使用：总共 {self.total_tokens}（Prompt: {self.prompt_tokens}, Completion: {self.completion_tokens}）")

def get_llm(
    model_name="gpt-4.1",
    temperature=0.7,
    streaming=False,
    callbacks=None
):
    """
    获取 AzureChatOpenAI 实例，自动读取配置
    如果模型名以'o'开头（如Azure的o系列模型），则强制temperature=1
    """
    # 判断是否为Azure的o开头模型
    if isinstance(model_name, str) and model_name.startswith("o"):
        temperature = 1
    llm = AzureChatOpenAI(
        openai_api_version=settings.AZURE_OPENAI_API_VERSION,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        openai_api_key=settings.AZURE_OPENAI_API_KEY,
        model_name=model_name,
        temperature=temperature,
        streaming=streaming,
        callbacks=callbacks or [CustomAzureCallbackHandler()]
    )
    return llm

# 可选：统一入口类，兼容多种大模型
class LLMEngine:
    def __init__(self, api_key: str = "", engine: str = "azure"):
        self.engine = engine
        self.api_key = api_key or settings.AZURE_OPENAI_API_KEY

    async def chat(self, messages, model="gpt-4.1", temperature=0.7, streaming=False):
        """
        支持 AzureChatOpenAI 聊天
        messages: [{"role": "user"/"assistant", "content": "..."}]
        """
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

        def to_lc_message(msg):
            role = msg.get("role")
            content = msg.get("content", "")
            if role == "user":
                return HumanMessage(content=content)
            elif role == "assistant":
                return AIMessage(content=content)
            elif role == "system":
                return SystemMessage(content=content)
            else:
                # 兼容未知角色
                return HumanMessage(content=content)

        lc_messages = [to_lc_message(m) for m in messages]

        if self.engine == "azure":
            llm = get_llm(model_name=model, temperature=temperature, streaming=streaming)
            # langchain 的 AzureChatOpenAI 支持 async 调用
            response = await llm.agenerate([lc_messages])
            # 取第一个回复
            return response.generations[0][0].text
        else:
            # TODO: 支持其他引擎
            return "暂未实现其他引擎"

llm_engine = LLMEngine()
