import os
import sys
import glob
from dataclasses import dataclass
from src.logger import logging
from src.exception import CustomException
from src.components.data_transformation import DataTransformation

@dataclass
class DataIngestionConfig:
    raw_data_dir: str = os.path.join('notebook', 'data', 'joined_data')

class DataIngestion:
    def __init__(self):
        self.ingestion_config = DataIngestionConfig()

    def initiate_data_ingestion(self):
        logging.info("Data Ingestion (Ma'lumotlarni qabul qilish) boshlandi")
        try:
            raw_dir = self.ingestion_config.raw_data_dir
            
            if not os.path.exists(raw_dir):
                raise Exception(f"Papka topilmadi: {raw_dir}. Jupyter'dagi fayllar saqlanganini tekshiring.")

            csv_files = glob.glob(os.path.join(raw_dir, "*.csv"))
            logging.info(f"Jami {len(csv_files)} ta tayyor CSV fayl topildi.")

            return raw_dir
            
        except Exception as e:
            logging.error("Data Ingestion jarayonida xatolik yuz berdi")
            raise CustomException(e, sys)

if __name__ == "__main__":
    ingestion = DataIngestion()
    raw_data_directory = ingestion.initiate_data_ingestion()
    
    transformation = DataTransformation()
    aral_path, regions_path = transformation.initiate_data_transformation(raw_data_directory)
    
    print(f"Jarayon muvaffaqiyatli yakunlandi!\nOrol ma'lumotlari: {aral_path}\nViloyatlar ma'lumotlari: {regions_path}")