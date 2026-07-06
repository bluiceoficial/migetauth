# Copyright (C) 2026 Murilo Gomes Julio
# SPDX-License-Identifier: GPL-2.0-only

# Site: https://github.com/bluiceoficial

import base64, hmac, hashlib, time, struct

def base32_decode(secret: str) -> bytes:
    secret = secret.upper().replace(" ", "")
    return base64.b32decode(secret, casefold=True)

def generate_totp(secret: str) -> str:
    secret = secret.upper().replace(" ", "")
    key = base32_decode(secret)
    counter = int(time.time()) // 30

    # converte para 8 bytes (big endian)
    msg = struct.pack(">Q", counter)

    h = hmac.new(key, msg, hashlib.sha1).digest()

    # dynamic truncation
    offset = h[-1] & 0x0F
    code = (
        ((h[offset] & 0x7F) << 24) |
        ((h[offset + 1] & 0xFF) << 16) |
        ((h[offset + 2] & 0xFF) << 8) |
        (h[offset + 3] & 0xFF)
    )

    # 6 dígitos
    return str(code % 1_000_000).zfill(6)
