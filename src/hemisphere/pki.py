#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pki.py — generación de PKI de desarrollo para los sitios y sus hemisferios.

Produce, en pki_dir:
  ca.pem, ca.key                — CA raíz legítima (ECDSA P-256)
  {cn}.pem, {cn}.key            — certificado + clave por CN (firmados por CA)
  rogue-ca.pem, rogue-ca.key    — CA intrusa (solo si rogue=True)
  rogue-{cn}.pem, rogue-{cn}.key— certs firmados por la CA intrusa (solo si rogue=True)

Requiere `cryptography`. Todos los certificados son ECDSA P-256, SHA-256, 1 año
de validez, con SAN = DNS:CN para que `check_hostname=True` funcione.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID


def _write(path: Path, data: bytes):
    path.write_bytes(data)


def _make_ca(common_name: str, days: int = 365):
    key = ec.generate_private_key(ec.SECP256R1())
    subject = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Kernel de Dios"),
    ])
    now = datetime.now(timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=5))
        .not_valid_after(now + timedelta(days=days))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .add_extension(x509.KeyUsage(
            digital_signature=True, content_commitment=False,
            key_encipherment=False, data_encipherment=False,
            key_agreement=False, key_cert_sign=True, crl_sign=True,
            encipher_only=False, decipher_only=False), critical=True)
        .sign(key, hashes.SHA256())
    )
    return key, cert


def _make_leaf(cn: str, ca_key, ca_cert, days: int = 365):
    key = ec.generate_private_key(ec.SECP256R1())
    subject = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, cn),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Kernel de Dios"),
    ])
    now = datetime.now(timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_cert.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=5))
        .not_valid_after(now + timedelta(days=days))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(x509.KeyUsage(
            digital_signature=True, content_commitment=False,
            key_encipherment=True, data_encipherment=False,
            key_agreement=False, key_cert_sign=False, crl_sign=False,
            encipher_only=False, decipher_only=False), critical=True)
        .add_extension(x509.ExtendedKeyUsage([
            x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
            x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH,
        ]), critical=False)
        .add_extension(x509.SubjectAlternativeName([x509.DNSName(cn)]), critical=False)
        .sign(ca_key, hashes.SHA256())
    )
    return key, cert


def _dump_key(key, path: Path):
    _write(path, key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ))


def _dump_cert(cert, path: Path):
    _write(path, cert.public_bytes(serialization.Encoding.PEM))


def make_pki(pki_dir, common_names, rogue: bool = False) -> dict:
    """
    Genera la PKI completa. Devuelve metadatos.

    Args:
        pki_dir: Path del directorio (se crea si no existe).
        common_names: iterable de CNs (ej: ["V1", ..., "V12", "V1.L", "V1.R", ...]).
        rogue: si True, genera además una CA intrusa con los mismos CNs.
    """
    pki = Path(pki_dir)
    pki.mkdir(parents=True, exist_ok=True)

    # CA legítima
    ca_key, ca_cert = _make_ca("kernel-dios-ca")
    _dump_key(ca_key, pki / "ca.key")
    _dump_cert(ca_cert, pki / "ca.pem")

    cns = sorted(set(common_names))
    for cn in cns:
        k, c = _make_leaf(cn, ca_key, ca_cert)
        _dump_key(k, pki / f"{cn}.key")
        _dump_cert(c, pki / f"{cn}.pem")

    meta = {
        "pki_dir": str(pki),
        "ca": "ca.pem",
        "cns": cns,
        "rogue": bool(rogue),
    }

    # CA intrusa (para tests de seguridad)
    if rogue:
        r_key, r_cert = _make_ca("rogue-ca")
        _dump_key(r_key, pki / "rogue-ca.key")
        _dump_cert(r_cert, pki / "rogue-ca.pem")
        for cn in cns:
            k, c = _make_leaf(cn, r_key, r_cert)
            _dump_key(k, pki / f"rogue-{cn}.key")
            _dump_cert(c, pki / f"rogue-{cn}.pem")
        meta["rogue_ca"] = "rogue-ca.pem"

    return meta


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "./pki"
    cns = [f"V{i}" for i in range(1, 13)] + \
          [f"V{i}.L" for i in range(1, 13)] + \
          [f"V{i}.R" for i in range(1, 13)]
    m = make_pki(out, cns, rogue=True)
    print(f"PKI generada en {m['pki_dir']}: {len(m['cns'])} CNs, rogue={m['rogue']}")