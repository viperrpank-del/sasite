import tkinter as tk
from tkinter import ttk, messagebox
import math
from database import VotingDatabase

class VotingEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Редактор Голосования - Админ панель с БД")
        self.root.geometry("700x550")
        
        # Инициализация базы данных
        self.db = VotingDatabase()
        self.candidates = []
        self.load_candidates()
        
        self.setup_ui()
    
    def load_candidates(self):
        """Загрузка кандидатов из БД"""
        self.candidates = self.db.get_all_candidates()
    
    def setup_ui(self):
        # Основные вкладки
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка управления кандидатами
        tab_candidates = ttk.Frame(notebook)
        notebook.add(tab_candidates, text='Управление кандидатами')
        
        # Вкладка голосования
        tab_voting = ttk.Frame(notebook)
        notebook.add(tab_voting, text='Голосование')
        
        # Вкладка анализа
        tab_analysis = ttk.Frame(notebook)
        notebook.add(tab_analysis, text='Анализ данных')
        
        self.setup_candidates_tab(tab_candidates)
        self.setup_voting_tab(tab_voting)
        self.setup_analysis_tab(tab_analysis)
    
    def setup_candidates_tab(self, parent):
        # Добавление кандидата
        frame_add = tk.Frame(parent)
        frame_add.pack(fill='x', padx=10, pady=10)
        
        tk.Label(frame_add, text="Добавить кандидата:", font=('Arial', 12, 'bold')).pack(anchor='w')
        
        frame_input = tk.Frame(frame_add)
        frame_input.pack(fill='x', pady=5)
        
        self.entry_candidate = tk.Entry(frame_input, width=30, font=('Arial', 10))
        self.entry_candidate.pack(side='left', padx=5)
        
        btn_add = tk.Button(frame_input, text="Добавить", command=self.add_candidate,
                          bg='#28a745', fg='white', font=('Arial', 10))
        btn_add.pack(side='left', padx=5)
        
        # Список кандидатов
        frame_list = tk.Frame(parent)
        frame_list.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(frame_list, text="Список кандидатов:", font=('Arial', 12, 'bold')).pack(anchor='w')
        
        # Treeview для отображения кандидатов
        columns = ('id', 'name', 'votes')
        self.tree_candidates = ttk.Treeview(frame_list, columns=columns, show='headings', height=8)
        
        self.tree_candidates.heading('id', text='ID')
        self.tree_candidates.heading('name', text='Имя кандидата')
        self.tree_candidates.heading('votes', text='Голоса')
        
        self.tree_candidates.column('id', width=50)
        self.tree_candidates.column('name', width=200)
        self.tree_candidates.column('votes', width=100)
        
        self.tree_candidates.pack(fill='both', expand=True, pady=5)
        
        frame_buttons = tk.Frame(frame_list)
        frame_buttons.pack(fill='x')
        
        btn_delete = tk.Button(frame_buttons, text="Удалить выбранного", 
                             command=self.delete_candidate, bg='#dc3545', fg='white')
        btn_delete.pack(side='left', padx=5)
        
        btn_refresh = tk.Button(frame_buttons, text="Обновить список", 
                              command=self.refresh_candidates, bg='#17a2b8', fg='white')
        btn_refresh.pack(side='left', padx=5)
        
        self.refresh_candidates()
    
    def setup_voting_tab(self, parent):
        # Голосование
        frame_vote = tk.Frame(parent)
        frame_vote.pack(fill='x', padx=10, pady=10)
        
        tk.Label(frame_vote, text="Имитация голосования:", font=('Arial', 12, 'bold')).pack(anchor='w')
        
        # Поле для имени голосующего
        frame_voter = tk.Frame(frame_vote)
        frame_voter.pack(fill='x', pady=5)
        
        tk.Label(frame_voter, text="Имя голосующего:").pack(side='left')
        self.entry_voter = tk.Entry(frame_voter, width=20)
        self.entry_voter.pack(side='left', padx=5)
        
        # Выбор кандидата
        frame_candidate = tk.Frame(frame_vote)
        frame_candidate.pack(fill='x', pady=5)
        
        tk.Label(frame_candidate, text="Кандидат:").pack(side='left')
        self.combo_candidate = ttk.Combobox(frame_candidate, width=20, state='readonly')
        self.combo_candidate.pack(side='left', padx=5)
        
        # Кнопка голосования
        btn_vote = tk.Button(frame_vote, text="Зарегистрировать голос", 
                           command=self.register_vote, bg='#007bff', fg='white')
        btn_vote.pack(pady=10)
        
        # Массовое голосование
        frame_mass = tk.Frame(parent)
        frame_mass.pack(fill='x', padx=10, pady=10)
        
        tk.Label(frame_mass, text="Массовое голосование (эксперимент):", 
                font=('Arial', 12, 'bold')).pack(anchor='w')
        
        frame_mass_input = tk.Frame(frame_mass)
        frame_mass_input.pack(fill='x', pady=5)
        
        tk.Label(frame_mass_input, text="Количество голосов:").pack(side='left')
        self.entry_mass_votes = tk.Entry(frame_mass_input, width=10)
        self.entry_mass_votes.pack(side='left', padx=5)
        self.entry_mass_votes.insert(0, "100")
        
        btn_mass_vote = tk.Button(frame_mass_input, text="Сгенерировать голоса",
                                command=self.generate_mass_votes)
        btn_mass_vote.pack(side='left', padx=10)
        
        self.update_candidates_combobox()
    
    def setup_analysis_tab(self, parent):
        # Вычислительный эксперимент: Статистический анализ
        frame_exp = tk.Frame(parent)
        frame_exp.pack(fill='x', padx=10, pady=10)
        
        tk.Label(frame_exp, text="Вычислительный эксперимент: Анализ распределения голосов", 
                font=('Arial', 12, 'bold')).pack(anchor='w')
        
        btn_analyze = tk.Button(frame_exp, text="Провести анализ", 
                              command=self.run_analysis,
                              bg='#17a2b8', fg='white', font=('Arial', 11))
        btn_analyze.pack(pady=10)
        
        # Результаты анализа
        self.text_analysis = tk.Text(parent, height=15, width=80, font=('Consolas', 9))
        self.text_analysis.pack(fill='both', expand=True, padx=10, pady=10)
    
    def refresh_candidates(self):
        """Обновление списка кандидатов"""
        for item in self.tree_candidates.get_children():
            self.tree_candidates.delete(item)
        
        results = self.db.get_voting_results()
        candidates = self.db.get_all_candidates()
        
        for candidate_id, name in candidates:
            votes = results.get(name, 0)
            self.tree_candidates.insert('', 'end', values=(candidate_id, name, votes))
    
    def update_candidates_combobox(self):
        """Обновление комбобокса с кандидатами"""
        candidates = self.db.get_all_candidates()
        candidate_names = [name for _, name in candidates]
        self.combo_candidate['values'] = candidate_names
        if candidate_names:
            self.combo_candidate.set(candidate_names[0])
    
    def add_candidate(self):
        name = self.entry_candidate.get().strip()
        if name:
            if self.db.add_candidate(name):
                messagebox.showinfo("Успех", f"Кандидат '{name}' добавлен!")
                self.entry_candidate.delete(0, tk.END)
                self.refresh_candidates()
                self.update_candidates_combobox()
            else:
                messagebox.showwarning("Ошибка", "Кандидат с таким именем уже существует!")
        else:
            messagebox.showwarning("Ошибка", "Введите имя кандидата!")
    
    def delete_candidate(self):
        selection = self.tree_candidates.selection()
        if selection:
            item = self.tree_candidates.item(selection[0])
            candidate_id = item['values'][0]
            candidate_name = item['values'][1]
            
            if messagebox.askyesno("Подтверждение", f"Удалить кандидата '{candidate_name}'?"):
                if self.db.delete_candidate(candidate_id):
                    messagebox.showinfo("Успех", "Кандидат удален!")
                    self.refresh_candidates()
                    self.update_candidates_combobox()
                else:
                    messagebox.showerror("Ошибка", "Не удалось удалить кандидата!")
    
    def register_vote(self):
        voter = self.entry_voter.get().strip()
        candidate_name = self.combo_candidate.get()
        
        if not voter:
            messagebox.showwarning("Ошибка", "Введите имя голосующего!")
            return
        
        if not candidate_name:
            messagebox.showwarning("Ошибка", "Выберите кандидата!")
            return
        
        # Находим ID кандидата
        candidates = self.db.get_all_candidates()
        candidate_id = None
        for cand_id, name in candidates:
            if name == candidate_name:
                candidate_id = cand_id
                break
        
        if candidate_id and self.db.register_vote(voter, candidate_id):
            messagebox.showinfo("Успех", f"Голос {voter} за {candidate_name} зарегистрирован!")
            self.entry_voter.delete(0, tk.END)
            self.refresh_candidates()
        else:
            messagebox.showwarning("Ошибка", "Не удалось зарегистрировать голос или человек уже голосовал!")
    
    def generate_mass_votes(self):
        try:
            num_votes = int(self.entry_mass_votes.get())
            if num_votes <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Ошибка", "Введите корректное число голосов!")
            return
        
        success_count = self.db.generate_mass_votes(num_votes)
        messagebox.showinfo("Успех", f"Сгенерировано {success_count} голосов!")
        self.refresh_candidates()
    
    def run_analysis(self):
        """Вычислительный эксперимент: Статистический анализ распределения голосов"""
        results = self.db.get_voting_results()
        total_votes = self.db.get_total_votes()
        
        if not results or total_votes == 0:
            self.text_analysis.delete(1.0, tk.END)
            self.text_analysis.insert(tk.END, "Нет данных для анализа!")
            return
        
        # Сбор данных для анализа
        candidates = list(results.keys())
        votes = list(results.values())
        
        analysis_text = "=== СТАТИСТИЧЕСКИЙ АНАЛИЗ РАСПРЕДЕЛЕНИЯ ГОЛОСОВ ===\n\n"
        
        # Основная статистика
        analysis_text += f"Общее количество голосов: {total_votes}\n"
        analysis_text += f"Количество кандидатов: {len(candidates)}\n\n"
        
        # Распределение голосов
        analysis_text += "РАСПРЕДЕЛЕНИЕ ГОЛОСОВ:\n"
        for candidate in candidates:
            vote_count = results[candidate]
            percentage = (vote_count / total_votes) * 100
            analysis_text += f"  {candidate}: {vote_count} голосов ({percentage:.2f}%)\n"
        
        # Вычислительный эксперимент: анализ равномерности распределения
        analysis_text += "\n=== ВЫЧИСЛИТЕЛЬНЫЙ ЭКСПЕРИМЕНТ ===\n"
        analysis_text += "Анализ равномерности распределения голосов:\n\n"
        
        # Среднее значение
        mean_votes = total_votes / len(candidates)
        analysis_text += f"Среднее количество голосов на кандидата: {mean_votes:.2f}\n"
        
        # Стандартное отклонение
        variance = sum((x - mean_votes) ** 2 for x in votes) / len(votes)
        std_dev = math.sqrt(variance)
        analysis_text += f"Стандартное отклонение: {std_dev:.2f}\n"
        
        # Коэффициент вариации
        coefficient_variation = (std_dev / mean_votes) * 100 if mean_votes > 0 else 0
        analysis_text += f"Коэффициент вариации: {coefficient_variation:.2f}%\n\n"
        
        # Анализ равномерности
        if coefficient_variation < 30:
            analysis_text += "ВЫВОД: Распределение голосов относительно РАВНОМЕРНОЕ\n"
        elif coefficient_variation < 60:
            analysis_text += "ВЫВОД: Распределение голосов УМЕРЕННОЕ\n"
        else:
            analysis_text += "ВЫВОД: Распределение голосов НЕРАВНОМЕРНОЕ\n"
        
        # Индекс концентрации (индекс Херфиндаля)
        herfindahl_index = sum((x / total_votes) ** 2 for x in votes) * 10000
        analysis_text += f"Индекс Херфиндаля (концентрации): {herfindahl_index:.2f}\n"
        
        if herfindahl_index < 1500:
            analysis_text += "Уровень концентрации: НИЗКИЙ (конкуренция высокая)\n"
        elif herfindahl_index < 2500:
            analysis_text += "Уровень концентрации: УМЕРЕННЫЙ\n"
        else:
            analysis_text += "Уровень концентрации: ВЫСОКИЙ (доминирование)\n"
        
        # Статистика из БД
        stats = self.db.get_voting_statistics()
        analysis_text += f"\n=== СТАТИСТИКА ИЗ БАЗЫ ДАННЫХ ===\n"
        analysis_text += f"Всего зарегистрированных голосующих: {stats['voter_count']}\n"
        analysis_text += f"Распределение голосов по часам: {stats['hourly_distribution']}\n"
        
        self.text_analysis.delete(1.0, tk.END)
        self.text_analysis.insert(tk.END, analysis_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = VotingEditor(root)
    root.mainloop()