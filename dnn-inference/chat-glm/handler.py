from transformers import AutoTokenizer, AutoModel
import torch

tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm2-6b", trust_remote_code=True)

# 判断是否GPU可用，否则使用cpu
if torch.cuda.is_available():
    model = AutoModel.from_pretrained("THUDM/chatglm2-6b", trust_remote_code=True).cuda()
else:
    model = AutoModel.from_pretrained("THUDM/chatglm2-6b", trust_remote_code=True).float()
model = model.eval()


def handle(obj):
    # obj = {
    #     "history": [],
    #     "input": "Hello, I'm a language model.",
    # }
    try:
        history = obj["history"]
        input = obj["input"]
    except Exception as e:
        return {"error": str(e)}

    # 开始预测
    response, history = model.chat(tokenizer, input, history=[])
    print(f"response:{response}")
    print(f"history:{history}")

    return history


if __name__ == "__main__":
    # 测试
    obj = {
        "history": [],
        "input": "你好",
    }
    handle(obj)