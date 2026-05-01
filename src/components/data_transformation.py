import os
import sys
import glob
import pandas as pd
from dataclasses import dataclass
from src.logger import logging
from src.exception import CustomException

@dataclass
class DataTransformationConfig:
    aral_master_path: str = os.path.join('data', 'processed', 'aral_sea_master.csv')
    regions_master_path: str = os.path.join('data', 'processed', 'regions_master.csv')

class DataTransformation:
    def __init__(self):
        self.transformation_config = DataTransformationConfig()

    def initiate_data_transformation(self, raw_data_dir):
        logging.info("Data Transformation (Ma'lumotlarni birlashtirish) boshlandi")
        try:
            os.makedirs(os.path.dirname(self.transformation_config.regions_master_path), exist_ok=True)

            all_csv_files = glob.glob(os.path.join(raw_data_dir, "*.csv"))
            region_dfs = []

            for file_path in all_csv_files:
                file_name = os.path.basename(file_path)
                df = pd.read_csv(file_path)

                if "aral" in file_name.lower():
                    df.to_csv(self.transformation_config.aral_master_path, index=False)
                    logging.info("Aral Sea fayli alohida saqlandi.")
                else:
                    # ===== XATONI TO'G'RILASH QISMI =====
                    # Agar 'Viloyat' ustuni yo'q bo'lsa, fayl nomidan olib avtomatik qo'shamiz
                    # Masalan: 'andijon.csv' yoki 'Andijon.csv' -> 'Andijon'
                    if 'Viloyat' not in df.columns:
                        viloyat_nomi = file_name.replace('.csv', '').capitalize()
                        df['Viloyat'] = viloyat_nomi
                    
                    region_dfs.append(df)

            if region_dfs:
                regions_master = pd.concat(region_dfs, ignore_index=True)
                regions_master.to_csv(self.transformation_config.regions_master_path, index=False)
                logging.info(f"Jami {len(region_dfs)} ta viloyat fayllari birlashtirildi va saqlandi.")

            return (
                self.transformation_config.aral_master_path,
                self.transformation_config.regions_master_path
            )

        except Exception as e:
            logging.error("Data Transformation jarayonida xatolik yuz berdi")
            raise CustomException(e, sys)