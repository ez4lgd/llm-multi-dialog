import sys
import os
import pytest
import asyncio

# 动态将 self_agent 目录加入 sys.path，保证 core 能被正确 import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from self_agent.modules.llm import LLMEngine

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "model,temperature,streaming",
    [
        ("gpt-4.1", 0.7, False),
        ("gpt-35-turbo", 0.2, False),
        ("gpt-4.1", 1.0, True),
        ("o4-mini", 0.5, False),
    ]
)
async def test_chat_various_models(model, temperature, streaming):
    """
    测试 LLMEngine.chat 支持不同模型名、temperature、streaming 参数
    """
    engine = LLMEngine()
    messages = [
        {"role": "system", "content": "你是一个测试助手。"},
        {"role": "user", "content": "你好，介绍一下你自己。"},
        {"role": "assistant", "content": "我是AI助手，很高兴为你服务。"}
    ]
    try:
        result = await engine.chat(
            messages=messages,
            model=model,
            temperature=temperature,
            streaming=streaming
        )
        assert isinstance(result, str)
        print(f"model={model}, temp={temperature}, streaming={streaming} => {result}")
    except Exception as e:
        # 对于不存在的模型等异常情况，允许抛出异常
        print(f"model={model} 发生异常: {e}")
        if model == "not-exist-model":
            assert True
        else:
            assert False, f"模型 {model} 不应异常: {e}"

@pytest.mark.asyncio
async def test_chat_roles():
    """
    测试 chat 支持多种角色消息
    """
    engine = LLMEngine()
    messages = [
        {"role": "system", "content": "你是一个系统消息。"},
        {"role": "user", "content": "用户问题。"},
        {"role": "assistant", "content": "助手回答。"},
        {"role": "unknown", "content": "未知角色消息。"}
    ]
    result = await engine.chat(messages=messages)
    assert isinstance(result, str)
    print("多角色消息测试结果:", result)
#pytest self_agent/tests/test_llm.py
