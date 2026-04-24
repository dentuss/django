import json
from .rest_response import RestStatus
from .utils import RestPagination

# =============================================================================
# КОНСПЕКТ: ProductController — пример REST-контроллера со страничной выдачей.
#
# Контроллер — класс, который обрабатывает запрос, определённый маршрутом.
# starter.py динамически находит класс по имени URL (/product -> ProductController)
# и вызывает метод serve(). Далее контроллер сам решает, что делать.
#
# Здесь:
#   GET /product?page=1&page_size=5 — вернуть порцию массива products_db.
#   Ответ формируется через RestPagination.paginate (см. utils.py).
# =============================================================================

# -----------------------------------------------------------------------------
# ДЗ: Формування метаданих
# Задание (часть): "Реалізувати вибірку товарів за даними пагінації".
#
# Что сделано:
#   * products_db — массив из 25 товаров (моковая БД).
#   * Метод get_products() читает из query_params параметры page и page_size,
#     передаёт их в RestPagination.paginate и возвращает клиенту готовую
#     REST-страницу: metadata + links + results.
# -----------------------------------------------------------------------------
class ProductController:
    def __init__(self, handler):
        # handler — это экземпляр RequestHandler (см. starter.py). Через него
        # доступны query_params, api, методы send_response/send_header и т.п.
        self.handler = handler

        # Мок-данные: 25 товаров с полями id, name, price.
        # В реальном приложении данные приходили бы из БД/ORM.
        self.products_db = [
            {"id": i, "name": f"Товар {i}", "price": i * 100}
            for i in range(1, 26)
        ]

    def serve(self):
        # serve() — точка входа, которую вызывает starter.py после маршрутизации.
        # Решаем, какой HTTP-метод пришёл, и распределяем обработку.
        if self.handler.command == "GET":
            self.get_products()
        else:
            # Если запрос пришёл не-GET-методом — возвращаем 405.
            # ДЗ: Практика. Работа с проєктом — вместо "магических" чисел
            # используем статическую фабрику RestStatus.METHOD_NOT_ALLOWED().
            status = RestStatus.METHOD_NOT_ALLOWED()
            self.handler.send_error(status.code, status.phrase)

    def get_products(self):
        # Читаем параметры пагинации из query-string.
        # Если параметр не передан — используем значения по умолчанию.
        page = self.handler.query_params.get('page', 1)
        page_size = self.handler.query_params.get('page_size', 5)

        # Делегируем формирование страницы утилите RestPagination.
        # Она сама проверит корректность значений и вернёт готовый dict.
        response_data = RestPagination.paginate(
            data=self.products_db,
            page=page,
            page_size=page_size
        )

        # Ручная отправка HTTP-ответа (JSON). Делаем это не через ControllerRest,
        # а напрямую через handler — здесь мы не наследник ControllerRest.
        self.handler.send_response(200)
        self.handler.send_header("Content-Type", "application/json")
        self.handler.end_headers()

        # ensure_ascii=False — сохраняем кириллицу в читабельном виде,
        # иначе json.dumps превратит её в \uXXXX-последовательности.
        response_json = json.dumps(response_data, ensure_ascii=False)
        self.handler.wfile.write(response_json.encode('utf-8'))
