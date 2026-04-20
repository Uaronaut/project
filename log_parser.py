import re
from collections import Counter
from datetime import datetime
import os

class LogProcessor:
    def __init__(self, filename):
        self.filename = filename
        self.errors = []
        self.requests = []
        
    def parse_log(self):
        """Парсинг лога с оптимизацией через single-pass чтение"""
        with open(self.filename, 'r', encoding='utf-8') as file:
            for line in file:
                # Оптимизация: одно прохождение вместо множества
                if 'ERROR' in line:
                    self._parse_error(line)
                elif re.search(r'GET|POST|PUT|DELETE', line):
                    self._parse_request(line)
                    
    def _parse_error(self, line):
        """Извлечение ошибок"""
        timestamp = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', line)
        error_msg = line.split('ERROR')[1].strip()
        self.errors.append({
            'time': timestamp.group() if timestamp else None,
            'message': error_msg
        })
    
    def _parse_request(self, line):
        """Извлечение HTTP запросов"""
        methods = ['GET', 'POST', 'PUT', 'DELETE']
        for method in methods:
            if method in line:
                self.requests.append(method)
                break
    
    def get_stats(self):
        """Агрегация статистики"""
        return {
            'total_errors': len(self.errors),
            'top_errors': Counter([e['message'] for e in self.errors]).most_common(5),
            'request_methods': dict(Counter(self.requests))
        }

# Пример использования с оптимизацией через контекстный менеджер
if __name__ == '__main__':
    # Генерация тестового лога
    with open('sample.log', 'w') as f:
        for i in range(1000):
            f.write(f"2024-01-01 10:{i//60:02d}:{i%60:02d} INFO Request processed\n")
            if i % 10 == 0:
                f.write(f"2024-01-01 10:{i//60:02d}:{i%60:02d} ERROR Database connection timeout\n")
            if i % 5 == 0:
                f.write(f"2024-01-01 10:{i//60:02d}:{i%60:02d} GET /api/users\n")
    
    # Обработка
    processor = LogProcessor('sample.log')
    processor.parse_log()
    print(processor.get_stats())