from http.server import BaseHTTPRequestHandler
from controllers.controller_rest import ControllerRest


# КОНСПЕКТ: UserController — наследник ControllerRest
#
# ControllerRest (см. controller_rest.py) берёт на себя весь "шаблонный" код:
#   - поиск метода do_GET/do_POST/...
#   - вызов before_execution/after_execution
#   - отправку JSON-ответа через self.rest_response
#
# В наследнике нужно лишь заполнить self.rest_response.data — и всё, JSON
# соберётся сам. Это и есть смысл шаблонного метода (template method pattern)





# ДЗ: Маршрутизація контролерів
# Задание: Включить в self.rest_response.data UserController сведения о:
#            - query_string (строка параметров запроса)
#            - api параметрах (method, service, section)
#
# Что сделано: в do_GET ниже формируется словарь data с ключами:
#   - result           — "бизнес"-часть ответа (просто пример данных)
#   - query_params     — разобранный словарь параметров ?key=value&...
#   - api_params       — словарь {method, service, section} из маршрута
#   - raw_query_string — сырая строка query после "?" в URL
# Эти данные клиент увидит в ответе и сможет проверить, как сработала
# маршрутизация

class UserController(ControllerRest):
    def __init__(self, handler: BaseHTTPRequestHandler):
        # Передаём handler в родителя, чтобы он сохранил его в self.handler и
        # проинициализировал self.rest_response = RestResponse()
        super().__init__(handler)

    def do_GET(self):
        # Родитель (ControllerRest.serve) после вызова этого метода сам
        # отправит JSON. Нам нужно только заполнить self.rest_response.data
        self.rest_response.data = {
            # Пример полезной нагрузки: произвольные поля "бизнес-ответа"
            "result": {
                "x": 10,
                "y": 20,
                "w": 30,
                "t": "Вітання!!"
            },

            # ДЗ: Маршрутизація контролерів
            # query_params — словарь параметров из строки запроса:
            # для /user?name=Ivan&age=30 это {"name": "Ivan", "age": "30"}
            # getattr с дефолтом {} защищает от случая, если handler
            # не готовил этот атрибут
            "query_params": getattr(self.handler, 'query_params', {}),

            # api_params — сведения о разобранном маршруте:
            # {"method": "GET", "service": "user", "section": "auth"}
            # Заполняется в starter.py в access_manager() до вызова контроллера
            "api_params": getattr(self.handler, 'api', {}),

            # raw_query_string — исходная строка параметров без разбора
            # Для запроса /user/auth?x=1&y=2 здесь будет "x=1&y=2"
            # Полезна, если клиенту важен точный оригинал URL
            "raw_query_string": self.handler.path.split('?', 1)[1] if '?' in self.handler.path else ""
        }
