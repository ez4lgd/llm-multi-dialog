import requests

# 定义请求的URL
url = "http://localhost:5000/api/v1/conversations/"

try:
    # 发送GET请求
    response = requests.get(url)
    
    # 检查响应状态码
    if response.status_code == 200:
        # 打印响应内容（假设是JSON格式）
        print("请求成功！响应内容：")
        print(response.json())
    else:
        print(f"请求失败，状态码：{response.status_code}")
        print("响应内容：", response.text)

except requests.exceptions.RequestException as e:
    print(f"请求发生错误：{e}")
