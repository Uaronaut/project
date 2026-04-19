#!/usr/bin/env python3
import psycopg2
from tabulate import tabulate
from contextlib import contextmanager
import os
from datetime import datetime

# Конфигурация
DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'dbname': 'notes_db',
    'user': 'postgres',
    'password': 'postgres'
}

class NotesApp:
    def __init__(self):
        self.conn = None
        
    def connect(self):
        """Подключение к БД"""
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            self._init_db()
            print("База данных подключена")
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            exit(1)
    
    def _init_db(self):
        """Создание таблицы"""
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT,
                    category TEXT DEFAULT 'Общее',
                    created_at TIMESTAMP DEFAULT NOW(),
                    is_archived BOOLEAN DEFAULT FALSE
                )
            """)
            self.conn.commit()
    
    @contextmanager
    def cursor(self):
        """Курсор"""
        cur = self.conn.cursor()
        try:
            yield cur
            self.conn.commit()
        finally:
            cur.close()
    
    def menu(self):
        """Главное меню"""
        while True:
            print("\n" + "="*50)
            print(" МЕНЕДЖЕР ЗАМЕТОК")
            print("="*50)
            print("1. Создать заметку")
            print("2. Все заметки")
            print("3. Поиск")
            print("4. По категориям")
            print("5. Архив")
            print("6. Выход")
            
            choice = input("\nВыберите (1-6): ").strip()
            
            if choice == '1':
                self.create_note()
            elif choice == '2':
                self.list_notes()
            elif choice == '3':
                self.search_notes()
            elif choice == '4':
                self.by_category()
            elif choice == '5':
                self.show_archive()
            elif choice == '6':
                print("👋 До свидания!")
                break
    
    def create_note(self):
        """Создание заметки"""
        print("\n--- Новая заметка ---")
        title = input("Заголовок: ").strip()
        if not title:
            print("Заголовок обязателен")
            return
        
        print("Текст (пустая строка - конец):")
        lines = []
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        
        category = input("Категория (Enter - Общее): ").strip() or "Общее"
        
        with self.cursor() as cur:
            cur.execute(
                "INSERT INTO notes (title, content, category) VALUES (%s, %s, %s)",
                (title, '\n'.join(lines), category)
            )
        print("Заметка создана")
    
    def list_notes(self, where="WHERE NOT is_archived", title="АКТИВНЫЕ ЗАМЕТКИ"):
        """Список заметок"""
        with self.cursor() as cur:
            cur.execute(f"SELECT id, title, category, created_at, content FROM notes {where} ORDER BY created_at DESC")
            notes = cur.fetchall()
            
            if not notes:
                print("📭 Заметок нет")
                return
            
            print(f"\n--- {title} ---")
            data = [[n[0], n[1], n[2], n[3].strftime('%d.%m.%Y'), n[4][:30]+'...' if n[4] else ''] 
                   for n in notes]
            print(tabulate(data, headers=['ID', 'Заголовок', 'Категория', 'Дата', 'Содержание']))
            
            self.view_note()
    
    def view_note(self):
        """Просмотр заметки"""
        try:
            nid = input("\nID заметки для просмотра (Enter - назад): ").strip()
            if not nid:
                return
            
            with self.cursor() as cur:
                cur.execute("SELECT * FROM notes WHERE id = %s", (nid,))
                note = cur.fetchone()
                
                if not note:
                    print("Заметка не найдена")
                    return
                
                print("\n" + "="*50)
                print(f"ID: {note[0]}")
                print(f"Заголовок: {note[1]}")
                print(f"Категория: {note[3]}")
                print(f"Создано: {note[4]}")
                print(f"Статус: {'Заметка в архиве' if note[5] else 'Страница активна'}")
                print("-"*50)
                print(note[2] or "[без текста]")
                print("="*50)
                
                # Действия с заметкой
                print("\n1. Редактировать")
                print("2. Удалить")
                print("3. Архив/Разархивировать")
                print("4. Назад")
                
                act = input("Действие: ").strip()
                if act == '1':
                    self.edit_note(nid)
                elif act == '2':
                    if input("Удалить? (д/н): ").lower() == 'д':
                        with self.cursor() as cur:
                            cur.execute("DELETE FROM notes WHERE id = %s", (nid,))
                        print("Удалено")
                elif act == '3':
                    with self.cursor() as cur:
                        cur.execute("UPDATE notes SET is_archived = NOT is_archived WHERE id = %s", (nid,))
                    print("Статус изменен")
        except:
            pass
    
    def edit_note(self, nid):
        """Редактирование"""
        with self.cursor() as cur:
            cur.execute("SELECT title, content, category FROM notes WHERE id = %s", (nid,))
            note = cur.fetchone()
            
            print("\n--- Редактирование ---")
            new_title = input(f"Заголовок [{note[0]}]: ").strip() or note[0]
            new_category = input(f"Категория [{note[2]}]: ").strip() or note[2]
            print(f"Текст (Enter - оставить):")
            new_content = note[1]
            if input("Изменить текст? (д/н): ").lower() == 'д':
                print("Новый текст (пустая строка - конец):")
                lines = []
                while True:
                    line = input()
                    if not line:
                        break
                    lines.append(line)
                new_content = '\n'.join(lines) if lines else note[1]
            
            cur.execute(
                "UPDATE notes SET title=%s, content=%s, category=%s WHERE id=%s",
                (new_title, new_content, new_category, nid)
            )
            print("Обновлено")
    
    def search_notes(self):
        """Поиск"""
        term = input("Поиск: ").strip()
        if not term:
            return
        
        with self.cursor() as cur:
            cur.execute(
                "SELECT id, title, category FROM notes WHERE title ILIKE %s OR content ILIKE %s",
                (f'%{term}%', f'%{term}%')
            )
            results = cur.fetchall()
            
            if results:
                print(f"\nНайдено: {len(results)}")
                for r in results:
                    print(f"[{r[0]}] {r[1]} ({r[2]})")
                self.view_note()
            else:
                print("Ничего не найдено")
    
    def by_category(self):
        """По категориям"""
        with self.cursor() as cur:
            cur.execute("SELECT DISTINCT category FROM notes")
            cats = [c[0] for c in cur.fetchall()]
            
            if not cats:
                print("📭 Нет категорий")
                return
            
            print("\nКатегории:")
            for i, cat in enumerate(cats, 1):
                cur.execute("SELECT COUNT(*) FROM notes WHERE category = %s", (cat,))
                cnt = cur.fetchone()[0]
                print(f"{i}. {cat} ({cnt})")
            
            try:
                choice = int(input("Выберите: ")) - 1
                if 0 <= choice < len(cats):
                    self.list_notes(
                        f"WHERE category = '{cats[choice]}' AND NOT is_archived",
                        f"КАТЕГОРИЯ: {cats[choice]}"
                    )
            except:
                pass
    
    def show_archive(self):
        """Архив"""
        self.list_notes("WHERE is_archived", "АРХИВ")
    
    def run(self):
        """Запуск"""
        self.connect()
        try:
            self.menu()
        finally:
            if self.conn:
                self.conn.close()

if __name__ == "__main__":
    NotesApp().run()