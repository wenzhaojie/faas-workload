from transformers import AutoTokenizer, AutoModel
import torch

tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm2-6b", trust_remote_code=True)

# 判断是否GPU可用，否则使用cpu
if torch.cuda.is_available():
    model = AutoModel.from_pretrained("THUDM/chatglm2-6b-int4", trust_remote_code=True).cuda()
else:
    model = AutoModel.from_pretrained("THUDM/chatglm2-6b-int4", trust_remote_code=True).float()
model = model.eval()


def handle_batch(obj):
    # obj = {
    #     "batch_list": [
    #         {
    #             "history": [],
    #             "input": "Hello, I'm a language model.",
    #         },
    #         {
    #             "history": [],
    #             "input": "你好",
    #         },
    #     ]
    # }

    # 开始预测
    batch_list = obj["batch_list"]
    history_list = []
    for item in batch_list:
        history = item["history"]
        input = item["input"]
        response, history = model.chat(tokenizer, input, history=history)
        history_list.append(history)

    # batch 预测
    response, history = model.evaluate()


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