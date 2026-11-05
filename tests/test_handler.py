"""Pruebas locales del handler: sin AWS, con un S3 falso en memoria."""

from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path

import pyarrow.parquet as pq
import pytest

HANDLER = (
    Path(__file__).resolve().parents[1]
    / "infra"
    / "modules"
    / "lambda"
    / "src"
    / "handler.py"
)
BUCKET = "bootcamp-test-datos"


class S3Falso:
    def __init__(self, objetos: dict[str, bytes]) -> None:
        self.objetos = objetos

    def get_object(self, Bucket: str, Key: str) -> dict:  # noqa: N803 (firma de boto3)
        assert Bucket == BUCKET
        return {"Body": io.BytesIO(self.objetos[Key])}

    def put_object(self, Bucket: str, Key: str, Body: bytes) -> None:  # noqa: N803
        assert Bucket == BUCKET
        self.objetos[Key] = Body


@pytest.fixture
def modulo(monkeypatch):
    # Prueba local: sin perfil ni credenciales reales (el cliente se reemplaza abajo).
    monkeypatch.delenv("AWS_PROFILE", raising=False)
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("PREFIJO_SALIDA", "salida/")
    spec = importlib.util.spec_from_file_location("handler", HANDLER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def evento(key: str) -> dict:
    return {"Records": [{"s3": {"bucket": {"name": BUCKET}, "object": {"key": key}}}]}


def leer_parquet(datos: bytes):
    return pq.read_table(io.BytesIO(datos))


def test_arreglo_json_se_convierte_en_parquet(modulo):
    filas = [{"id": 1, "monto": 10.5}, {"id": 2, "monto": 7.0}]
    s3 = S3Falso({"entrada/ventas.json": json.dumps(filas).encode()})
    modulo.s3 = s3

    resultado = modulo.handler(evento("entrada/ventas.json"), None)

    assert resultado == {"parquet": "salida/ventas.parquet", "filas": 2}
    assert leer_parquet(s3.objetos["salida/ventas.parquet"]).to_pylist() == filas


def test_objeto_json_unico_es_una_fila(modulo):
    s3 = S3Falso({"entrada/uno.json": b'{"id": 1, "producto": "cafe"}'})
    modulo.s3 = s3

    resultado = modulo.handler(evento("entrada/uno.json"), None)

    assert resultado["filas"] == 1
    assert leer_parquet(s3.objetos["salida/uno.parquet"]).to_pylist() == [
        {"id": 1, "producto": "cafe"}
    ]


def test_key_con_espacios_llega_codificada_en_el_evento(modulo):
    # S3 codifica la key del evento: "mis ventas.json" llega como "mis+ventas.json".
    s3 = S3Falso({"entrada/mis ventas.json": b"[]"})
    modulo.s3 = s3

    resultado = modulo.handler(evento("entrada/mis+ventas.json"), None)

    assert resultado == {"parquet": "salida/mis ventas.parquet", "filas": 0}
