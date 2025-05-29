from tkinter import messagebox, filedialog
import os

def select_config_file():
    messagebox.showinfo(
        "Информация о файле конфигурации",
        "Файл конфигурации представляет собой таблицу из двух колонок.\n"
        "В первой колонке - ФИО преподавателя,\n"
        "во второй колонке - гиперссылка на этого преподавателя на сайте расписания СФУ.\n\n"
        "Пожалуйста, проверьте файл конфигурации во избежание возможных ошибок."
    )
    file_path = filedialog.askopenfilename(
        title="Выберите файл конфигурации",
        filetypes=(
            ("Excel файлы", "*.xlsx *.xls *.xlsm *.xlsb *.csv"),
            ("Все файлы", "*.*")
        )
    )
    if file_path:
        # Проверяем расширение файла
        ext = os.path.splitext(file_path)[1].lower()
        valid_extensions = ['.xlsx', '.xls', '.xlsm', '.xlsb','.csv']

        if ext not in valid_extensions:
            messagebox.showerror(
                "Ошибка",
                "Выбран файл недопустимого формата!\n"
                "Пожалуйста, выберите файл Excel (.xlsx, .xls и т.д.) или CSV"
            )
            return

        # Здесь происходит дальнейшая работа с файлом