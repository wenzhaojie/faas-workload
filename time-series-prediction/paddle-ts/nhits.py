from basic import Basic_model
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
from paddlets import TSDataset
from paddlets.models.forecasting import RNNBlockRegressor, LSTNetRegressor, MLPRegressor, NBEATSModel, TCNRegressor, NHiTSModel, TransformerModel, InformerModel, DeepARModel


class Nhits_model(Basic_model):
    def __init__(self, name="Nhits_model", scaler=StandardScaler(), ordinary_param_dict=None, unique_param_dict=None):
        super().__init__()
        self.name = name
        self.scaler = scaler
        if ordinary_param_dict != None:
            self.ordinary_param_dict.update(ordinary_param_dict)
        if unique_param_dict != None:
            self.unique_param_dict.update(unique_param_dict)
        pass

    def train(self, history):
        # 转换np数据格式
        history = np.array(history)
        # 先初始化 dataframe
        freq = self.ordinary_param_dict.get("freq", "1min")
        train_df = pd.DataFrame(
            {
                'time_col': pd.date_range('2022-01-01', periods=len(history), freq=freq),
                'value': history
            }
        )
        train_dataset = TSDataset.load_from_dataframe(
            train_df,  # Also can be path to the CSV file
            time_col='time_col',
            target_cols='value',
            freq=freq
        )

        # 初始化模型
        seq_len = self.ordinary_param_dict.get("seq_len")
        pred_len = self.ordinary_param_dict.get("pred_len")

        self.model = NHiTSModel(
            in_chunk_len=seq_len,
            out_chunk_len=pred_len,
        )

        # 开始训练
        self.model.fit(train_dataset)
        pass


    def predict(self, history, predict_window) -> list:
        # 转换np数据格式
        history = np.array(history)
        freq = self.ordinary_param_dict.get("freq", "1min")
        # 先初始化 dataframe
        history_df = pd.DataFrame(
            {
                'time_col': pd.date_range('2022-01-01', periods=len(history), freq=freq),
                'value': history
            }
        )
        history_dataset = TSDataset.load_from_dataframe(
            history_df,  # Also can be path to the CSV file
            time_col='time_col',
            target_cols='value',
            freq=freq
        )
        predicted_dataset = self.model.predict(history_dataset, )
        pred = predicted_dataset.to_numpy().reshape(-1, ).tolist()
        assert predict_window <= len(pred)
        pred = pred[0:predict_window]

        return pred


