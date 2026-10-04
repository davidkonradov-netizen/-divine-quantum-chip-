#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_cluster.py — utilidades compartidas por los tests de integración.

  - until(predicate, timeout)  — espera activa hasta que predicate() sea verdadero.
  - raw_client(...)            — cliente mTLS crudo para probar aceptación/rechazo.
"""
from __future__ import annotations

import asyncio
import ssl
import time
from pathlib import Path


async def until(predicate, timeout: float, interval: float = 0.05) -> bool:
    """Espera hasta que predicate() sea True o se agote el timeout.
    Devuelve el valor de la última evaluación (bool)."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            if predicate():
                return True
        except Exception:
            pass
        await asyncio.sleep(interval)
    try:
        return bool(predicate())
    except Exception:
        return False


def _client_ctx(pki_dir: Path, cn: str, rogue: bool):
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_3
    if rogue:
        ca = pki_dir / "rogue-ca.pem"
        cert = pki_dir / f"rogue-{cn}.pem"
        key = pki_dir / f"rogue-{cn}.key"
    else:
        ca = pki_dir / "ca.pem"
        cert = pki_dir / f"{cn}.pem"
        key = pki_dir / f"{cn}.key"
    ctx.load_verify_locations(ca)
    ctx.load_cert_chain(cert, key)
    ctx.check_hostname = False  # nos identificamos por CN, no por SAN del servidor
    ctx.verify_mode = ssl.CERT_REQUIRED
    return ctx


async def raw_client(pki_dir, cn: str, endpoint, server_cn: str,
                     payload: bytes, rogue: bool = False,
                     timeout: float = 2.0):
    """
    Abre conexión mTLS a `endpoint`, envía `payload` (una línea) y devuelve
    la respuesta (bytes) o None si la conexión fue rechazada.
    """
    pki = Path(pki_dir)
    ctx = _client_ctx(pki, cn, rogue)
    host, port = endpoint
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port, ssl=ctx,
                                    server_hostname=server_cn),
            timeout=timeout,
        )
    except (ssl.SSLError, OSError, asyncio.TimeoutError, ConnectionError):
        return None

    try:
        writer.write(payload)
        await writer.drain()
        line = await asyncio.wait_for(reader.readline(), timeout=timeout)
        return line or None
    except (asyncio.TimeoutError, OSError, ssl.SSLError):
        return None
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass