from basic import Basic_model
from sklearn.preprocessing import StandardScaler
from paddlets.models.forecasting import RNNBlockRegressor, LSTNetRegressor, MLPRegressor, NBEATSModel, TCNRegressor, NHiTSModel, TransformerModel, InformerModel, DeepARModel


class Nbeats_model(Basic_model):
    def __init__(self, name="Nbeats_model", scaler=StandardScaler(), model_class=NBEATSModel, ordinary_param_dict=None, unique_param_dict=None):
        super().__init__()
        self.name = name
        self.scaler = scaler
        self.model_class = model_class
        self.update_param_dict(ordinary_param_dict=ordinary_param_dict, unique_param_dict=unique_param_dict)
        pass



if __name__ == "__main__":
    m = Nbeats_model()
    m.demo()
