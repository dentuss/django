import json

# =============================================================================
# КОНСПЕКТ: Ещё один вариант пагинации — с полными ссылками (HATEOAS-like).
#
# HATEOAS (Hypermedia as the Engine of Application State) — один из уровней
# зрелости REST: вместе с данными сервер возвращает готовые URL-и для
# следующих действий. В этом файле реализация близка к этому принципу:
# вместе с данными отдаются ссылки self/first/last/next/prev — клиенту не
# нужно самому собирать URL.
#
# BaseController здесь — отдельный "мини-базовый" класс для контроллеров,
# которые умеют отдавать JSON и страничные ответы с ссылками.
# =============================================================================
class BaseController:
    """Базовий клас для всіх контролерів з підтримкою REST-відповідей"""
    def __init__(self, handler):
        self.handler = handler

    def send_json(self, data, status=200):
        # Общая процедура отправки JSON-ответа. Экономит 4 строки повторяющегося
        # кода в каждом наследнике.
        self.handler.send_response(status)
        self.handler.send_header("Content-type", "application/json")
        self.handler.end_headers()
        self.handler.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    # -------------------------------------------------------------------------
    # ДЗ: Формування метаданих
    # Задание (расширение): метаданные RestPagination с признаком
    # наличия/отсутствия ссылок на предыдущую и следующую страницы.
    #
    # Что сделано: метод response_with_pagination() формирует полноценный
    # REST-ответ со словарём "links", где:
    #   * self  — ссылка на текущую страницу
    #   * first — ссылка на первую страницу
    #   * last  — ссылка на последнюю страницу
    #   * next  — ссылка на следующую страницу ИЛИ None, если её нет
    #   * prev  — ссылка на предыдущую страницу ИЛИ None, если её нет
    # Т.е. присутствие или отсутствие next/prev в виде настоящих URL-ов —
    # это и есть информативная метаданность из ДЗ.
    # -------------------------------------------------------------------------
    def response_with_pagination(self, data_list, total_items):
        # handler.page и handler.per_page готовит hw-3.py/starter.py после
        # разбора query-параметров ?page=...&per_page=...
        page = self.handler.page
        per_page = self.handler.per_page

        # Вычисляем общее число страниц. Формула (x + y - 1) // y — это
        # "ceiling division" без импорта math: округление вверх.
        total_pages = (total_items + per_page - 1) // per_page if total_items > 0 else 1

        # Формируем базовый путь ресурса вида /users или /users/auth,
        # чтобы в ссылках сохранять исходный URI.
        path = f"/{self.handler.api['service']}"
        if self.handler.api['section']:
            path += f"/{self.handler.api['section']}"

        # Маленькая локальная функция для сборки URL с параметрами пагинации.
        def make_link(p):
            return f"{path}?page={p}&per_page={per_page}"

        # Итоговая структура ответа — классический REST-шаблон:
        # data + meta + links.
        response = {
            "data": data_list,
            "meta": {
                "total_items": total_items,
                "total_pages": total_pages,
                "current_page": page,
                "per_page": per_page
            },
            "links": {
                "self": make_link(page),
                "first": make_link(1),
                "last": make_link(total_pages),
                # next/prev = None если листать некуда. Это "відмості про
                # наявність/відсутність посилань" из ДЗ "Формування метаданих".
                "next": make_link(page + 1) if page < total_pages else None,
                "prev": make_link(page - 1) if page > 1 else None
            }
        }
        self.send_json(response)

# -----------------------------------------------------------------------------
# UsersController демонстрирует пагинацию на отдельной сущности "пользователи".
# -----------------------------------------------------------------------------
class UsersController(BaseController):
    def do_GET(self):
        # Імітація бази даних — 45 пользователей.
        mock_db = [{"id": i, "name": f"User_{i}"} for i in range(1, 46)]

        total = len(mock_db)
        # Индексы начала/конца среза страницы.
        start = (self.handler.page - 1) * self.handler.per_page
        end = start + self.handler.per_page

        # Непосредственно "вибірка за даними пагінації".
        paged_data = mock_db[start:end]

        # Защита от ухода "за край" массива: если клиент попросил страницу,
        # которой нет (например, page=100), возвращаем 404.
        if not paged_data and self.handler.page > 1:
            self.send_json({"error": "Page not found"}, 404)
            return

        # Отправляем страницу + мета + ссылки.
        self.response_with_pagination(paged_data, total)
