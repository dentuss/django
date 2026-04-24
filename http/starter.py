from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import socket
import sys
import importlib
import os
from controllers.rest_response import RestStatus

# =============================================================================
# КОНСПЕКТ: starter.py — "ядро" HTTP-сервера в этом проекте.
#
# Здесь реализованы:
#   * собственный RequestHandler поверх стандартного BaseHTTPRequestHandler;
#   * "access manager" — точка входа, через которую проходят все запросы
#     (аналог диспетчера в MVC);
#   * раздача статических файлов с "белым списком" расширений;
#   * динамическая маршрутизация: URL /<service>/<section> -> автоматически
#     ищется модуль controllers.<service>_controller и класс
#     <Service>Controller. Это и есть "маршрутизация контролерів".
#
# Жизненный цикл запроса:
#   1) handle_one_request читает одну HTTP-строку.
#   2) access_manager выполняет маршрутизацию/раздачу статики.
#   3) Найденный контроллер через .serve() формирует ответ.
# =============================================================================

DEV_MODE = True  # В DEV показываем сообщения об ошибках в теле ответа. В проде — нет.

def url_decode(input_str: str | None) -> str | None:
    # Обёртка над urllib.parse.unquote_plus с защитой от None.
    # Декодирует %-последовательности и '+' как пробел.
    return None if input_str is None else urllib.parse.unquote_plus(input_str)


# -----------------------------------------------------------------------------
# AccessManagerRequestHandler — промежуточный базовый класс.
# Он перехватывает обработку одной HTTP-строки и вместо стандартного
# do_GET/do_POST направляет поток управления в метод access_manager().
# Так достигается "единая точка входа" для всех запросов.
# -----------------------------------------------------------------------------
class AccessManagerRequestHandler(BaseHTTPRequestHandler):
    def handle_one_request(self):
        # Метод-переопределение из стандартного http.server.
        # Вместо вызова do_<METHOD> мы сами разбираем строку и вызываем
        # access_manager, чтобы контролировать поток.
        try:
            self.raw_requestline = self.rfile.readline(65537)
            if len(self.raw_requestline) > 65536:
                self.send_error(414) # Request-URI Too Long
                return
            if not self.raw_requestline:
                self.close_connection = 1
                return
            if not self.parse_request():
                return

            mname = 'access_manager'
            if not hasattr(self, mname):
                # ДЗ: Практика. Работа с проєктом — используем статические
                # статусы вместо магических чисел (501 Not Implemented).
                status = RestStatus.NOT_IMPLEMENTED()
                self.send_error(status.code, "Method 'access_manager' not overriden")
                return

            method = getattr(self, mname)
            method()
            self.wfile.flush()
        except socket.timeout as e:
            self.log_error("Request timed out: %r", e)
            self.close_connection = 1
            return

    def access_manager(self):
        # Базовая реализация: если наследник не переопределил access_manager,
        # "падаем" на дефолтную диспетчеризацию по do_<METHOD>.
        mname = 'do_' + self.command
        if not hasattr(self, mname):
            # ДЗ: Практика — 405 через фабрику статусов.
            status = RestStatus.METHOD_NOT_ALLOWED()
            self.send_error(status.code, f"Unsupported method: {self.command}")
            return
        method = getattr(self, mname)
        method()


