# 用于调用Knative Function
import os
import requests
import json

class KnativeInvoker:
    def __init__(self, gateway_ip=None, gateway_port=None) -> None:
        if gateway_ip and gateway_port != None:
            self.gateway_ip = gateway_ip
            self.gateway_port = gateway_port
        else:
            self.init()

    def init(self):
        # 从环境变量中初始化
        self.gateway_ip = os.environ.get("GATEWAY_IP", "192.168.122.11")
        self.gateway_port = os.environ.get("GATEWAY_PORT", 31895)

    def invoke_sync_function(self, function_name, data):
        headers = {
            "Host": f"{function_name}.default.example.com"
        }
        url = "http://" + self.gateway_ip + ":" + str(self.gateway_port) + "/function"
        response = requests.post(url, headers=headers, json=data)
        if str(response) == '<Response [200]>': # 成功调用了
            content = response.content.decode('utf-8')
        else:
            content = "<Response [404]>"
        return content


if __name__ == "__main__":
    my_invoker = KnativeInvoker()
    response = my_invoker.invoke_sync_function("helloworld-python", "123")
    print(response)
    