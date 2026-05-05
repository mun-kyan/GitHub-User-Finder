import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("800x600")

        # Загрузка избранных пользователей
        self.favorites = self.load_favorites()

        self.setup_ui()

    def setup_ui(self):
        # Поле поиска
        ttk.Label(self.root, text="Имя пользователя GitHub:").pack(pady=5)
        self.search_entry = ttk.Entry(self.root, width=50)
        self.search_entry.pack(pady=5)

        # Кнопка поиска
        self.search_btn = ttk.Button(self.root, text="Найти пользователя", command=self.search_user)
        self.search_btn.pack(pady=5)

        # Результаты поиска
        ttk.Label(self.root, text="Результаты поиска:").pack(pady=10)
        columns = ("Логин", "Имя", "Местоположение", "Публичные репозитории")
        self.results_tree = ttk.Treeview(self.root, columns=columns, show="headings", height=10)

        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=150)

        self.results_tree.pack(pady=10, padx=20, fill="both", expand=True)

        # Привязка двойного клика для добавления в избранное
        self.results_tree.bind("<Double-1>", self.add_to_favorites)

        # Список избранных пользователей
        ttk.Label(self.root, text="Избранные пользователи:").pack(pady=10)
        self.favorites_listbox = tk.Listbox(self.root, height=8, width=70)
        self.favorites_listbox.pack(pady=10, padx=20, fill="both", expand=True)

        # Кнопка удаления из избранного
        self.remove_btn = ttk.Button(self.root, text="Удалить из избранного", command=self.remove_from_favorites)
        self.remove_btn.pack(pady=5)

        # Заполнение списка избранных
        self.refresh_favorites_list()
    def search_user(self):
        username = self.search_entry.get().strip()

        # Валидация ввода
        if not username:
            messagebox.showerror("Ошибка", "Поле поиска не должно быть пустым")
            return

        try:
            # Запрос к GitHub API
            url = f"https://api.github.com/users/{username}"
            response = requests.get(url)

            if response.status_code == 200:
                user_data = response.json()
                self.display_search_results([user_data])
            elif response.status_code == 404:
                messagebox.showwarning("Предупреждение", "Пользователь не найден")
            else:
                messagebox.showerror("Ошибка", f"Ошибка API: {response.status_code}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка подключения: {e}")

    def display_search_results(self, users):
        # Очистка таблицы результатов
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        # Заполнение таблицы результатами
        for user in users:
            login = user.get("login", "N/A")
            name = user.get("name", "N/A")
            location = user.get("location", "N/A")
            repos = user.get("public_repos", 0)

            self.results_tree.insert("", "end", values=(login, name, location, repos))
    def load_favorites(self):
        if os.path.exists("favorites.json"):
            with open("favorites.json", "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_favorites(self):
        with open("favorites.json", "w", encoding="utf-8") as f:
            json.dump(self.favorites, f, ensure_ascii=False, indent=2)

    def add_to_favorites(self, event=None):
        selection = self.results_tree.selection()
        if selection:
            item = selection[0]
            values = self.results_tree.item(item, "values")
            username = values[0]  # Логин — первый столбец

            # Проверка, не добавлен ли уже пользователь
            if any(fav["login"] == username for fav in self.favorites):
                messagebox.showinfo("Информация", "Пользователь уже в избранном")
                return

            # Получаем полные данные пользователя
            url = f"https://api.github.com/users/{username}"
            response = requests.get(url)
            if response.status_code == 200:
                user_data = response.json()
                self.favorites.append({
                    "login": username,
                    "name": user_data.get("name", "N/A"),
                    "avatar_url": user_data.get("avatar_url", ""),
                    "html_url": user_data.get("html_url", "")
                })
                self.save_favorites()
                self.refresh_favorites_list()
                messagebox.showinfo("Успех", f"Пользователь {username} добавлен в избранное")
            else:
                messagebox.showerror("Ошибка", "Не удалось получить данные пользователя")

    def refresh_favorites_list(self):
        self.favorites_listbox.delete(0, tk.END)
        for fav in self.favorites:
            display_text = f"{fav['login']} ({fav['name']})"
            self.favorites_listbox.insert(tk.END, display_text)

    def remove_from_favorites(self):
        selection = self.favorites_listbox.curselection()
        if selection:
            index = selection[0]
            removed_user = self.favorites.pop(index)
            self.save_favorites()
            self.refresh_favorites_list()
            messagebox.showinfo("Успех", f"Пользователь {removed_user['login']} удалён из избранного")
if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()
