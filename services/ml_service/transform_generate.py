from pathlib import Path
import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import TargetEncoder


class TransformData:

    def __init__(self, df):
        self.cat_features = [
            "sexo",
            "ind_nuevo",
            "indrel",
            "tiprel_1mes",
            "indext",
            "canal_entrada",
            "cod_prov",
            "nomprov",
            "ind_actividad_cliente",
            "segmento",
            "product_name",
        ]

        self.products = [
            "ind_nom_pens_ult1",
            "ind_ctop_fin_ult1",
            "ind_reca_fin_ult1",
            "ind_cno_fin_ult1",
            "ind_cco_fin_ult1",
            "ind_dela_fin_ult1",
            "ind_valo_fin_ult1",
            "ind_ctpp_fin_ult1",
            "ind_fond_fin_ult1",
            "ind_nomina_ult1",
            "ind_tjcr_fin_ult1",
            "ind_ecue_fin_ult1",
            "ind_recibo_ult1",
        ]

        self.df = df

        base_dir = Path(__file__).parent.parent
        self.model_path = str(base_dir / "models" / "dict_encoders.pkl")
        self.load_dict_encoders(self.model_path)

    def load_dict_encoders(self, path):
        """Загружаем словарь энкодеров для категориальных переменных.
        Args:
            model_path (str): Путь.
        """
        try:
            with open(path, "rb") as f:
                self.dict_encoders = pickle.load(f)
        except Exception as e:
            print(f"Failed to load encoders: {e}")

    def transform_cat_features(self):
        """Кодирование категориальных перменных"""
        # self.df = self.df.rename(
        #     columns={col: f"{col}_first" for col in self.cat_features}
        # )

        for col in self.cat_features:
            try:
                self.df[col] = self.df[col].fillna(-99)
                self.df[col] = self.df[col].astype("int")
            except:
                self.df[col] = self.df[col].fillna("non_type")
                self.df[col] = self.df[col].astype("str")

        for col in self.cat_features:
            self.df[f"{col}_first"] = self.df[col]
            self.df[col] = self.dict_encoders[col].transform(self.df[[col]])

        return self.df

    def generate_features(self):
        """Генерация новых переменных"""

        current_dir = Path(__file__).parent.parent
        data_path = current_dir / "data" / "df_long_cumsum.parquet"

        history_df = pd.read_parquet(data_path)

        try:
            history_df["fecha_dato"] = pd.to_datetime(history_df["fecha_dato"])
            self.df = self.df.merge(
                history_df, how="left", on=["ncodpers", "fecha_dato", "product_name"]
            )
        except:
            self.df["cumsum_id_product"] = 0

        del history_df

        self.df["ult_fec_cli_1t"] = pd.to_datetime(self.df["ult_fec_cli_1t"])

        mask = ~self.df["ult_fec_cli_1t"].isna()
        try:
            self.df.loc[mask, "period_prem"] = (
                self.df.loc[mask, "fecha_dato"] - self.df.loc[mask, "ult_fec_cli_1t"]
            ).dt.days
        except:
            self.df["period_prem"] = -1

        self.df["period_prem"] = self.df["period_prem"].fillna(-1)
        self.df.loc[self.df["period_prem"] < 0, "period_prem"] = -1

        return self.df

    def generate_target(self):
        """Добавляем продукты-кандидаты"""
        self.df = self.df.merge(
            pd.DataFrame(self.products, columns=["product_name"]), how="cross"
        )

        return self.df

    def correct_data(self):
        self.df["age"] = self.df["age"].apply(
            lambda x: x.strip() if isinstance(x, str) else x
        )
        self.df["age"] = self.df["age"].replace("NA", np.nan)
        self.df["age"] = self.df["age"].astype(float)

        self.df["fecha_dato"] = pd.to_datetime(self.df["fecha_dato"])
        self.df["fecha_alta"] = pd.to_datetime(self.df["fecha_alta"])
        self.df["ult_fec_cli_1t"] = pd.to_datetime(self.df["ult_fec_cli_1t"])

        self.df["antiguedad"] = self.df["antiguedad"].apply(
            lambda x: x.strip() if isinstance(x, str) else x
        )
        self.df["antiguedad"] = self.df["antiguedad"].replace("NA", np.nan)
        self.df["antiguedad"] = self.df["antiguedad"].astype(float)
        self.df.loc[self.df["antiguedad"] == -999999, "antiguedad"] = np.nan

        self.df["indrel_1mes"] = self.df["indrel_1mes"].replace("P", 99)
        self.df["indrel_1mes"] = self.df["indrel_1mes"].astype("float")

        # удалим признаки где более 99% заполнено одним значением
        cols_to_del = [
            "ind_empleado",
            "pais_residencia",
            "indrel_1mes",
            "indresi",
            "conyuemp",
            "indfall",
            "tipodom",
        ]
        for col in cols_to_del:
            if col in self.df.columns:
                self.df = self.df.drop(col, axis=1)
            else:
                continue

        return self.df

    def preprocess_data(self):
        self.df = self.correct_data()
        self.df = self.generate_target()
        self.df = self.generate_features()
        self.df = self.transform_cat_features()

        return self.df
