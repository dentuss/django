# КОНСПЕКТ: HomeController — контроллер корневого маршрута "/"
#
# starter.py, когда не находит "service" в URL (т.е. пользователь пришёл на "/"),
# подставляет имя "home" -> грузит этот файл и класс HomeController
# Здесь нет REST-обёртки (RestResponse), мы сами формируем HTML
#
# Тут важно:
#   - как из контроллера писать заголовки и тело ответа вручную;
#   - как работает "нестандартный" HTTP-метод LINK (клиентский JS делает
#     fetch с method:"LINK", а у нас do_LINK его обрабатывает)

class HomeController:
    def __init__(self, handler):
        # handler — это наш RequestHandler из starter.py. Через него пишем ответ
        self.handler = handler

    def do_GET(self):
        # Отправляем заголовки через handler
        self.handler.send_response(200)
        self.handler.send_header("Content-Type", "text/html; charset=utf-8")
        self.handler.end_headers()

        # Контент — простой HTML с кнопкой и inline-скриптом,
        # который демонстрирует нестандартный метод LINK
        html = """
        <h1>HTTP Server Working</h1>
        <img src="/img/Python.png" alt="logo" width="150" />
        <hr/>
        <button onclick="linkClick()">Send LINK request</button>
        <!-- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
             Изменение: добавлена учебная ссылка на /exam,
             чтобы быстро проверить новый маршрут и контроллер. -->
        <p><a href="/exam">Open /exam</a> | <a href="/exam/api">Open /exam/api</a></p>
        <p id="out"></p>
        <script>
            function linkClick() {
                fetch("/", { method: "LINK" })
                .then(r => r.text())
                .then(t => document.getElementById('out').innerText = t);
            }
        </script>
        """
        self.handler.wfile.write(html.encode('utf-8'))

    def do_LINK(self):
        # Обработчик нестандартного HTTP-метода LINK
        # В starter.py через do_<METHOD> он вызывается автоматически —
        # благодаря единому диспетчеру по имени метода
        self.handler.send_response(200)
        self.handler.send_header("Content-Type", "text/plain; charset=utf-8")
        self.handler.end_headers()
        self.handler.wfile.write("LINK method response received!".encode('utf-8'))
