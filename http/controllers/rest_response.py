# =============================================================================
# КОНСПЕКТ: Файл описывает структуру ответа REST-сервиса.
#
# REST (Representational State Transfer) — это архитектурный стиль, в котором
# клиент и сервер обмениваются "состоянием" ресурса через HTTP. Принципы:
#   * stateless (сервер не хранит состояние клиента между запросами)
#   * единый интерфейс (URI идентифицирует ресурс, метод — действие)
#   * ответ должен быть структурирован (обычно JSON)
#
# В этом проекте мы сами делаем мини-REST-обвязку поверх встроенного
# http.server, поэтому формат ответа вводим вручную: status + data.
# =============================================================================

# -----------------------------------------------------------------------------
# ДЗ: Практика. Работа с проєктом
# Задание: Реализовать статические поля RestStatus для стандартных HTTP-кодов.
#          В starter.py подобрать правильные статусы для ошибочных ситуаций.
#
# Что сделано: ниже класс RestStatus содержит набор @staticmethod-фабрик
# для типовых HTTP-статусов (OK 200, NOT_FOUND 404, METHOD_NOT_ALLOWED 405,
# UNSUPPORTED_MEDIA_TYPE 415, INTERNAL_SERVER_ERROR 500, NOT_IMPLEMENTED 501).
# Эти статусы далее вызываются в starter.py там, где раньше были "магические"
# числовые коды. Т.е. вместо send_error(404, ...) пишем
# status = RestStatus.NOT_FOUND(); self.send_error(status.code, ...).
# -----------------------------------------------------------------------------
class RestStatus:
    # Класс-обёртка вокруг HTTP-статуса. Хранит:
    #   isOk   — bool, удобный флаг "успех/ошибка" (для клиента, без разбора кода)
    #   code   — численный HTTP-код (200, 404, ...)
    #   phrase — текстовая фраза, соответствующая коду ("OK", "Not Found", ...)
    def __init__(self, isOk: bool = True, code: int = 200, phrase: str = "OK"):
        self.isOk = isOk
        self.code = code
        self.phrase = phrase

    # __json__ — наш собственный "хук" сериализации. Не стандартный для Python,
    # но мы сами вызываем его в send_rest_response() через default=lambda x: ...
    # (см. controller_rest.py). Благодаря этому json.dumps умеет сериализовать
    # наши классы как словари.
    def __json__(self):
        return {
            "isOk": self.isOk,
            "code": self.code,
            "phrase": self.phrase
        }

    # --- ДЗ: Практика. Работа с проєктом ---
    # Ниже идут статические фабрики типовых статусов. Вызов RestStatus.OK()
    # возвращает готовый объект со всеми полями, заполненными по спецификации
    # HTTP. Это и есть "статические поля для стандартных HTTP-кодов".
    @staticmethod
    def OK(): return RestStatus(True, 200, "OK")

    @staticmethod
    def NOT_FOUND(msg="Not Found"):
        # 404 — запрошенный ресурс (контроллер, файл, запись) не найден
        return RestStatus(False, 404, msg)

    @staticmethod
    def METHOD_NOT_ALLOWED(msg="Method Not Allowed"):
        # 405 — HTTP-метод (GET/POST/...) не поддерживается данным ресурсом
        return RestStatus(False, 405, msg)

    @staticmethod
    def UNSUPPORTED_MEDIA_TYPE(msg="Unsupported Media Type"):
        # 415 — запрошен файл с расширением, которого нет в "белом списке".
        # Используется в starter.check_static_asset() как часть
        # ДЗ по REST-имплементации (Content-Type + whitelist).
        return RestStatus(False, 415, msg)

    @staticmethod
    def INTERNAL_SERVER_ERROR(msg="Internal Server Error"):
        # 500 — непредвиденная ошибка при выполнении контроллера
        return RestStatus(False, 500, msg)

    @staticmethod
    def NOT_IMPLEMENTED(msg="Not Implemented"):
        # 501 — запрошенная функциональность отсутствует
        # (например, наследник не переопределил access_manager)
        return RestStatus(False, 501, msg)


# -----------------------------------------------------------------------------
# RestResponse — обёртка для REST-ответа. Хранит статус и полезную нагрузку
# (data). Любой контроллер, унаследованный от ControllerRest, заполняет
# self.rest_response.data — а базовый класс сам выводит этот объект в JSON.
# -----------------------------------------------------------------------------
class RestResponse:
    def __init__(self, status: RestStatus | None = None, data: any = None):
        # По умолчанию статус — 200 OK (успех).
        self.status = status if status is not None else RestStatus.OK()
        self.data = data

    def __json__(self):
        # Формат итогового JSON: { "status": {...}, "data": ... }
        # data может быть любой сериализуемой структурой (dict/list/...),
        # в т.ч. результат пагинации из RestPagination.paginate().
        return {
            "status": self.status.__json__(),
            "data": self.data
        }
