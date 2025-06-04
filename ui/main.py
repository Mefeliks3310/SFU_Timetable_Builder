import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from logic.main import MainLogic


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


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
        icon_path = resource_path("content/sfu_icon.png")
        icon = tk.PhotoImage(file=icon_path)
        self.window.iconphoto(True, icon)
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

        logo_path = resource_path("content/sfu_logo.png")
        logo = tk.PhotoImage(file=logo_path)
        logo_label = tk.Label(self.window, image=logo, bg="#FF7900")
        logo_label.image = logo  # сохранить ссылку
        logo_label.pack(pady=(0, 20))

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
                                        command=self.open_window_combine_schedule)
        btn_create_schedule.pack(side=tk.LEFT, padx=10)
        btn_create_schedule.bind("<Button-1>", lambda e: on_button_press(btn_create_schedule))
        btn_create_schedule.bind("<ButtonRelease-1>", lambda e: on_button_release(btn_create_schedule))

    def load_config(self):
        messagebox.showinfo(
            "Информация о файле конфигурации",
            "Файл конфигурации представляет собой таблицу из двух колонок.\n"
            "В первой колонке - ФИО преподавателя,\n"
            "во второй колонке - гиперссылка на преподавателя на сайте расписания СФУ.\n\n"
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

    def open_window_combine_schedule(self):
        if len(self.logic.teachers) == 0:
            messagebox.showwarning("Нет данных", "Сначала загрузите конфигурационный файл.")
            return
        # Проверяем, существует ли уже окно и не было ли оно уничтожено
        if hasattr(self, 'download_window') and self.download_window.winfo_exists():
            # Окно уже существует, поднимаем его на передний план
            self.download_window.lift()
            return
        # Создаем новое окно и сохраняем ссылку на него
        self.download_window = DownloadWindow(self.window, self.logic)


class DownloadWindow(tk.Toplevel):
    def __init__(self, master, logic):
        super().__init__(master)
        self.logic = logic
        self.title("Состояние загрузки")
        self.geometry("700x500")
        self.configure(bg="#FF7900")
        self.resizable(False, False)

        self.status_frame = tk.Frame(self, bg="white")
        self.status_frame.pack(pady=20, fill=tk.BOTH, expand=True)

        self.loading_label = tk.Label(self, text="Загрузка расписаний...", font=("Arial", 12), bg="white")
        self.loading_label.pack(pady=10)
        self.progress = ttk.Progressbar(self, mode='indeterminate', length=300)
        self.progress.pack(pady=10)
        self.progress.start()

        style = ttk.Style()
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

        button_frame = tk.Frame(self, bg="#FF7900")
        button_frame.pack(pady=10)

        self.btn_refresh = ttk.Button(button_frame, text="Обновить таблицу", style="Custom.TButton",
                                     command=self.refresh_schedule, state=tk.DISABLED)
        self.btn_refresh.pack(side=tk.LEFT, padx=10)

        self.btn_download = ttk.Button(button_frame, text="Скачать таблицу", style="Custom.TButton",
                                      command=self.download_schedule, state=tk.DISABLED)
        self.btn_download.pack(side=tk.LEFT, padx=10)

        # Запускаем загрузку расписаний в отдельном потоке
        threading.Thread(target=self.load_schedules, daemon=True).start()

    def load_schedules(self):
        try:
            def update_callback(teacher_name, schedule):
                status = "ok" if isinstance(schedule, tuple) else schedule
                self.after(0, lambda: self.update_status_list(teacher_name, status))

            self.logic.create_combined_schedule(check_only=True, callback=update_callback)
            self.after(0, self.stop_loading)
        except ValueError as e:
            self.after(0, lambda: messagebox.showerror("Ошибка", str(e)))
            self.after(0, self.stop_loading)

    def stop_loading(self):
        self.progress.stop()
        self.progress.pack_forget()
        self.loading_label.pack_forget()
        self.btn_download.config(state=tk.NORMAL)
        self.btn_refresh.config(state=tk.NORMAL)

    def update_status_list(self, teacher_name, status):
        # Обновляем или добавляем статус конкретного преподавателя
        for widget in self.status_frame.winfo_children():
            if widget["text"].startswith(teacher_name):
                widget.destroy()
                break

        icon = "✅" if status == "ok" else "❌"
        label = tk.Label(self.status_frame, text=f"{teacher_name} {icon} {status}",
                         anchor="w", font=("Arial", 12), bg="white")
        label.pack(fill=tk.X, padx=20, pady=2)

    def refresh_schedule(self):
        self.btn_refresh.config(state=tk.DISABLED)
        self.btn_download.config(state=tk.DISABLED)
        for widget in self.status_frame.winfo_children():
            widget.destroy()
        self.loading_label.pack(pady=10)
        self.progress.pack(pady=10)
        self.progress.start()
        threading.Thread(target=self.load_schedules, daemon=True).start()

    def download_schedule(self):
        try:
            self.logic.create_combined_schedule(save_file=True)
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
        except PermissionError as e:
            messagebox.showerror("Ошибка", str(e))