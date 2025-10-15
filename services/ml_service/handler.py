from pathlib import Path
import pickle
import pandas as pd
import numpy as np

from transform_generate import TransformData


class FastApiHandler:
    """
    Класс FastApiHandler, который обрабатывает запрос и возвращает предсказание.
    В качестве предсказаний будем отдавать названия продуктов, для которых вероятность приобретения более 0.5
    """

    def __init__(self):
        """Инициализация переменных класса."""

        self.key_value = "user_id"

        base_dir = Path(__file__).parent.parent
        self.model_path = str(base_dir / "models" / "logreg_model.pkl")
        self.load_model(model_path=self.model_path)

        # необходимые параметры для предсказаний модели оттока
        self.required_model_params = [
            "sexo",
            "age",
            "ind_nuevo",
            "antiguedad",
            "indrel",
            "tiprel_1mes",
            "indext",
            "canal_entrada",
            "cod_prov",
            "nomprov",
            "ind_actividad_cliente",
            "renta",
            "segmento",
            "product_name",
        ]

        self.cols = [
            "sexo",
            "age",
            "ind_nuevo",
            "antiguedad",
            "indrel",
            "tiprel_1mes",
            "indext",
            "canal_entrada",
            "cod_prov",
            "nomprov",
            "ind_actividad_cliente",
            "renta",
            "segmento",
            "product_name",
            "period_prem",
            "cumsum_id_product",
            # "ncodpers",
        ]

    def load_model(self, model_path: str):
        """Загружаем обученную модель.
        Args:
            model_path (str): Путь до модели.
        """
        try:
            with open(model_path, "rb") as f:
                self.model = pickle.load(f)
        except Exception as e:
            print(f"Failed to load model: {e}")

    def producte_predict(self, model_params: dict) -> float:
        """Предсказываем цену квартиры.

        Args:
            model_params (dict): Параметры для модели.

        Returns:
            float — цена.
        """
        df_model_params = pd.DataFrame({k: [v] for k, v in model_params.items()})

        transformer = TransformData(df_model_params)
        df_model_params = transformer.preprocess_data()
        
        df_model_params[self.cols] = df_model_params[
            self.cols
        ].fillna(0)

        result = self.model.predict_proba(df_model_params[self.cols])
        df_model_params['preds'] = result[:,1]
        result = df_model_params[df_model_params['preds']>0.5]['product_name_first'].to_list()

        return result

    def validate_params(self, params: dict) -> bool:
        """Разбираем запрос и проверяем его корректность.

        Args:
            params (dict): Словарь параметров запроса.

        Returns:
            - **dict**: Cловарь со всеми параметрами запроса.
        """
        if self.check_required_query_params(params):
            print("All query params exist")
        else:
            print("Not all query params exist")
            return False

        return True

    def handle(self, params):
        """Функция для обработки входящих запросов по API. Запрос состоит из параметров.

        Args:
            params (dict): Словарь параметров запроса.

        Returns:
            - **dict**: Словарь, содержащий результат выполнения запроса.
        """
        try:
            # валидируем запрос к API
            if not self.validate_params(params):
                print("Error while handling request")
                response = {"Error": "Problem with parameters", "par": params}

            else:
                model_params = params["model_params"]
                user_id = params[self.key_value]
                print(
                    f"Predicting for user_id: {user_id} and model_params:\n{model_params}"
                )
                # получаем предсказания модели
                products = self.producte_predict(model_params)
                response = {
                    "user_id": user_id,
                    "products": products,
                }
        except Exception as e:
            print(f"Error while handling request: {e}")
            return {"Error": "Problem with request"}
        else:
            return response

    def check_required_model_params(self, model_params: dict) -> bool:
        """Проверяем параметры пользователя на наличие обязательного набора.

        Args:
            model_params (dict): Параметры пользователя для предсказания.

        Returns:
            bool: True — если есть нужные параметры, False — иначе
        """
        if set(model_params.keys()) == set(self.required_model_params):
            return True
        return False

    def check_required_query_params(self, query_params: dict) -> bool:
        """Проверяем параметры запроса на наличие обязательного набора.

        Args:
            query_params (dict): Параметры запроса.

        Returns:
            bool: True — если есть нужные параметры, False — иначе
        """
        if self.key_value not in query_params or "model_params" not in query_params:
            return False

        return True


if __name__ == "__main__":

    test_params = {
        "user_id": 1375586,
        "model_params": {
            "fecha_dato": "2016-05-28",
            "ncodpers": 1375586,
            "ind_empleado": "N",
            "pais_residencia": "ES",
            "sexo": "H",
            "age": 36,
            "fecha_alta": "2015-01-12",
            "ind_nuevo": 0.0,
            "antiguedad": 16,
            "indrel": 1.0,
            "ult_fec_cli_1t": np.nan,
            "indrel_1mes": "1.0",
            "tiprel_1mes": "A",
            "indresi": "S",
            "indext": "N",
            "conyuemp": np.nan,
            "canal_entrada": "KHL",
            "indfall": "N",
            "tipodom": 1.0,
            "cod_prov": 29.0,
            "nomprov": "MALAGA",
            "ind_actividad_cliente": 1.0,
            "renta": 87218.1,
            "segmento": "02 - PARTICULARES",
        },
    }

    # создаём обработчик запросов для API
    handler = FastApiHandler()

    # делаем тестовый запрос
    response = handler.handle(test_params)
    print(response)
