from basic import Basic_model
from sklearn.preprocessing import StandardScaler
from paddlets.models.forecasting import RNNBlockRegressor, LSTNetRegressor, MLPRegressor, NBEATSModel, TCNRegressor, NHiTSModel, TransformerModel, InformerModel, DeepARModel


class Informer_model(Basic_model):
    def __init__(self, name="Informer_model", scaler=StandardScaler(), model_class=InformerModel, ordinary_param_dict=None, unique_param_dict=None):
        super().__init__()
        self.name = name
        self.scaler = scaler
        self.model_class = model_class
        if ordinary_param_dict != None:
            self.ordinary_param_dict.update(ordinary_param_dict)
        if unique_param_dict != None:
            self.unique_param_dict.update(unique_param_dict)

        pass



if __name__ == "__main__":
    m = Informer_model()
    m.demo()
