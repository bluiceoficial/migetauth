# Copyright (C) 2026 Murilo Gomes Julio
# SPDX-License-Identifier: GPL-2.0-only

import io, os, zipfile, urllib.request, urllib.error, urllib.parse
from core import BASE_DIR, DB_NAME, KEY_FILE


def _montar_url(ip, porta, senha, endpoint):
    return f"http://{ip}:{porta}/{endpoint}?pw={urllib.parse.quote(senha, safe='')}"


def ping(ip, porta, senha, timeout=3):
    url = _montar_url(ip, porta, senha, "ping")
    resp = urllib.request.urlopen(url, timeout=timeout)
    return resp.status == 200


def download(ip, porta, senha, timeout=10):
    url = _montar_url(ip, porta, senha, "download")
    try:
        resp = urllib.request.urlopen(url, timeout=timeout)
        if resp.status != 200:
            raise RuntimeError(f"Erro HTTP {resp.status}")
        data = resp.read()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Erro HTTP {e.code}: {e.read().decode()}")
    except Exception as e:
        raise RuntimeError(f"Falha na conexão: {e}")

    os.makedirs(BASE_DIR, exist_ok=True)
    for f in (DB_NAME, KEY_FILE):
        if os.path.exists(f):
            os.remove(f)
    buf = io.BytesIO(data)
    with zipfile.ZipFile(buf, "r") as z:
        z.extract("auth.db", BASE_DIR)
        z.extract("secret.key", BASE_DIR)

    # Recarrega a chave Fernet
    import importlib, core as core_module
    from cryptography.fernet import Fernet
    core_module.fernet = Fernet(open(KEY_FILE, "rb").read())

    return True


def upload(ip, porta, senha, timeout=10):
    if not os.path.exists(DB_NAME) or not os.path.exists(KEY_FILE):
        raise RuntimeError("Banco local ou chave não encontrados")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(DB_NAME, "auth.db")
        z.write(KEY_FILE, "secret.key")
    data = buf.getvalue()

    url = _montar_url(ip, porta, senha, "upload")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/zip")
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        if resp.status != 200:
            raise RuntimeError(f"Erro HTTP {resp.status}")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Erro HTTP {e.code}: {e.read().decode()}")
    except Exception as e:
        raise RuntimeError(f"Falha na conexão: {e}")

    return True
