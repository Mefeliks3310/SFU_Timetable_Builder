import tkinter as tk
from tkinter import ttk
from logic.main import select_config_file
def main():
    # загрузка окна
    window = tk.Tk()
    window.title("SFU TimeTable Builder")
    window.geometry("500x400")
    window.configure(bg="#FF7900")
    window.resizable(False,False)

    # иконка
    icon = tk.PhotoImage(file=r"content\sfu_icon.png")
    window.iconphoto(True, icon)
    # стиль кнопок
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Custom.TButton",
                    background="White",
                    foreground="black",
                    font=("Arial", 12, "bold"),
                    borderwidth=2,
                    relief="flat",
                    padding=10)
    style.map("Custom.TButton",
              background=[("active", "#eae9e9")])

    # если кнопка нажата - новый стиль
    def on_button_press(button):
        button.configure(style="Pressed.TButton")
    # если кнопку отжали - возварщаем стиль
    def on_button_release(button):
        button.configure(style="Custom.TButton")

    style.configure("Pressed.TButton",
                    background="#ff8а00",
                    foreground="black",
                    font=("Arial", 12, "bold"),
                    borderwidth=2,
                    relief="flat",
                    padding=10)
    # шапка

    logo = tk.PhotoImage(file=r"content/sfu_logo.png")
    logo_label = tk.Label(window, image=logo)
    logo_label.pack(side=tk.TOP, pady=20)


    button_frame = tk.Frame(window, bg="#FF7900")
    button_frame.pack(side=tk.TOP, pady=20)

    # кнопка загрузки конфига
    button_admin = ttk.Button(button_frame, text="Загрузить конфиг", style="Custom.TButton", command=select_config_file)
    button_admin.pack(side=tk.LEFT, padx=10)
    button_admin.bind("<Button-1>", lambda e: on_button_press(button_admin))
    button_admin.bind("<ButtonRelease-1>", lambda e: on_button_release(button_admin))

    # кнопка скачать таблицу
    button_user = ttk.Button(button_frame, text="Скачать таблицу", style="Custom.TButton")
    button_user.pack(side=tk.LEFT, padx=10)
    button_user.bind("<Button-1>", lambda e: on_button_press(button_user))
    button_user.bind("<ButtonRelease-1>", lambda e: on_button_release(button_user))

    window.mainloop()

if __name__ == "__main__":
    main()