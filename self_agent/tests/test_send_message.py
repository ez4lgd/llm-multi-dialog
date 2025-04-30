import asyncio
import uuid
from httpx import AsyncClient

async def main():
    # 允许自定义消息内容
    content = input("请输入要发送的消息内容：")
    conversation_id = str(uuid.uuid4())

    async with AsyncClient(base_url="http://localhost:5000") as ac:
        resp = await ac.post(
            f"/api/v1/conversations/{conversation_id}/messages",
            json={"content": content}
        )
        print("返回结果：")
        print(resp.json())

if __name__ == "__main__":
    asyncio.run(main())
