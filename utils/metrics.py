"""
Модуль простых метрик для бота: считает уникальных пользователей и общее число обработанных кошельков
"""

# множество для отслеживания уникальных пользователей
seen_users: set[int] = set()
# общее число проверенных кошельков
total_wallets_checked: int = 0


def add_user(user_id: int) -> None:
    """
    Добавляет пользователя в набор уникальных, если ещё не был,
    и печатает текущее число уникальных пользователей.
    """
    global seen_users
    if user_id not in seen_users:
        seen_users.add(user_id)
        print(f"[Metrics] Unique users: {len(seen_users)}")


def add_wallets(count: int) -> None:
    """
    Увеличивает счётчик проверенных кошельков на count
    и печатает обновлённое общее число.
    """
    global total_wallets_checked
    total_wallets_checked += count
    print(f"[Metrics] Wallets checked total: {total_wallets_checked}")
