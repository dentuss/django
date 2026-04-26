from http.server import BaseHTTPRequestHandler
from controllers.rest_response import RestResponse, RestStatus
import json


# КОНСПЕКТ: ControllerRest — базовый REST-контроллер
#
# Это реализация паттерна "Template Method": базовый класс описывает общий
# алгоритм (serve), а конкретные действия (do_GET, do_POST, ...) определяют
# наследники. Базовый класс заботится о:
#   - диспетчеризации по HTTP-методу (serve ищет do_<METHOD>);
#   - запуске before_execution / after_execution (хуки для расширений);
#   - перехвате ошибок и преобразовании их в корректный REST-ответ;
#   - сериализации RestResponse в JSON
#
# Наследнику ( user_controller.py) остаётся только переопределить do_GET
# и заполнить self.rest_response.data


# С целью избегания адреса /rest меняем правило именования для класса
# (иначе URL /rest маршрутизировался бы на сам класс-родитель)
class ControllerRest :
  def __init__(self, handler: BaseHTTPRequestHandler):
    # Сохраняем HTTP-обработчик — через него пишем заголовки и тело ответа
    self.handler = handler
    # Заготовка ответа: по умолчанию пустой OK. Наследник её дополняет
    self.rest_response = RestResponse()


  def before_execution(self):
    # Хук "до основного действия". Наследник может переопределить для
    # аутентификации, логирования, проверки прав и т.п.
    pass


  def after_execution(self):
    # Хук "после основного действия"
    pass


  # Основной метод запуска контроллера, который обеспечивает жизненный цикл запроса
  def serve(self):
    # По имени HTTP-метода ищем метод класса: GET -> do_GET, POST -> do_POST ...
    mname = 'do_' + self.handler.command
    if not hasattr(self, mname):
      # Метод не реализован — 405 Method Not Allowed
      # (Здесь используется прямой RestStatus с явным кодом 405; в
      # rest_response.py есть также фабрика RestStatus.METHOD_NOT_ALLOWED.)
      self.rest_response.status = RestStatus(
        is_ok = False,
        code = 405,
        phrase = "Unsupported method (%r) in '%r'" % (self.handler.command, self.__class__.__name__)
      )
    else:
      method = getattr(self, mname)
      # выполняем метод, передавая управление контроллеру
      try:
        self.before_execution()
        method()                 # <- здесь вызывается наследный do_GET/...
        self.after_execution()
        self.send_success()
        return
      except Exception as ex:
        # Любая ошибка внутри action -> 500 Internal Server Error
        self.rest_response.status = RestStatus(
          is_ok = False,
          code = 500,
          phrase = "Request processing error " + str(ex)
        )
    self.send_error()


  def send_success(self):
    # Успех — обычный REST-ответ
    self.send_rest_response()


  def send_error(self):
    # При ошибке отдаём точно такой же формат, просто status.isOk = False
    # Клиенту это удобнее, чем разные форматы на 2xx и 4xx
    self.send_rest_response()


  def send_rest_response(self):
    # Единая точка отправки JSON-ответа
    # Заголовки говорят клиенту: это JSON в UTF-8
    self.handler.send_response(200, "OK")
    self.handler.send_header("Content-Type", "application/json; charset=utf-8")
    self.handler.end_headers()
    # json.dumps не умеет сам сериализовать наши классы. Поэтому передаём
    # default=lambda: если у объекта есть метод __json__ — используем его
    # (см. rest_response.py), иначе приводим к строке. Это позволяет
    # писать self.rest_response.data = {"status": RestStatus.OK()} и
    # получать корректный JSON
    self.handler.wfile.write(
      json.dumps(
        self.rest_response,
        ensure_ascii=False,
        default=lambda x: x.__json__() if hasattr(x, "__json__") else str(x)
      ).encode()
    )
