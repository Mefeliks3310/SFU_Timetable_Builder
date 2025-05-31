# ui/main_window.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from logic.main import MainLogic


class MainWindow:
    def __init__(self, logic: MainLogic):
        self.logic = logic

        self.window = tk.Tk()
        self.window.title("SFU TimeTable Builder")
        self.window.geometry("500x400")
        self.window.configure(bg="#FF7900")
        self.window.resizable(False, False)

        self.setup_ui()
        self.window.mainloop()



    def setup_ui(self):
        icon = tk.PhotoImage(file="content/sfu_icon.png")
        self.window.iconphoto(True, icon)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.TButton",
            background="White",
            foreground="black",
            font=("Arial", 12, "bold"),
            borderwidth=2,
            relief="flat",
            padding=10)

        style.configure("Pressed.TButton",
            background="#ff8a00",
            foreground="black",
            font=("Arial", 12, "bold"),
            borderwidth=2,
            relief="sunken",
            padding=10)

        def on_button_press(button):
            button.configure(style="Pressed.TButton")

        def on_button_release(button):
            button.configure(style="Custom.TButton")

        logo = tk.PhotoImage(file="content/sfu_logo.png")
        logo_label = tk.Label(self.window, image=logo, bg="#FF7900")
        logo_label.image = logo  # сохранить ссылку
        logo_label.pack(pady=(0,20))

        button_frame = tk.Frame(self.window, bg="#FF7900")
        button_frame.pack(pady=20)

        btn_load = ttk.Button(button_frame, text="Загрузить конфиг",
                              style="Custom.TButton",
                              command=self.load_config)
        btn_load.pack(side=tk.LEFT, padx=10)
        btn_load.bind("<Button-1>", lambda e: on_button_press(btn_load))
        btn_load.bind("<ButtonRelease-1>", lambda e: on_button_release(btn_load))

        btn_create_schedule = ttk.Button(button_frame, text="Скачать таблицу",
                                         style="Custom.TButton",
                                         command=self.open_window_combine_schedulde)
        btn_create_schedule.pack(side=tk.LEFT, padx=10)
        btn_create_schedule.bind("<Button-1>", lambda e: on_button_press(btn_create_schedule))
        btn_create_schedule.bind("<ButtonRelease-1>", lambda e: on_button_release(btn_create_schedule))

    def load_config(self):
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
        if not file_path:
            return

        try:
            self.logic.load_config_file(file_path)
            messagebox.showinfo("Успех", "Файл успешно загружен.")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")

    def open_window_combine_schedulde(self):
        if len(self.logic.teachers) == 0:
            messagebox.showwarning("Нет данных", "Сначала загрузите конфигурационный файл.")
            return
        self.logic.create_combined_schedule()
        DownloadWindow(self.window, self.logic)


class DownloadWindow(tk.Toplevel):
    def __init__(self, master, logic):
        super().__init__(master)
        self.logic = logic
        self.title("Состояние загрузки")
        self.geometry("700x500")
        self.configure(bg="white")
        self.resizable(False, False)

        self.status_frame = tk.Frame(self, bg="white")
        self.status_frame.pack(pady=20, fill=tk.BOTH, expand=True)

        self.update_status_list()

        button_frame = tk.Frame(self, bg="white")
        button_frame.pack(pady=10)

        self.btn_refresh = ttk.Button(button_frame, text="Обновить таблицу", state=tk.DISABLED)
        self.btn_refresh.pack(side=tk.LEFT, padx=10)

        self.btn_download = ttk.Button(button_frame, text="Скачать таблицу", state=tk.DISABLED)
        self.btn_download.pack(side=tk.LEFT, padx=10)

    def update_status_list(self):
        for widget in self.status_frame.winfo_children():
            widget.destroy()

        statuses = self.logic.get_teacher_statuses()
        for status in statuses:
            icon = "✅" if statuses[status] == "ok" else "❌"
            label = tk.Label(self.status_frame, text=f"{status} {icon} {statuses[status]}",
                             anchor="w", font=("Arial", 12), bg="white")
            label.pack(fill=tk.X, padx=20, pady=2)



if __name__ == "__main__":
    logic = MainLogic()
    ui = MainWindow(logic)
