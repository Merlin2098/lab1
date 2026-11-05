"""Prueba de punta a punta (e2e) del pipeline desplegado, con boto3.

Sube datos/muestra.json a entrada/, espera el Parquet en salida/ y, si no
aparece, diagnostica por qué (estado de la Lambda, disparador, métricas e
invocación directa con su log). Al final borra lo que subió.

Requisitos: `terraform -chdir=infra apply` hecho y credenciales cargadas
(set -a; source .env.credentials; set +a).

Uso (desde la raíz del repo):
  bash scripts/con_credenciales.sh uv run python scripts/e2e.py [--archivo datos/x.json] [--conservar]
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import boto3
import pyarrow.parquet as pq
from botocore.exceptions import BotoCoreError, ClientError

RAIZ = Path(__file__).resolve().parents[1]
MUESTRA = RAIZ / "datos" / "muestra.json"  # se ajusta en main() con --archivo


def muestra_por_defecto() -> Path:
    """datos/muestra.json si existe; si no, la muestra con fecha más reciente."""
    if MUESTRA.is_file():
        return MUESTRA
    candidatas = sorted((RAIZ / "datos").glob("muestra_*.json"))
    return candidatas[-1] if candidatas else MUESTRA


ESPERA_S = 90


def paso(texto: str) -> None:
    print(f"\n== {texto}")


def ok(texto: str) -> None:
    print(f"   [OK] {texto}")


def falla(texto: str) -> None:
    print(f"   [FALLA] {texto}")


def outputs_terraform() -> dict:
    r = subprocess.run(
        ["terraform", f"-chdir={RAIZ / 'infra'}", "output", "-json"],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0 or not r.stdout.strip() or r.stdout.strip() == "{}":
        sys.exit(
            "No hay outputs de Terraform: ejecuta primero terraform -chdir=infra apply"
        )
    return {k: v["value"] for k, v in json.loads(r.stdout).items()}


def validar_destinos(
    sesion,
    bucket: str,
    nombre: str,
    clave_entrada: str,
    clave_salida: str,
    parquet: bytes,
    log_group: str,
    desde_ms: int,
) -> bool:
    """Comprueba que cada cosa llegó a su recurso y nada a otro lado."""
    paso("6 · Validar que todo llegó a su recurso")
    correcto = True

    # S3: exactamente el JSON en entrada/ y el Parquet en salida/.
    s3 = sesion.client("s3")
    claves = {
        o["Key"]
        for o in s3.list_objects_v2(Bucket=bucket).get("Contents", [])
        if nombre in o["Key"]
    }
    if claves == {clave_entrada, clave_salida}:
        ok(
            f"S3: JSON en {clave_entrada.split('/')[0]}/ y Parquet en {clave_salida.split('/')[0]}/"
        )
    else:
        falla(
            f"S3: se esperaban {[clave_entrada, clave_salida]} y hay {sorted(claves)}"
        )
        correcto = False

    # Parquet: mismas filas y columnas que el JSON de entrada.
    origen = json.loads(MUESTRA.read_text(encoding="utf-8"))
    tabla = pq.read_table(io.BytesIO(parquet))
    if tabla.num_rows == len(origen) and set(tabla.column_names) == set(origen[0]):
        ok(
            f"Parquet: {tabla.num_rows} filas y {tabla.num_columns} columnas, igual que el JSON"
        )
    else:
        falla(
            f"Parquet: {tabla.num_rows} filas / {tabla.column_names}; "
            f"JSON: {len(origen)} filas / {list(origen[0])}"
        )
        correcto = False

    # CloudWatch: el log de ESTA ejecución está en el log group de la Lambda.
    logs = sesion.client("logs")
    esperadas = [
        f"Evento recibido: {clave_entrada}",
        f"Parquet escrito: {clave_salida}",
    ]
    mensajes: list[str] = []
    for _ in range(10):  # los logs tardan unos segundos en llegar
        eventos = logs.filter_log_events(
            logGroupName=log_group, startTime=desde_ms, filterPattern=f'"{nombre}"'
        )["events"]
        mensajes = [e["message"] for e in eventos]
        if all(any(linea in m for m in mensajes) for linea in esperadas):
            break
        time.sleep(3)
    faltan = [linea for linea in esperadas if not any(linea in m for m in mensajes)]
    if not faltan:
        ok(f"CloudWatch: «Evento recibido» y «Parquet escrito» en {log_group}")
    else:
        falla(f"CloudWatch: faltan en {log_group}: {faltan}")
        correcto = False

    return correcto


def diagnosticar(sesion, bucket: str, funcion: str, clave: str) -> None:
    """Se ejecuta solo si el Parquet no apareció."""
    lam = sesion.client("lambda")

    paso("Diagnóstico 1 · Métricas de la última hora")
    cw = sesion.client("cloudwatch")
    ahora = datetime.now(timezone.utc)
    for metrica in ("Invocations", "Errors"):
        datos = cw.get_metric_statistics(
            Namespace="AWS/Lambda",
            MetricName=metrica,
            Dimensions=[{"Name": "FunctionName", "Value": funcion}],
            StartTime=ahora - timedelta(hours=1),
            EndTime=ahora,
            Period=3600,
            Statistics=["Sum"],
        )["Datapoints"]
        print(f"   {metrica}: {int(sum(d['Sum'] for d in datos))}")
    print(
        "   (Invocations = 0 -> S3 no llamó a la Lambda; Errors > 0 -> la llamó y falló)"
    )

    paso("Diagnóstico 2 · Invocación directa con el mismo archivo")
    evento = {
        "Records": [{"s3": {"bucket": {"name": bucket}, "object": {"key": clave}}}]
    }
    r = lam.invoke(
        FunctionName=funcion,
        Payload=json.dumps(evento).encode(),
        LogType="Tail",
    )
    log = base64.b64decode(r.get("LogResult", "")).decode(errors="replace")
    respuesta = r["Payload"].read().decode(errors="replace")
    if r.get("FunctionError"):
        falla(f"La Lambda falla al ejecutarse ({r['FunctionError']}):")
    else:
        ok("Invocada a mano funciona -> el problema está en el disparo de S3")
    print("   --- respuesta ---\n   " + respuesta)
    print("   --- log (últimos 4 KB) ---\n" + log)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # tildes correctas en Git Bash (Windows)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--conservar", action="store_true", help="no borrar los objetos de prueba"
    )
    parser.add_argument(
        "--archivo",
        type=Path,
        help="JSON a subir (por defecto, la muestra más reciente de datos/)",
    )
    args = parser.parse_args()

    global MUESTRA
    MUESTRA = args.archivo or muestra_por_defecto()
    if not MUESTRA.is_file():
        print(f"No existe {MUESTRA}: genera una con scripts/generar_muestra.py")
        return 1
    print(
        f"Archivo de prueba: {MUESTRA.relative_to(RAIZ) if MUESTRA.is_relative_to(RAIZ) else MUESTRA}"
    )

    out = outputs_terraform()
    bucket, funcion = out["bucket"], out["lambda_name"]
    sesion = boto3.Session(
        region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
    )

    paso("1 · Credenciales")
    try:
        arn = sesion.client("sts").get_caller_identity()["Arn"]
    except (ClientError, BotoCoreError) as error:
        falla(f"No hay credenciales válidas: {error}")
        print("   Carga tus claves: set -a; source .env.credentials; set +a")
        return 1
    ok(f"Usuario: {arn.split(':')[-1]}")

    paso("2 · Estado de la Lambda")
    cfg = sesion.client("lambda").get_function_configuration(FunctionName=funcion)
    print(
        f"   Estado: {cfg['State']} · Última actualización: {cfg['LastUpdateStatus']}"
    )
    print(
        f"   Layers: {[layer['Arn'].split(':')[-2:] for layer in cfg.get('Layers', [])]}"
    )
    print(f"   Log group: {cfg.get('LoggingConfig', {}).get('LogGroup')}")
    if cfg["State"] != "Active":
        falla(f"La función no está activa: {cfg.get('StateReason')}")
        return 1
    ok("Activa")

    paso("3 · Disparador de S3")
    s3 = sesion.client("s3")
    reglas = s3.get_bucket_notification_configuration(Bucket=bucket).get(
        "LambdaFunctionConfigurations", []
    )
    if not reglas:
        falla("El bucket no tiene notificación hacia la Lambda")
        return 1
    filtros = {
        r["Name"].lower(): r["Value"] for r in reglas[0]["Filter"]["Key"]["FilterRules"]
    }
    ok(
        f"ObjectCreated -> {funcion} · prefijo={filtros.get('prefix')} sufijo={filtros.get('suffix')}"
    )

    paso("4 · Subir la muestra a entrada/")
    nombre = f"e2e-{int(time.time())}"
    clave_entrada = f"{filtros.get('prefix', 'entrada/')}{nombre}.json"
    clave_salida = f"salida/{nombre}.parquet"
    s3.upload_file(str(MUESTRA), bucket, clave_entrada)
    ok(f"s3://{bucket}/{clave_entrada} ({MUESTRA.stat().st_size / 1024:.0f} KB)")

    paso(f"5 · Esperar el Parquet (hasta {ESPERA_S} s)")
    inicio = time.time()
    parquet = None
    while time.time() - inicio < ESPERA_S:
        try:
            parquet = s3.get_object(Bucket=bucket, Key=clave_salida)["Body"].read()
            break
        except ClientError:
            time.sleep(3)

    exito = parquet is not None
    if exito:
        ok(f"s3://{bucket}/{clave_salida} en {time.time() - inicio:.0f} s")
        print(
            f"   JSON {MUESTRA.stat().st_size / 1024:.0f} KB -> Parquet {len(parquet) / 1024:.0f} KB"
        )
        exito = validar_destinos(
            sesion,
            bucket,
            nombre,
            clave_entrada,
            clave_salida,
            parquet,
            cfg.get("LoggingConfig", {}).get("LogGroup") or out["log_group_name"],
            int(inicio * 1000),
        )
    else:
        falla(f"No apareció {clave_salida}")
        diagnosticar(sesion, bucket, funcion, clave_entrada)

    if not args.conservar:
        paso("7 · Limpieza")
        s3.delete_objects(
            Bucket=bucket,
            Delete={"Objects": [{"Key": clave_entrada}, {"Key": clave_salida}]},
        )
        ok("Objetos de prueba borrados")

    print("\nRESULTADO:", "PASA" if exito else "FALLA")
    return 0 if exito else 1


if __name__ == "__main__":
    sys.exit(main())
