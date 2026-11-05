# Convierte un JSON subido a entrada/ en Parquet dentro de salida/.
import io
import json
import os
from pathlib import PurePosixPath
from urllib.parse import unquote_plus

import boto3
import pyarrow as pa
import pyarrow.parquet as pq

s3 = boto3.client("s3")
PREFIJO_SALIDA = os.environ["PREFIJO_SALIDA"]


def handler(event, context):
    info = event["Records"][0]["s3"]
    bucket = info["bucket"]["name"]
    key = unquote_plus(info["object"]["key"])
    print(f"Evento recibido: {key}")

    tabla = leer_json(bucket, key)
    salida = escribir_parquet(tabla, bucket, key)
    print(f"Parquet escrito: {salida} ({tabla.num_rows} filas)")
    return {"parquet": salida, "filas": tabla.num_rows}


def leer_json(bucket, key):
    cuerpo = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
    datos = json.loads(cuerpo)
    filas = datos if isinstance(datos, list) else [datos]
    return pa.Table.from_pylist(filas)


def escribir_parquet(tabla, bucket, key):
    buffer = io.BytesIO()
    pq.write_table(tabla, buffer)
    nombre = PurePosixPath(key).stem + ".parquet"
    salida = PREFIJO_SALIDA + nombre
    s3.put_object(Bucket=bucket, Key=salida, Body=buffer.getvalue())
    return salida
