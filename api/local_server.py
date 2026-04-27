import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from main import main


HOST = os.environ.get("CONTACT_API_HOST", "127.0.0.1")
PORT = int(os.environ.get("CONTACT_API_PORT", "8000"))


class ContactRequestHandler(BaseHTTPRequestHandler):
    def _send_lambda_response(self, response: dict) -> None:
        status_code = response.get("statusCode", 500)
        body = response.get("body", "")

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "http://localhost:4200")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def do_OPTIONS(self) -> None:
        self._send_lambda_response({"statusCode": 204, "body": ""})

    def do_POST(self) -> None:
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length).decode("utf-8")
        event = {
            "version": "2.0",
            "rawPath": self.path,
            "body": raw_body,
            "requestContext": {
                "http": {
                    "method": "POST",
                    "path": self.path,
                }
            },
        }
        self._send_lambda_response(main(event, None))

    def log_message(self, format: str, *args) -> None:
        print(f"{self.address_string()} - {format % args}")


if __name__ == "__main__":
    os.environ.setdefault("ENVIRONMENT_CONFIG", "local.config.json")
    server = ThreadingHTTPServer((HOST, PORT), ContactRequestHandler)
    print(f"Serving local contact API on http://{HOST}:{PORT}")
    server.serve_forever()
