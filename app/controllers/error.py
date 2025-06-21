from flask import Flask, render_template


class ErrorController:
    def __init__(self, app: Flask) -> None:
        self.app = app
        self._register_routes()

    def _register_routes(self) -> None:
        self.app.register_error_handler(403, self.handle_403)
        self.app.register_error_handler(404, self.handle_404)
        self.app.register_error_handler(500, self.handle_500)

    @staticmethod
    def handle_403(error):
        print(f"[!] 403 Forbidden: {error} ({type(error).__name__})")
        return render_template(template_name_or_list="errors/403.html"), 403

    @staticmethod
    def handle_404(error):
        print(f"[!] 404 Not Found: {error} ({type(error).__name__})")
        return render_template(template_name_or_list="errors/404.html"), 404

    @staticmethod
    def handle_500(error):
        print(f"[!] 500 Internal Server Error: {error} ({type(error).__name__})")
        return render_template(template_name_or_list="errors/500.html"), 500
