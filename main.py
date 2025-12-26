import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import threading

class BackupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Утилита резервного копирования")
        self.root.geometry("600x400")
        self.root.resizable(False, False)

        # Переменные
        self.source_path = tk.StringVar()

        # Заголовок
        title_label = tk.Label(root, text="Утилита резервного копирования", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=20)

        # Выбор папки
        frame_source = tk.Frame(root)
        frame_source.pack(pady=10, fill=tk.X, padx=50)

        tk.Label(frame_source, text="Исходная папка:", font=("Arial", 12)).pack(anchor=tk.W)
        tk.Entry(frame_source, textvariable=self.source_path, width=50, state="readonly").pack(pady=5)
        tk.Button(frame_source, text="Выбрать папку", command=self.choose_folder).pack(pady=5)

        # Кнопка запуска
        self.backup_button = tk.Button(root, text="Начать резервное копирование", 
                                       font=("Arial", 12), bg="#4CAF50", fg="white",
                                       command=self.start_backup_thread)
        self.backup_button.pack(pady=30)

        # Прогресс-бар
        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="indeterminate")
        self.progress.pack(pady=10)

        # Статус
        self.status_label = tk.Label(root, text="Готов к работе", fg="blue", font=("Arial", 10))
        self.status_label.pack(pady=10)

    def choose_folder(self):
        folder = filedialog.askdirectory(title="Выберите папку для резервного копирования")
        if folder:
            self.source_path.set(folder)

    def create_backup_folder(self):
        date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_name = f"Backup_{date_str}"
        backup_path = os.path.join(os.path.dirname(self.source_path.get()), backup_name)
        os.makedirs(backup_path, exist_ok=True)
        return backup_path

    def perform_backup(self):
        source = self.source_path.get()
        if not source or not os.path.exists(source):
            messagebox.showerror("Ошибка", "Пожалуйста, выберите существующую папку!")
            return False

        try:
            backup_path = self.create_backup_folder()
            start_time = datetime.now()

            # Копирование с сохранением структуры
            shutil.copytree(source, backup_path, dirs_exist_ok=True)

            end_time = datetime.now()
            duration = end_time - start_time

            # Запись в лог
            log_entry = f"""
=== Резервное копирование ===
Время начала: {start_time.strftime("%Y-%m-%d %H:%M:%S")}
Время окончания: {end_time.strftime("%Y-%m-%d %H:%M:%S")}
Продолжительность: {duration}
Исходная папка: {source}
Папка бэкапа: {backup_path}
Статус: Успешно
{'-'*50}
"""
            with open("backup_log.txt", "a", encoding="utf-8") as log_file:
                log_file.write(log_entry)

            messagebox.showinfo("Успех", f"Резервная копия создана!\nПапка: {backup_path}")
            return True

        except Exception as e:
            error_msg = f"Ошибка при копировании: {str(e)}"
            with open("backup_log.txt", "a", encoding="utf-8") as log_file:
                log_file.write(f"{datetime.now()} | ОШИБКА: {error_msg}\n")
            messagebox.showerror("Ошибка", error_msg)
            return False

    def start_backup_thread(self):
        if not self.source_path.get():
            messagebox.showwarning("Предупреждение", "Сначала выберите папку!")
            return

        # Запуск в отдельном потоке, чтобы интерфейс не зависал
        self.backup_button.config(state="disabled")
        self.progress.start()
        self.status_label.config(text="Выполняется копирование...", fg="orange")

        def backup_task():
            success = self.perform_backup()
            self.root.after(0, self.finish_backup, success)

        threading.Thread(target=backup_task, daemon=True).start()

    def finish_backup(self, success):
        self.progress.stop()
        self.backup_button.config(state="normal")
        if success:
            self.status_label.config(text="Резервное копирование завершено успешно!", fg="green")
        else:
            self.status_label.config(text="Ошибка при выполнении", fg="red")


if __name__ == "__main__":
    root = tk.Tk()
    app = BackupApp(root)
    root.mainloop()