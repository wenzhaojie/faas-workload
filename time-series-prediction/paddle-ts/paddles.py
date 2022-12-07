from .basic import Basic_model
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import numpy as np
import pandas as pd
from paddlets import TSDataset
from paddlets.models.forecasting import RNNBlockRegressor, LSTNetRegressor, MLPRegressor, NBEATSModel, TCNRegressor, NHiTSModel, TransformerModel, InformerModel, DeepARModel
import copy
import time


class NHiTSModel_model(Basic_model):
    def __init__(self, name="NHiTSModel", scaler=StandardScaler()):
        super().__init__(name, scaler)
        self.name = name
        self.scaler = scaler
        self.default_extra_parameters = {
            "seq_len": 1440 * 3,
            "pred_len": 1440,
            "history_error_correct": False,
            "is_scaler": False,
            "use_future": True,
            "is_round": False,
            "num_stacks": 3, # Stack数量。
            "num_blocks": 3, # 构成每个stack的block数量。
            "num_layers": 2, # 每个block中分叉结构前的全连接层数量。
            "layer_widths": 512, # 每个block中全连接层的神经元数量，如果传入list，则list长度必须等于num_stacks，且list中每个元素对应于当前层的神经元数量。如果传入整数，则每个stack中的block中具有相同的神经元数量。
        }
        print(f"初始化 {self.name}!")
        pass

    def train(self, history, extra_parameters=None):
        # 转换np数据格式
        history = np.array(history)
        # 先初始化 dataframe
        train_df = pd.DataFrame(
            {
                'time_col': pd.date_range('2022-01-01', periods=len(history), freq='1min'),
                'value': history
            }
        )
        train_dataset = TSDataset.load_from_dataframe(
            train_df,  # Also can be path to the CSV file
            time_col='time_col',
            target_cols='value',
            freq='1min'
        )

        # 初始化模型
        model_parameters = copy.deepcopy(self.default_extra_parameters)
        if extra_parameters != None:
            model_parameters.update(extra_parameters)
        
        seq_len = model_parameters["seq_len"]
        pred_len = model_parameters["pred_len"]
        history_error_correct = model_parameters["history_error_correct"]
        is_scaler = model_parameters["is_scaler"]
        use_future = model_parameters["use_future"]
        is_round = model_parameters["is_round"]


        self.model = NHiTSModel(
            in_chunk_len=seq_len,
            out_chunk_len=pred_len,
        )

        # 开始训练
        start_t = time.time()
        self.model.fit(train_dataset)
        pass

    def predict(self, history, predict_window, extra_parameters=None):
        # 转换np数据格式
        history = np.array(history)
        # 先初始化 dataframe
        history_df = pd.DataFrame(
            {
                'time_col': pd.date_range('2022-01-01', periods=len(history), freq='1min'),
                'value': history
            }
        )
        history_dataset = TSDataset.load_from_dataframe(
            history_df,  # Also can be path to the CSV file
            time_col='time_col',
            target_cols='value',
            freq='1min'
        )
        predicted_dataset = self.model.predict(history_dataset, )
        pred = predicted_dataset.to_numpy().reshape(-1,).tolist()
        assert predict_window <= len(pred)
        pred = pred[0:predict_window]

        return pred

    def recursive_predict(self, history, predict_window):
        # 转换np数据格式
        history = np.array(history)
        # 先初始化 dataframe
        history_df = pd.DataFrame(
            {
                'time_col': pd.date_range('2022-01-01', periods=len(history), freq='1min'),
                'value': history
            }
        )
        history_dataset = TSDataset.load_from_dataframe(
            history_df,  # Also can be path to the CSV file
            time_col='time_col',
            target_cols='value',
            freq='1min'
        )
        # 滚动预测
        rolling_predicted_dataset = self.model.recursive_predict(tsdataset=history_dataset, predict_length=predict_window)
        pred = rolling_predicted_dataset.to_numpy().reshape(-1,).tolist()
        assert predict_window <= len(pred)
        pred = pred[0:predict_window]

        return pred



if __name__ == "__main__":
    m = NHiTSModel_model()
    m.demo()