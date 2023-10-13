import logging
from transformers import AutoTokenizer, AutoModelForCausalLM

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class SimpleTokenCounter:
    def __init__(self, model_path="/home/wzj/GitHubProjects/Llama-2-7b-chat-hf"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
        self.tokenizer.add_special_tokens({"pad_token": "<PAD>"})
        self.model = AutoModelForCausalLM.from_pretrained(model_path)

    def get_token_count(self, input_text, max_length=512):
        if isinstance(input_text, (bytes, bytearray)):
            input_text = input_text.decode("utf-8")
        inputs = self.tokenizer.encode_plus(
            input_text,
            add_special_tokens=True,
            return_tensors="pt",
            truncation=True,
            max_length=max_length,  # 设置最大长度
            padding=True, # 设置padding
        )
        token_count = len(inputs["input_ids"][0])
        return token_count
    


if __name__ == "__main__":
    # 使用
    model_path = "/home/wzj/GitHubProjects/Llama-2-7b-chat-hf"  # 请替换为你的模型路径
    sentence = "Your English sentence here."

    counter = SimpleTokenCounter(model_path)
    token_count = counter.get_token_count(sentence)
    print(f"The token count for the sentence is: {token_count}")