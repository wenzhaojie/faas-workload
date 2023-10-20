import torch
from transformers import AutoTokenizer, AutoModel
from ts.torch_handler.base_handler import BaseHandler
import time
import os
import json
from ts.protocol.otf_message_handler import send_intermediate_predict_response
from pkg_resources import packaging

if packaging.version.parse(torch.__version__) >= packaging.version.parse("1.8.1"):
    from torch.profiler import ProfilerActivity, profile, record_function

    PROFILER_AVAILABLE = True
else:
    PROFILER_AVAILABLE = False


class TransformersGpt2Handler(BaseHandler):
    def initialize(self, content):

        # 加载模型并设置到设备上
        self.tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm2-6b", trust_remote_code=True)
        self.model = AutoModel.from_pretrained("THUDM/chatglm2-6b", trust_remote_code=True, device='cuda')
        self.model = self.model.eval()


    def preprocess(self, request):
        inputs = []
        for request_json in request:
            question_text = request_json["body"]["question"]
            history = request_json["body"]['history']
            prompt = self.tokenizer.build_prompt(question_text, history=history)
            inputs.append(prompt)
        inputs = self.tokenizer(inputs, return_tensors="pt", padding=True)
        inputs = inputs.to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))
        # if isinstance(question_text, (bytes, bytearray)):
        #     text = text.decode("utf-8")
        return inputs

    def inference(self, inputs, *args, **kwargs):
        with torch.no_grad():
            input_length = inputs["input_ids"].shape[-1]
            for outputs in self.model.stream_generate(
                    **inputs,
                    max_length=8192,
                    num_beams=1,
                    do_sample=True,
                    top_p=0.8,
                    temperature=0.8,
            ):
                outputs = outputs[:, input_length:]
                batch_out_sentence = self.tokenizer.batch_decode(outputs)
                # send_intermediate_predict_response(batch_out_sentence, self.context.request_ids, "Intermediate Prediction success", 200, self.context)

            return batch_out_sentence

    def postprocess(self, batch_out_sentence):

        return batch_out_sentence
