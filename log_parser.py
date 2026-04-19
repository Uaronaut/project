import time
import random
from datetime import datetime, timedelta
from collections import defaultdict

def generate_logs(n=1000):
    """Генерирует тестовые логи"""
    types, users, actions = ['INFO','WARNING','ERROR','DEBUG'], [f'user_{i}' for i in range(1,51)], ['login','logout','view','download']
    return [{
        'timestamp': (datetime.now() - timedelta(days=7) + timedelta(seconds=random.randint(0,604800))).isoformat(),
        'type': random.choice(types),
        'user': random.choice(users),
        'action': random.choice(actions),
        'status': random.choice([200,400,404,500]),
        'response_time': round(random.uniform(0.1,5.0), 2)
    } for _ in range(n)]

def slow_processor(logs):
    """Медленная версия с вложенными циклами"""
    start = time.time()
    stats, errors, slow, corr = {'by_type':{}}, defaultdict(list), [], []
    
    # Три отдельных цикла
    for log in logs:
        t = log['type']
        stats['by_type'][t] = stats['by_type'].get(t, {'count':0, 'sum':0})
        stats['by_type'][t]['count'] += 1
        stats['by_type'][t]['sum'] += log['response_time']
    
    for t in stats['by_type']:
        stats['by_type'][t]['avg'] = stats['by_type'][t]['sum'] / stats['by_type'][t]['count']
    
    for log in logs:
        if log['status'] >= 400:
            errors[f"{log['status']}_{log['action']}"].append(log['user'])
        if log['response_time'] > 2:
            slow.append(log)
    
    # Квадратичный поиск корреляций O(n²)
    for i, l1 in enumerate(logs):
        for l2 in logs[i+1:]:
            if l1['user'] == l2['user']:
                t1, t2 = datetime.fromisoformat(l1['timestamp']), datetime.fromisoformat(l2['timestamp'])
                if abs((t1 - t2).total_seconds()) < 60:
                    corr.append((l1['user'], l1['action'], l2['action']))
    
    return time.time() - start, len(corr)

def fast_processor(logs):
    """Быстрая версия с оптимизациями"""
    start = time.time()
    by_type, errors, users, slow, corr = {}, defaultdict(set), defaultdict(list), [], []
    user_logs = defaultdict(list)
    
    # Один проход для всей статистики
    for log in logs:
        t, u, s = log['type'], log['user'], log['status']
        
        by_type[t] = by_type.get(t, {'count':0, 'sum':0})
        by_type[t]['count'] += 1
        by_type[t]['sum'] += log['response_time']
        
        if s >= 400:
            errors[f"{s}_{log['action']}"].add(u)
        if log['response_time'] > 2:
            slow.append(log)
        
        user_logs[u].append(log)  # Для корреляций
    
    # Средние значения
    for t in by_type:
        by_type[t]['avg'] = by_type[t]['sum'] / by_type[t]['count']
    
    # Оптимизированный поиск корреляций O(n log n)
    for u, logs_list in user_logs.items():
        logs_list.sort(key=lambda x: x['timestamp'])
        for i in range(len(logs_list)-1):
            curr, j = logs_list[i], i+1
            while j < len(logs_list):
                diff = (datetime.fromisoformat(logs_list[j]['timestamp']) - 
                       datetime.fromisoformat(curr['timestamp'])).total_seconds()
                if diff <= 60:
                    corr.append((u, curr['action'], logs_list[j]['action']))
                    j += 1
                else:
                    break
    
    return time.time() - start, len(corr)

# Сравнение производительности
print("Генерация логов...")
logs = generate_logs(5000)

print("\nМедленная версия:")
slow_time, slow_corr = slow_processor(logs)
print(f"Время: {slow_time:.8f}с, Корреляций: {slow_corr}")

print("\nБыстрая версия:")
fast_time, fast_corr = fast_processor(logs)
print(f"Время: {fast_time:.8f}с, Корреляций: {fast_corr}")

print(f"\nУскорение: {slow_time/fast_time:.1f}x")