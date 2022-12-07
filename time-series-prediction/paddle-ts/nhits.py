from basic import Basic_model
from sklearn.preprocessing import StandardScaler
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

        self.set_model_class(NHiTSModel)
        pass



if __name__ == "__main__":
    m = Nhits_model()
    m.demo()
