# models 都需继承以下方法
import numpy as np
from sklearn.preprocessing import StandardScaler
import time
import math
from metrics import get_metric_dict
from pyplotter.plot import Plotter

class Basic_model:
    def __init__(self, name="Basic_model", scaler=StandardScaler()):
        # 初始化一些必要的参数  
        # print(f"正在初始化Basic_model!")
        # print(f"Basic_model scaler:{scaler}")
        self.scaler = scaler
        self.name = name
        self.ordinary_param_dict = {
            "seq_len": 1440 * 3,
            "pred_len": 1440,
            "is_scaler": False,
            "is_use_future": True,
            "period": 1440
        }

        self.unique_param_dict = {
        }
        pass

    def get_scaler(self):
        return self.scaler


    def get_name(self) -> str:
        return self.name
    

    def train(self, history):
        # 训练
        pass

    def predict(self, history, predict_window) -> list:
        # 使用一段历史序列来预测未来的值
        return []

    def rolling_predict(self, history, predict_window, test=None):
        # 滚动预测
        # history: 用于预测的历史数据
        # predict_window: 预测目标长度
        # test: 用于回测预测效果

        seq_len = self.ordinary_param_dict.get("seq_len", None)
        pred_len = self.ordinary_param_dict.get("pred_len", None)
        is_use_future = self.ordinary_param_dict.get("is_use_future", None)

        # 为了方便,转换成list格式的数据
        history = list(history)

        # 预测的结果需要存放
        predict_list = []
        compute_t_list = []
        pointer = 0

        # 是否使用test数据?
        if is_use_future == True:
            assert len(test) == predict_window
            history_add = list(test)
        else:
            history_add = predict_list

        while len(predict_list) < predict_window:
            # 获取 input
            if pointer < seq_len:
                history_base = history[-seq_len+pointer:]
                train = history_base + history_add[:pointer]
            else:
                history_base = []
                train = history_base + history_add[pointer-seq_len:pointer]

            assert len(train) == seq_len
            predict_res = self.predict(history=train, predict_window=pred_len)
            assert len(predict_res) == pred_len
            predict_list.extend(predict_res)
            # print(f"len(predict_list):{len(predict_list)}")
            pointer += pred_len

        # 最后收尾阶段
        # 有可能预测超出了我们所需要的
        rolling_predict= predict_list[:predict_window]
        return np.array(rolling_predict)


    def evaluate(self, train, test):
        '''
        用于评估模型的效果
        train: 训练数据
        test: 预测真实的数据
        '''
        is_scaler = self.ordinary_param_dict.get("is_scaler", None)

        # 先做归一化
        if is_scaler == True:
            combined_trace = np.concatenate((np.array(train), np.array(test)))
            processed_trace = self.scaler.fit_transform(combined_trace.reshape(-1,1)).reshape(-1,)
            train = processed_trace[:len(train)]
            test = processed_trace[len(train):]
        else:
            train = np.array(train)
            test = np.array(test)
        
        # 再训练
        start_t = time.time()
        self.train(history=train)
        train_t = time.time() - start_t

        # 滚动预测
        start_t = time.time()
        predict = self.rolling_predict(
            history=train, 
            predict_window=len(test),
            test=test,
        )
        predict_t = time.time() - start_t # 计算时间

        
        # 做还原归一化
        if is_scaler == True:
            predict = self.scaler.inverse_transform(predict.reshape(-1,1)).reshape(-1,)
            test = self.scaler.inverse_transform(test.reshape(-1,1)).reshape(-1,)

        # 指标计算
        metrics_dict = get_metric_dict(y_pred=predict, y_test=test)

        # 收集日志
        log_dict = {
            "model":self.name,
            "train_length":len(train),
            "test_length":len(test),
            "predict_t":predict_t,
            "train_t":train_t
        }

        log_dict.update(metrics_dict)

        return log_dict, predict

    # 一个预测的实例
    def demo(self):
        x_list = np.linspace(0,100,1200)
        y_list = np.sin(x_list)

        train_data = y_list[0:1000]
        test_data = y_list[1000:1200]

        print(f"len(train_data):{len(train_data)}")

        self.ordinary_param_dict = {
            "seq_len": 20,
            "pred_len": 10,

        }

        print(f"开始评估")
        log_dict, predict_result = self.evaluate(train=train_data, test=test_data)

        print(f"log_dict:{log_dict}")
        print(f"predict_result:{predict_result}")

        my_plotter = Plotter()

        my_plotter.plot_lines(
            y_list=[predict_result, test_data],
            legend_label_list=["Predict", "Real"],
        )






        
        





    
