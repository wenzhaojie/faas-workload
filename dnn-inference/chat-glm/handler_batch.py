from transformers import AutoTokenizer, AutoModel
import torch

tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm2-6b", trust_remote_code=True)

# 判断是否GPU可用，否则使用cpu
if torch.cuda.is_available():
    model = AutoModel.from_pretrained("THUDM/chatglm2-6b", trust_remote_code=True).cuda()
    torch_device = 'cuda'
else:
    model = AutoModel.from_pretrained("THUDM/chatglm2-6b", trust_remote_code=True).float()
    torch_device = 'cpu'

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

    sentences = [
        "你好",
        "介绍一下清华大学"
    ]
    parameters = [(False, 2048, 1),
                  (False, 64, 1),
                  (True, 2048, 1),
                  (True, 64, 1),
                  (True, 2048, 4)]

    outputs = []

    for (do_sample, max_length, num_beams) in zip(parameters):

        inputs = tokenizer(sentences, return_tensors="pt", padding=True)
        inputs = inputs.to(torch_device)

        outputs = model.generate(
            **inputs,
            do_sample=do_sample,
            max_length=max_length,
            num_beams=num_beams
        )

        batch_out_sentence = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        print(batch_out_sentence)
        outputs.append(batch_out_sentence)

    return outputs


if __name__ == "__main__":
    # 测试
    obj = {
        "history": [],
        "input": "你好",
    }
    handle_batch(obj)