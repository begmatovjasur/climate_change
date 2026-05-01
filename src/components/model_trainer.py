import os
import sys
import pandas as pd
import numpy as np
from dataclasses import dataclass
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score
from src.logger import logging
from src.exception import CustomException

@dataclass
class ModelTrainerConfig:

    future_data_path: str = os.path.join("data", "processed", "future_predictions.csv")

class ModelTrainer:
    def __init__(self):
        self.model_trainer_config = ModelTrainerConfig()

    def initiate_model_trainer(self, regions_data_path):
        try:
            logging.info("Model Trainer boshlandi. Tarixiy ma'lumotlar o'qilmoqda...")
            df = pd.read_csv(regions_data_path)

            viloyatlar = df['Viloyat'].dropna().unique()
            parametrlar = [col for col in df.columns if col not in ['Year', 'Viloyat', 'Category', 'Decade', 'Decade_Str']]

            future_years = np.arange(2025, 2051)
            future_results = []

            models = {
                "Linear Regression": LinearRegression(),
                "Ridge Regression": Ridge(),
                "Lasso Regression": Lasso(),
                "Polynomial Regression (Degree 2)": Pipeline([('poly', PolynomialFeatures(degree=2)), ('linear', LinearRegression())]),
                "Polynomial Regression (Degree 3)": Pipeline([('poly', PolynomialFeatures(degree=3)), ('linear', LinearRegression())])
            }

            for viloyat in viloyatlar:
                df_viloyat = df[df['Viloyat'] == viloyat]

                for parametr in parametrlar:
                    temp_df = df_viloyat[['Year', parametr]].dropna()
                    if len(temp_df) < 10:
                        continue

                    X = temp_df[['Year']]
                    y = temp_df[parametr]

                    best_model_name = ""
                    best_model = None
                    best_score = -float("inf")

                    for name, model in models.items():
                        model.fit(X, y)
                        y_pred = model.predict(X)
                        score = r2_score(y, y_pred)
                        
                        if score > best_score:
                            best_score = score
                            best_model = model
                            best_model_name = name

                    X_future = pd.DataFrame({'Year': future_years})
                    y_future_pred = best_model.predict(X_future)

                    std_dev = np.std(y - best_model.predict(X)) 
                    noise = np.random.normal(0, std_dev * 0.8, len(future_years))
                    y_future_realistic = y_future_pred + noise

                    for i, year in enumerate(future_years):
                        future_results.append({
                            'Viloyat': viloyat,
                            'Year': year,
                            'Parameter': parametr,
                            'Predicted_Value': y_future_realistic[i]
                        })

            future_df = pd.DataFrame(future_results)
            os.makedirs(os.path.dirname(self.model_trainer_config.future_data_path), exist_ok=True)
            future_df.to_csv(self.model_trainer_config.future_data_path, index=False)

            logging.info(f"Model o'qitish yakunlandi. Haqiqiy bashoratlar saqlandi: {self.model_trainer_config.future_data_path}")
            return self.model_trainer_config.future_data_path

        except Exception as e:
            logging.error("Model Trainer jarayonida xatolik yuz berdi")
            raise CustomException(e, sys)

if __name__ == "__main__":
    trainer = ModelTrainer()
    trainer.initiate_model_trainer("data/processed/regions_master.csv")
    print("Bashoratlar muvaffaqiyatli hisoblandi va saqlandi!")