import sqlite3
import json
from datetime import datetime

class VotingDatabase:
    def __init__(self, db_name='voting_system.db'):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных и создание таблиц"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Таблица кандидатов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица голосующих
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                voted BOOLEAN DEFAULT FALSE,
                vote_date TIMESTAMP
            )
        ''')
        
        # Таблица голосов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                voter_id INTEGER,
                candidate_id INTEGER,
                vote_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (voter_id) REFERENCES voters (id),
                FOREIGN KEY (candidate_id) REFERENCES candidates (id)
            )
        ''')
        
        # Таблица результатов (для быстрого доступа)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS results (
                candidate_id INTEGER PRIMARY KEY,
                vote_count INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (candidate_id) REFERENCES candidates (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Добавляем тестовые данные, если таблицы пустые
        self.add_sample_data()
    
    def add_sample_data(self):
        """Добавление тестовых данных"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Проверяем, есть ли уже кандидаты
        cursor.execute("SELECT COUNT(*) FROM candidates")
        if cursor.fetchone()[0] == 0:
            # Добавляем стандартных кандидатов
            sample_candidates = ['Кандидат А', 'Кандидат Б', 'Кандидат В', 'Кандидат Г']
            for candidate in sample_candidates:
                try:
                    cursor.execute("INSERT INTO candidates (name) VALUES (?)", (candidate,))
                except sqlite3.IntegrityError:
                    pass  # Уже существует
        
        conn.commit()
        conn.close()
    
    def get_all_candidates(self):
        """Получить всех кандидатов"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM candidates ORDER BY name")
        candidates = cursor.fetchall()
        conn.close()
        return candidates
    
    def add_candidate(self, name):
        """Добавить нового кандидата"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO candidates (name) VALUES (?)", (name,))
            candidate_id = cursor.lastrowid
            # Добавляем запись в результаты
            cursor.execute("INSERT INTO results (candidate_id, vote_count) VALUES (?, ?)", 
                         (candidate_id, 0))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False
    
    def delete_candidate(self, candidate_id):
        """Удалить кандидата"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            # Удаляем связанные голоса
            cursor.execute("DELETE FROM votes WHERE candidate_id = ?", (candidate_id,))
            # Удаляем из результатов
            cursor.execute("DELETE FROM results WHERE candidate_id = ?", (candidate_id,))
            # Удаляем кандидата
            cursor.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))
            conn.commit()
            conn.close()
            return True
        except:
            conn.close()
            return False
    
    def register_vote(self, voter_name, candidate_id):
        """Зарегистрировать голос"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            # Проверяем, голосовал ли уже этот человек
            cursor.execute("SELECT id, voted FROM voters WHERE name = ?", (voter_name,))
            voter_data = cursor.fetchone()
            
            if voter_data and voter_data[1]:  # Уже голосовал
                conn.close()
                return False
            
            if not voter_data:
                # Создаем нового голосующего
                cursor.execute("INSERT INTO voters (name, voted) VALUES (?, ?)", 
                             (voter_name, True))
                voter_id = cursor.lastrowid
            else:
                # Обновляем существующего
                voter_id = voter_data[0]
                cursor.execute("UPDATE voters SET voted = ?, vote_date = CURRENT_TIMESTAMP WHERE id = ?", 
                             (True, voter_id))
            
            # Регистрируем голос
            cursor.execute("INSERT INTO votes (voter_id, candidate_id) VALUES (?, ?)", 
                         (voter_id, candidate_id))
            
            # Обновляем счетчик результатов
            cursor.execute('''
                INSERT OR REPLACE INTO results (candidate_id, vote_count, last_updated)
                VALUES (?, COALESCE((SELECT vote_count FROM results WHERE candidate_id = ?), 0) + 1, CURRENT_TIMESTAMP)
            ''', (candidate_id, candidate_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            conn.close()
            print(f"Error registering vote: {e}")
            return False
    
    def get_voting_results(self):
        """Получить результаты голосования"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.name, COALESCE(r.vote_count, 0) as votes
            FROM candidates c
            LEFT JOIN results r ON c.id = r.candidate_id
            ORDER BY votes DESC
        ''')
        
        results = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        return results
    
    def get_total_votes(self):
        """Получить общее количество голосов"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(vote_count) FROM results")
        total = cursor.fetchone()[0] or 0
        conn.close()
        return total
    
    def get_voting_statistics(self):
        """Получить статистику для вычислительного эксперимента"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Основная статистика
        cursor.execute("SELECT COUNT(*) FROM candidates")
        candidate_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM voters WHERE voted = 1")
        voter_count = cursor.fetchone()[0]
        
        # Распределение голосов по часам (для эксперимента с динамикой)
        cursor.execute('''
            SELECT strftime('%H', vote_timestamp) as hour, COUNT(*) as vote_count
            FROM votes 
            GROUP BY hour
            ORDER BY hour
        ''')
        hourly_distribution = cursor.fetchall()
        
        conn.close()
        
        return {
            'candidate_count': candidate_count,
            'voter_count': voter_count,
            'hourly_distribution': dict(hourly_distribution)
        }
    
    def generate_mass_votes(self, num_votes):
        """Генерация массовых голосов (для эксперимента)"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Получаем список кандидатов
        cursor.execute("SELECT id FROM candidates")
        candidate_ids = [row[0] for row in cursor.fetchall()]
        
        if not candidate_ids:
            conn.close()
            return False
        
        import random
        from datetime import datetime, timedelta
        
        success_count = 0
        for i in range(num_votes):
            voter_name = f"AutoVoter_{i+1}_{random.randint(1000,9999)}"
            candidate_id = random.choice(candidate_ids)
            
            try:
                # Случайное время в течение последних 24 часов
                random_time = datetime.now() - timedelta(hours=random.randint(0, 23), 
                                                       minutes=random.randint(0, 59))
                
                cursor.execute("INSERT INTO voters (name, voted) VALUES (?, ?)", 
                             (voter_name, True))
                voter_id = cursor.lastrowid
                
                cursor.execute("INSERT INTO votes (voter_id, candidate_id, vote_timestamp) VALUES (?, ?, ?)", 
                             (voter_id, candidate_id, random_time))
                
                cursor.execute('''
                    INSERT OR REPLACE INTO results (candidate_id, vote_count, last_updated)
                    VALUES (?, COALESCE((SELECT vote_count FROM results WHERE candidate_id = ?), 0) + 1, CURRENT_TIMESTAMP)
                ''', (candidate_id, candidate_id))
                
                success_count += 1
                
            except sqlite3.IntegrityError:
                continue  # Пропускаем дубликаты
        
        conn.commit()
        conn.close()
        return success_count

# Создание БД при импорте
if __name__ == "__main__":
    db = VotingDatabase()
    print("База данных голосования инициализирована успешно!")
    print("Таблицы созданы, добавлены тестовые данные.")