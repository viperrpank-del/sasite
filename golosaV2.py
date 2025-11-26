import tkinter as tk
from tkinter import ttk
import math
from database import VotingDatabase

class VotingViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Просмотрщик Голосования - Только чтение с БД")
        self.root.geometry("600x500")
        
        # Инициализация базы данных
        self.db = VotingDatabase()
        
        self.setup_ui()
    
    def setup_ui(self):
        # Основные вкладки
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка результатов
        tab_results = ttk.Frame(notebook)
        notebook.add(tab_results, text='Результаты')
        
        # Вкладка визуализации
        tab_visualization = ttk.Frame(notebook)
        notebook.add(tab_visualization, text='Визуализация')
        
        # Вкладка эксперимента
        tab_experiment = ttk.Frame(notebook)
        notebook.add(tab_experiment, text='Вычислительный эксперимент')
        
        self.setup_results_tab(tab_results)
        self.setup_visualization_tab(tab_visualization)
        self.setup_experiment_tab(tab_experiment)
    
    def setup_results_tab(self, parent):
        # Заголовок
        lbl_title = tk.Label(parent, text="ОФИЦИАЛЬНЫЕ РЕЗУЛЬТАТЫ ГОЛОСОВАНИЯ", 
                           font=('Arial', 14, 'bold'), fg='#2c3e50')
        lbl_title.pack(pady=10)
        
        # Информация о голосовании
        frame_info = tk.Frame(parent)
        frame_info.pack(fill='x', padx=20, pady=5)
        
        total_votes = self.db.get_total_votes()
        stats = self.db.get_voting_statistics()
        
        info_text = f"Всего проголосовало: {total_votes} человек\n"
        info_text += f"Количество кандидатов: {stats['candidate_count']}\n"
        info_text += "Данные загружены из базы данных SQLite"
        
        lbl_info = tk.Label(frame_info, text=info_text, font=('Arial', 10), 
                          justify='left', bg='#f8f9fa', relief='solid', padx=10, pady=5)
        lbl_info.pack(fill='x')
        
        # Таблица результатов
        frame_table = tk.Frame(parent)
        frame_table.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Создание Treeview
        columns = ('candidate', 'votes', 'percentage')
        self.tree = ttk.Treeview(frame_table, columns=columns, show='headings', height=8)
        
        # Заголовки
        self.tree.heading('candidate', text='Кандидат')
        self.tree.heading('votes', text='Голоса')
        self.tree.heading('percentage', text='Процент')
        
        # Колонки
        self.tree.column('candidate', width=200)
        self.tree.column('votes', width=100)
        self.tree.column('percentage', width=100)
        
        # Добавление данных из БД
        results = self.db.get_voting_results()
        total_votes = sum(results.values())
        
        for candidate, votes in sorted(results.items(), key=lambda x: x[1], reverse=True):
            percentage = (votes / total_votes) * 100 if total_votes > 0 else 0
            self.tree.insert('', 'end', values=(
                candidate, 
                votes, 
                f"{percentage:.1f}%"
            ))
        
        self.tree.pack(fill='both', expand=True)
        
        # Победитель
        if results:
            winner = max(results.items(), key=lambda x: x[1])
            winner_percentage = (winner[1] / total_votes) * 100
            
            frame_winner = tk.Frame(parent)
            frame_winner.pack(fill='x', padx=20, pady=10)
            
            winner_text = f"🏆 ПОБЕДИТЕЛЬ: {winner[0]} - {winner[1]} голосов ({winner_percentage:.1f}%)"
            lbl_winner = tk.Label(frame_winner, text=winner_text, 
                                font=('Arial', 12, 'bold'), fg='#e74c3c')
            lbl_winner.pack()
    
    def setup_visualization_tab(self, parent):
        # Простая текстовая визуализация результатов
        lbl_title = tk.Label(parent, text="ВИЗУАЛИЗАЦИЯ РЕЗУЛЬТАТОВ", 
                           font=('Arial', 14, 'bold'), fg='#2c3e50')
        lbl_title.pack(pady=10)
        
        # Область для визуализации
        self.viz_frame = tk.Frame(parent, bg='white')
        self.viz_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.draw_simple_bar_chart()
    
    def draw_simple_bar_chart(self):
        """Простая текстовая визуализация в виде столбчатой диаграммы"""
        results = self.db.get_voting_results()
        total_votes = sum(results.values())
        max_votes = max(results.values()) if results else 1
        
        for widget in self.viz_frame.winfo_children():
            widget.destroy()
        
        for candidate, votes in sorted(results.items(), key=lambda x: x[1], reverse=True):
            frame_candidate = tk.Frame(self.viz_frame)
            frame_candidate.pack(fill='x', padx=10, pady=2)
            
            # Имя кандидата
            lbl_name = tk.Label(frame_candidate, text=candidate, width=15, anchor='w')
            lbl_name.pack(side='left')
            
            # Полоса голосов
            percentage = (votes / max_votes) * 80  # Масштабирование для отображения
            bar_color = '#3498db' if votes != max_votes else '#e74c3c'
            
            frame_bar = tk.Frame(frame_candidate, height=20, bg='#ecf0f1')
            frame_bar.pack(side='left', fill='x', expand=True, padx=5)
            frame_bar.pack_propagate(False)
            
            inner_bar = tk.Frame(frame_bar, height=20, width=percentage, bg=bar_color)
            inner_bar.pack(side='left')
            
            # Количество голосов и процент
            vote_percentage = (votes / total_votes) * 100 if total_votes > 0 else 0
            lbl_stats = tk.Label(frame_candidate, text=f"{votes} ({vote_percentage:.1f}%)", 
                               width=15, anchor='e')
            lbl_stats.pack(side='right')
    
    def setup_experiment_tab(self, parent):
        """Вычислительный эксперимент: Анализ динамики голосования"""
        lbl_title = tk.Label(parent, text="ЭКСПЕРИМЕНТ: МОДЕЛИРОВАНИЕ ДИНАМИКИ ГОЛОСОВАНИЯ", 
                           font=('Arial', 12, 'bold'), fg='#2c3e50')
        lbl_title.pack(pady=10)
        
        # Описание эксперимента
        description = """Эксперимент анализирует распределение голосов по времени
на основе реальных данных из базы данных."""
        
        lbl_desc = tk.Label(parent, text=description, font=('Arial', 10), 
                          justify='center', wraplength=500)
        lbl_desc.pack(pady=5)
        
        # Кнопка запуска эксперимента
        btn_run = tk.Button(parent, text="Запустить анализ динамики", 
                          command=self.run_dynamics_experiment,
                          bg='#9b59b6', fg='white', font=('Arial', 11))
        btn_run.pack(pady=10)
        
        # Область вывода результатов
        self.experiment_text = tk.Text(parent, height=15, width=70, font=('Consolas', 9))
        self.experiment_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(self.experiment_text)
        scrollbar.pack(side='right', fill='y')
        self.experiment_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.experiment_text.yview)
    
    def run_dynamics_experiment(self):
        """Вычислительный эксперимент: Анализ динамики голосования на основе реальных данных"""
        # Очистка предыдущих результатов
        self.experiment_text.delete(1.0, tk.END)
        
        experiment_text = "=== АНАЛИЗ ДИНАМИКИ ГОЛОСОВАНИЯ ИЗ БАЗЫ ДАННЫХ ===\n\n"
        
        # Получаем статистику из БД
        stats = self.db.get_voting_statistics()
        results = self.db.get_voting_results()
        
        if not results:
            experiment_text += "Нет данных для анализа!"
            self.experiment_text.insert(tk.END, experiment_text)
            return
        
        experiment_text += f"Общее количество голосов: {sum(results.values())}\n"
        experiment_text += f"Количество кандидатов: {len(results)}\n\n"
        
        # Анализ распределения по часам
        hourly_data = stats['hourly_distribution']
        if hourly_data:
            experiment_text += "РАСПРЕДЕЛЕНИЕ ГОЛОСОВ ПО ВРЕМЕНИ:\n"
            experiment_text += "Время | Количество голосов | Процент\n"
            experiment_text += "-" * 50 + "\n"
            
            total_hourly_votes = sum(hourly_data.values())
            for hour in sorted(hourly_data.keys()):
                votes = hourly_data[hour]
                percentage = (votes / total_hourly_votes) * 100 if total_hourly_votes > 0 else 0
                experiment_text += f"  {hour}:00 | {votes:4} голосов | {percentage:5.1f}%\n"
            
            # Анализ активности
            experiment_text += "\nАНАЛИЗ АКТИВНОСТИ:\n"
            max_hour = max(hourly_data.items(), key=lambda x: x[1]) if hourly_data else None
            min_hour = min(hourly_data.items(), key=lambda x: x[1]) if hourly_data else None
            
            if max_hour and min_hour:
                experiment_text += f"Пик активности: {max_hour[0]}:00 - {max_hour[1]} голосов\n"
                experiment_text += f"Минимум активности: {min_hour[0]}:00 - {min_hour[1]} голосов\n"
                
                # Коэффициент неравномерности
                activity_ratio = max_hour[1] / min_hour[1] if min_hour[1] > 0 else 0
                experiment_text += f"Коэффициент неравномерности: {activity_ratio:.2f}\n"
        
        else:
            experiment_text += "Нет данных о распределении по времени.\n"
            experiment_text += "Для получения данных используйте массовое голосование в редакторе.\n"
        
        # Вычислительный эксперимент: прогнозирование
        experiment_text += "\n=== ВЫЧИСЛИТЕЛЬНЫЙ ЭКСПЕРИМЕНТ ===\n"
        experiment_text += "Прогнозирование итогов на основе текущих данных:\n\n"
        
        total_votes = sum(results.values())
        if total_votes > 0:
            # Прогноз на основе текущего распределения
            forecast_votes = total_votes * 1.5  # Предполагаем рост на 50%
            
            experiment_text += f"Текущее количество голосов: {total_votes}\n"
            experiment_text += f"Прогнозируемое итоговое количество: {forecast_votes:.0f}\n\n"
            
            experiment_text += "Прогнозируемые результаты:\n"
            for candidate, votes in sorted(results.items(), key=lambda x: x[1], reverse=True):
                current_percentage = (votes / total_votes) * 100
                forecast_votes_candidate = votes * 1.5
                forecast_percentage = (forecast_votes_candidate / forecast_votes) * 100
                
                experiment_text += f"  {candidate}: {forecast_votes_candidate:.0f} голосов ({forecast_percentage:.1f}%)\n"
            
            # Анализ стабильности
            experiment_text += "\nАНАЛИЗ СТАБИЛЬНОСТИ РЕЗУЛЬТАТОВ:\n"
            percentages = [(votes / total_votes) * 100 for votes in results.values()]
            std_dev_percentage = math.sqrt(sum((p - 100/len(percentages)) ** 2 for p in percentages) / len(percentages))
            
            experiment_text += f"Стандартное отклонение процентов: {std_dev_percentage:.2f}%\n"
            if std_dev_percentage < 15:
                experiment_text += "Стабильность: ВЫСОКАЯ (результаты предсказуемы)\n"
            elif std_dev_percentage < 30:
                experiment_text += "Стабильность: СРЕДНЯЯ\n"
            else:
                experiment_text += "Стабильность: НИЗКАЯ (возможны изменения)\n"
        
        self.experiment_text.insert(tk.END, experiment_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = VotingViewer(root)
    root.mainloop()