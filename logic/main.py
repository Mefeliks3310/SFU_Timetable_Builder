import tkinter as tk
from ui.admin_ui import AdminUI
from ui.user_ui import UserUI
def main():
    root = tk.Tk()
    root.title("SFU Timetable Builder")
    root.geometry("600x400")

    tk.Button(root,text="Режим администратора", command=lambda: AdminUI(root),font=("Arial",12)).pack(pady=10)
    tk.Button(root, text="Режим пользователя", command=lambda: UserUI(root), font=("Arial",12)).pack(pady=10)

    root.mainloop()

if __name__  == "__main__":
    main()