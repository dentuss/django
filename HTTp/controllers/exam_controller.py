import json


class ExamController:
    def __init__(self, handler):
        self.handler = handler

    def do_GET(self):
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # Изменение: маршрут /exam теперь поддерживает два сценария
        # Зачем: закрыть практические задания — HTML-страница и JSON-контроллер
        if self.handler.api.get("section") == "api":
            payload = {
                "message": "Exam endpoint is alive",
                "project": "HTTP",
                "status": "ok",
            }
            self.handler.send_response(200)
            self.handler.send_header("Content-Type", "application/json; charset=utf-8")
            self.handler.end_headers()
            self.handler.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
            return

        html = """
        <h1>Exam Page</h1>
        <p>Сторінка /exam працює.</p>
        <p>JSON-версія доступна за адресою <code>/exam/api</code>.</p>
        """
        self.handler.send_response(200)
        self.handler.send_header("Content-Type", "text/html; charset=utf-8")
        self.handler.end_headers()
        self.handler.wfile.write(html.encode("utf-8"))

    def serve(self):
        if self.handler.command == "GET":
            self.do_GET()
            return
        self.handler.send_error(405, "Method Not Allowed")
