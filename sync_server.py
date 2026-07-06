# Copyright (C) 2026 Murilo Gomes Julio
# SPDX-License-Identifier: GPL-2.0-only
#
# Servidor de sincronia — executa no PC para receber/enviar DB + chave.
# Uso:  python sync_server.py
#       python sync_server.py --port 5555 --password minhasenha

import argparse, io, os, threading, zipfile
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

BASE_DIR = os.path.expanduser("~/.config/migetauth")
DB_NAME = os.path.join(BASE_DIR, "auth.db")
KEY_FILE = os.path.join(BASE_DIR, "secret.key")


class SyncHandler(BaseHTTPRequestHandler):
    password = "migetauth"

    def _auth(self):
        qs = parse_qs(urlparse(self.path).query)
        return qs.get("pw", [""])[0]

    def _send_json(self, code, data):
        import json
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_zip(self):
        if not os.path.exists(DB_NAME) or not os.path.exists(KEY_FILE):
            self._send_json(500, {"error": "Arquivos do banco ainda não existem"})
            return
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            z.write(DB_NAME, "auth.db")
            z.write(KEY_FILE, "secret.key")
        data = buf.getvalue()
        self.send_response(200)
        self.send_header("Content-Type", "application/zip")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _receive_zip(self, data):
        os.makedirs(BASE_DIR, exist_ok=True)
        for f in (DB_NAME, KEY_FILE):
            if os.path.exists(f):
                os.remove(f)
        buf = io.BytesIO(data)
        with zipfile.ZipFile(buf, "r") as z:
            z.extract("auth.db", BASE_DIR)
            z.extract("secret.key", BASE_DIR)
        return True

    def do_GET(self):
        path = self.path.split("?")[0]
        if self._auth() != self.password:
            self._send_json(403, {"error": "Senha incorreta"})
            return
        if path == "/ping":
            self._send_json(200, {"status": "ok"})
        elif path == "/download":
            self._send_zip()
        else:
            self._send_json(404, {"error": "Endpoint inválido"})

    def do_POST(self):
        path = self.path.split("?")[0]
        if self._auth() != self.password:
            self._send_json(403, {"error": "Senha incorreta"})
            return
        if path == "/upload":
            length = int(self.headers.get("Content-Length", 0))
            data = self.rfile.read(length)
            try:
                self._receive_zip(data)
                self._send_json(200, {"status": "ok", "message": "Banco sincronizado"})
            except Exception as e:
                self._send_json(500, {"error": str(e)})
        else:
            self._send_json(404, {"error": "Endpoint inválido"})

    def log_message(self, fmt, *args):
        msg = f"[sync_server] {args[0]} {args[1]} {args[2]}"
        log = getattr(self.__class__, '_log_callback', None)
        if log:
            log(msg)
        else:
            print(msg)


def obter_ip_local():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def start_server(port=5555, password="migetauth", log_callback=None):
    """Inicia o servidor em uma thread separada. Retorna (server, thread, ip)."""
    SyncHandler.password = password
    SyncHandler._log_callback = log_callback
    ip = obter_ip_local()
    server = HTTPServer(("0.0.0.0", port), SyncHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, ip


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Servidor de sincronia MiGetAuth")
    parser.add_argument("--port", type=int, default=5555, help="Porta (padrão: 5555)")
    parser.add_argument("--password", type=str, default="migetauth", help="Senha de acesso")
    args = parser.parse_args()

    ip = obter_ip_local()
    print("=" * 50)
    print("  Servidor MiGetAuth rodando em:")
    print(f"  IP: {ip}")
    print(f"  Porta: {args.port}")
    print(f"  Senha: {args.password}")
    print("=" * 50)
    print("  No app mobile, use:")
    print(f"    IP: {ip}")
    print(f"    Porta: {args.port}")
    print(f"    Senha: {args.password}")
    print("=" * 50)

    server = HTTPServer(("0.0.0.0", args.port), SyncHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
        server.server_close()
