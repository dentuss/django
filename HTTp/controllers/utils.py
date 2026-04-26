import math


# КОНСПЕКТ: Пагинация в REST
#
# Пагинация — способ отдавать большой список данных "страницами", а не целиком
# Клиент запрашивает ресурс с параметрами ?page=N&page_size=M, а сервер
# возвращает только нужный срез + метаданные, по которым клиент понимает:
#   - сколько всего записей
#   - сколько страниц
#   - на какой странице мы сейчас
#   - есть ли "следующая" / "предыдущая" страница
#
# Такой ответ — сам по себе ресурс, поэтому структура хорошо ложится в REST:
# data + metadata + links



# ДЗ: REST — метаданные для массива + пагинация
# Задание: Составить метаданные для данных типа "массив", предусмотреть
#          пагинацию. Соблюдать принципы REST
#
# ДЗ: Формування метаданих
# Задание (расширение): Расширить метаданные RestPagination — включить
#          сведения о наличии/отсутствии ссылок на предыдущую и следующую
#          страницы. Реализовать выборку товаров по данным пагинации
#
# Что сделано:
#   1) Класс RestPagination с методом paginate() формирует JSON-структуру,
#      которая включает:
#        - metadata: total_items, total_pages, current_page, page_size,
#                    has_next, has_previous  <- ДЗ Формування метаданих
#        - links: next, prev  <- номера страниц для переходов, или None,
#                 если страницы нет (ДЗ: признак наличия/отсутствия ссылок)
#        - results: срез массива по текущей странице  <- ДЗ: "вибірка за
#                 даними пагінації" реализована через data[start:end]
#   2) Используется из product_controller.ProductController.get_products()
#      (именно "выборка товаров")

class RestPagination:
    @staticmethod
    def paginate(data, page, page_size):
        # Защищаемся от некорректных входных значений:
        # page/page_size могут прийти как строки из URL или как None
        # max(1, ...) гарантирует, что страница >= 1 и размер страницы >= 1
        try:
            page = max(1, int(page))
            page_size = max(1, int(page_size))
        except (ValueError, TypeError):
            # Значения по умолчанию при некорректном вводе
            page, page_size = 1, 10

        total_items = len(data)
        # math.ceil чтобы "хвост" данных (<page_size) тоже был отдельной страницей
        total_pages = math.ceil(total_items / page_size)

        # Срез данных: индексы элементов, принадлежащих текущей странице
        # Пример: page=2, page_size=5 => элементы [5:10]
        start = (page - 1) * page_size
        end = start + page_size
        paginated_data = data[start:end]

        # ДЗ: Формування метаданих
        # Булевы флаги, по которым клиент понимает, можно ли листать дальше/назад
        has_next = page < total_pages
        has_previous = page > 1

        # Финальная REST-структура.
        # Все три ключа (metadata, links, results) делают ответ самодостаточным:
        # клиент получает и данные, и инструкцию "как двигаться по списку"
        return {
            "metadata": {
                "total_items": total_items,     # всего записей
                "total_pages": total_pages,     # всего страниц
                "current_page": page,           # текущая страница
                "page_size": page_size,         # размер страницы
                "has_next": has_next,           # можно ли перейти вперёд
                "has_previous": has_previous    # можно ли перейти назад
            },
            "links": {
                # Номер следующей/предыдущей страницы или None, если её нет
                # Это и есть "наличие/отсутствие посилань" из ДЗ
                "next": page + 1 if has_next else None,
                "prev": page - 1 if has_previous else None
            },
            "results": paginated_data           # данные самой страницы (срез)
        }
