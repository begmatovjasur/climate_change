import sys
from src.components.model_trainer import ModelTrainer
from src.logger import logging
from src.exception import CustomException

class TrainPipeline:
    def __init__(self):
        self.model_trainer = ModelTrainer()

    def run_pipeline(self):
        try:
            logging.info("Training Pipeline (O'qitish zanjiri) boshlandi...")
            
            
            data_path = "data/processed/regions_master.csv"
            
            logging.info("Model Trainer ishga tushirilmoqda...")
            future_data_path = self.model_trainer.initiate_model_trainer(data_path)
            
            logging.info(f"Training Pipeline muvaffaqiyatli yakunlandi! Natija: {future_data_path}")
            
        except Exception as e:
            raise CustomException(e, sys)

if __name__ == "__main__":
    pipeline = TrainPipeline()
    pipeline.run_pipeline()