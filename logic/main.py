# logic/main_logic.py
import os
import pandas as pd
from tkinter import messagebox, filedialog


class MainLogic:
    def __init__(self):
        self.teachers = []

    def load_data(self, file_path):
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path, header=None)
        else:
            return pd.read_excel(file_path, engine='openpyxl', header=None, names=["фио", "ссылка"])

    def load_config_file(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in ['.xlsx', '.xls', '.xlsm', '.xlsb', '.csv']:
            raise ValueError("Недопустимый формат файла")

        if ext == '.csv':
            df = pd.read_csv(file_path, header=None)
        else:
            df = pd.read_excel(file_path, engine='openpyxl', header=None, names=["фио", "ссылка"])

        self.teachers = df.to_dict("records")

    def create_combined_schedule(self):
        if not self.teachers:
            raise ValueError("Нет данных", "Сначала загрузите конфигурационный файл.")

        # Заглушка (в будущем сюда - логика объединения расписания)
        messagebox.showinfo("Готово", "Объединённое расписание успешно создано!")
