"""Prueba de punta a punta del pipeline desplegado (prueba previa del ponente).

Requiere `terraform apply` en infra/ y credenciales en el entorno.
Ejecutar con: uv run pytest -m cloud
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

import pytest
from aws_session import get_client, get_session

RAIZ = Path(__file__).resolve().parents[2]
pytestmark = pytest.mark.cloud


def _outputs() -> dict:
    salida = subprocess.run(
        ["terraform", f"-chdir={RAIZ / 'infra'}", "output", "-json"],
        capture_output=True,
        text=True,
        check=True,
    )
    return {k: v["value"] for k, v in json.loads(salida.stdout).items()}


@pytest.fixture(scope="module")
def outputs() -> dict:
    try:
        credenciales = get_session().get_credentials()
    except Exception as error:  # p. ej. un AWS_PROFILE que no existe
        pytest.skip(f"Credenciales de AWS no válidas: {error}")
    if credenciales is None:
        pytest.skip("Sin credenciales de AWS en el entorno")
    datos = _outputs()
    if not datos:
        pytest.skip("No hay outputs: ¿se ejecutó terraform apply en infra/?")
    return datos


def test_log_group_tiene_retencion(outputs):
    grupos = get_client("logs").describe_log_groups(
        logGroupNamePrefix=outputs["log_group_name"]
    )
    grupo = next(
        g for g in grupos["logGroups"] if g["logGroupName"] == outputs["log_group_name"]
    )
    assert grupo.get("retentionInDays"), "El log group debe tener retención"


def test_bucket_es_privado(outputs):
    bpa = get_client("s3").get_public_access_block(Bucket=outputs["bucket"])
    assert all(bpa["PublicAccessBlockConfiguration"].values())


def test_subir_json_genera_parquet(outputs):
    s3 = get_client("s3")
    bucket = outputs["bucket"]
    nombre = f"prueba-{int(time.time())}"
    s3.upload_file(
        str(RAIZ / "datos" / "muestra.json"), bucket, f"entrada/{nombre}.json"
    )

    clave_salida = f"salida/{nombre}.parquet"
    for _ in range(30):  # hasta ~60 s (arranque en frío de PyArrow)
        respuesta = s3.list_objects_v2(Bucket=bucket, Prefix=clave_salida)
        if respuesta.get("KeyCount"):
            break
        time.sleep(2)
    else:
        pytest.fail(
            f"No apareció {clave_salida}: revisar logs en {outputs['log_group_name']}"
        )

    s3.delete_objects(
        Bucket=bucket,
        Delete={"Objects": [{"Key": f"entrada/{nombre}.json"}, {"Key": clave_salida}]},
    )