# -----------------------------------------------------------------------------
# RequestHandler — основной обработчик запросов. Здесь живёт вся бизнес-логика:
#   * разбор query-string;
#   * разбор маршрута (service/section);
#   * раздача статики с whitelist (ДЗ: REST імплементація);
#   * динамическая загрузка контроллера и вызов serve().
# -----------------------------------------------------------------------------
class RequestHandler(AccessManagerRequestHandler):
    def __init__(self, request, client_address, server):
        # Инициализируем "свои" атрибуты ДО вызова super().__init__, потому что
        # родитель сам прогоняет handle_one_request и наши хендлеры к ним
        # обращаются.
        self.query_params = {}
        self.api = {
            # ДЗ: Маршрутизація контролерів — позже эти поля читаются
            # UserController-ом и включаются в REST-ответ.
            "method": None,   # GET/POST/...
            "service": None,  # первая часть URL (/user/... -> "user")
            "section": None,  # вторая часть URL (/user/auth -> "auth")
        }
        super().__init__(request, client_address, server)

    def access_manager(self):
        # 1) Разделяем URL на "путь" и "query-string".
        parts = self.path.split('?', 1)
        request_path = parts[0]

        # 2) Если запрошен статический файл — отдаём его и выходим.
        if self.check_static_asset(request_path):
            return

        # 3) Заполняем api — сведения о маршруте.
        self.api["method"] = self.command
        path_parts = request_path.strip("/").split("/")
        # Если пользователь пришёл на "/" — маршрутизируем на HomeController.
        self.api["service"] = path_parts[0] if len(path_parts) > 0 and path_parts[0] else "home"
        self.api["section"] = path_parts[1] if len(path_parts) > 1 else None

        # 4) Разбор Query String в словарь query_params.
        # Пример: ?a=1&b=2&a=3 -> {"a": ["1","3"], "b": "2"}.
        # Если ключ встречается несколько раз, значение становится списком.
        query_string = parts[1] if len(parts) > 1 else ""
        for item in query_string.split('&'):
            if not item: continue
            kv = item.split('=', 1)
            key = url_decode(kv[0])
            value = url_decode(kv[1]) if len(kv) > 1 else None

            if key in self.query_params:
                if not isinstance(self.query_params[key], list):
                    self.query_params[key] = [self.query_params[key]]
                self.query_params[key].append(value)
            else:
                self.query_params[key] = value

        # 5) Динамический импорт контроллера по имени сервиса.
        # /user/... -> модуль controllers.user_controller, класс UserController.
        module_name = self.api["service"].lower() + "_controller"
        class_name = self.api["service"].capitalize() + "Controller"

        if "." not in sys.path:
            sys.path.append(".")

        try:
            controller_module = importlib.import_module(f"controllers.{module_name}")
        except Exception as ex:
            # ДЗ: Практика — 404 через фабрику (раньше было просто 404 числом).
            status = RestStatus.NOT_FOUND()
            self.send_error(status.code, f"Controller module {module_name} not found. {ex if DEV_MODE else ''}")
            return

        controller_class = getattr(controller_module, class_name, None)
        if controller_class is None:
            status = RestStatus.NOT_FOUND()
            self.send_error(status.code, f"Controller class {class_name} not found")
            return

        # 6) Создаём контроллер, передаём ему self (handler) — чтобы он имел
        # доступ к query_params, api, методам отправки ответа и т.п.
        controller_object = controller_class(self)

        if not hasattr(controller_object, 'serve'):
            # ДЗ: Практика — 501 через фабрику (Not Implemented).
            status = RestStatus.NOT_IMPLEMENTED()
            self.send_error(status.code, f"Method 'serve' not found in {class_name}")
            return

        # 7) Запускаем контроллер. Любая ошибка внутри -> 500.
        try:
            controller_object.serve()
        except Exception as ex:
            # ДЗ: Практика — 500 через фабрику RestStatus.INTERNAL_SERVER_ERROR().
            status = RestStatus.INTERNAL_SERVER_ERROR()
            message = str(ex) if DEV_MODE else status.phrase
            self.send_error(status.code, message)

    # -------------------------------------------------------------------------
    # ДЗ: REST імплементація
    # Задание: Реализовать определение Content-Type для файлов, что
    #          передаются как статические ассеты. Обеспечить "белый список" —
    #          если расширения файла нет в списке разрешённых, файл не
    #          отсылать (400 или 415).
    #
    # Что сделано в check_static_asset():
    #   1. Метод работает только для GET — для других методов возвращаем False,
    #      чтобы диспетчер пошёл дальше.
    #   2. Блокируем directory traversal (../) -> 403 Forbidden.
    #   3. Извлекаем расширение файла; если его нет — это не статика.
    #   4. allowed_media_types — это и есть "белый список". Ключ = расширение,
    #      значение = правильный Content-Type для данного типа.
    #   5. Если расширение в списке — открываем файл и отдаём его с верным
    #      Content-Type (200 OK) или 404, если файла нет.
    #   6. Если расширение НЕ в списке — возвращаем 415 Unsupported Media
    #      Type (этот статус тоже добавлен как фабрика в RestStatus).
    # -------------------------------------------------------------------------
    def check_static_asset(self, request_path: str) -> bool:
        # Статика — это только GET. Для POST/PUT/... даём диспетчеру работать.
        if self.command != "GET":
            return False

        # Защита от path traversal: отказываемся обслуживать пути, где
        # пользователь пытается "подняться" в родительские каталоги.
        if '../' in request_path:
            self.send_error(403, "Forbidden")
            return True

        _, ext = os.path.splitext(request_path)
        ext = ext.lower()

        # Если расширения нет — значит это не файл, а маршрут контроллера.
        if not ext:
            return False

        # --- БЕЛЫЙ СПИСОК РАЗРЕШЁННЫХ ТИПОВ (ДЗ: REST імплементація) ---
        # Здесь же происходит "определение Content-Type": ключ даёт расширение,
        # значение — точный MIME-тип, который мы отправим в заголовке.
        allowed_media_types = {
            ".png":  "image/png",
            ".jpg":  "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif":  "image/gif",
            ".ico":  "image/x-icon",
            ".css":  "text/css",
            ".js":   "text/javascript",
            ".html": "text/html; charset=utf-8"
        }

        if ext in allowed_media_types:
            # Файл в whitelist -> пробуем отдать.
            full_path = os.path.join("static", request_path.lstrip("/"))
            try:
                if os.path.exists(full_path) and os.path.isfile(full_path):
                    with open(full_path, "rb") as file:
                        self.send_response(200, "OK")
                        self.send_header("Content-Type", allowed_media_types[ext])
                        self.end_headers()
                        self.wfile.write(file.read())
                        return True
                else:
                    # Файла нет -> 404 (через фабрику).
                    status = RestStatus.NOT_FOUND()
                    self.send_error(status.code, f"File {request_path} not found")
                    return True
            except Exception as e:
                # Любая неожиданность при чтении -> 500.
                self.send_error(500, str(e))
                return True
        else:
            # Расширение НЕ в whitelist -> 415 Unsupported Media Type.
            # Это ключевой пункт ДЗ: "не надсилати такий файл".
            status = RestStatus.UNSUPPORTED_MEDIA_TYPE()
            self.send_error(status.code, f"{status.phrase}: {ext}")
            return True


def main():
    # Запуск сервера на localhost:8080.
    host, port = '127.0.0.1', 8080
    try:
        http_server = HTTPServer((host, port), RequestHandler)
        print(f"Server started: http://{host}:{port}")
        http_server.serve_forever()
    except Exception as e:
        print(f"Server failed: {e}")
    except KeyboardInterrupt:
        print("\nServer stopped")

if __name__ == '__main__':
    main()
