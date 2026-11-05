# ADR-0006 — Empaquetado de la Lambda: zip con archive_file y PyArrow desde una layer pública

- **Estado:** aceptada
- **Fecha:** 2026-11-05
- **Decide:** Ricardo Uculmana (ponente)
- **Detalla:** [ADR-0001](0001-pipeline-s3-lambda-parquet.md), punto 4

## Contexto

Convertir JSON a Parquet requiere PyArrow, que no está en el runtime de Lambda.
Empaquetarlo uno mismo es frágil con este público:

- un zip construido en Windows o macOS trae binarios incompatibles con Lambda
  (Linux);
- PyArrow pesa decenas de MB, y subirlo desde conexiones domésticas es lento;
- los participantes no tienen Python ni herramientas de build instalados.

## Decisión

1. **El código propio** (`infra/modules/lambda/src/handler.py`) se comprime con
   `data "archive_file"` en `infra/modules/lambda/build/handler.zip` durante el
   `plan`/`apply`. `build/` no se versiona.
2. **El zip se envía directo a la API de Lambda** (`filename` en
   `aws_lambda_function`). **No hay bucket de artefactos:** Lambda guarda la copia
   en su almacenamiento interno, fuera de la cuenta del participante.
3. **`source_code_hash`** con el hash del zip: si cambia `handler.py`, el
   siguiente `apply` actualiza la función; si no, no sube nada.
4. **PyArrow viene de la layer gestionada *AWS SDK for pandas*,** publicada por
   AWS: `arn:aws:lambda:us-east-1:336392948345:layer:AWSSDKPandas-Python312:32`
   (versión 3.18.0). El ARN está en la variable `layer_arn`.
5. **Runtime y arquitectura alineados con la layer:** `python3.12` y `x86_64`.
   Python 3.12 también está fijado en `.python-version` y `pyproject.toml` para
   probar el handler en local con la misma versión.
6. **Recursos de la función:** 512 MB de memoria y 60 s de timeout (los valores
   por defecto, 128 MB y 3 s, no alcanzan para el arranque en frío de PyArrow).
   En la prueba real usó 229 MB y tardó unos 8 s con 20 000 filas.

## Alternativas descartadas

- **Construir una layer propia** con `pip install --platform manylinux…`. Exige
  Python en la máquina del participante y una subida pesada.
- **Imagen de contenedor en Amazon ECR.** Exige Docker y un repositorio más;
  excesivo para una función de 40 líneas.
- **Subir el zip a un bucket S3** (`s3_bucket`/`s3_key`). Solo hace falta para
  paquetes de más de 50 MB; el nuestro pesa menos de 1 KB.
- **Transformación con la biblioteca estándar** (sin Parquet). Evitaría la layer,
  pero pierde la comparación JSON frente a Parquet, que es el puente a la sesión 2.

## Consecuencias

- **Cero pasos de build para el participante:** `terraform apply` hace todo.
- **Dependencia externa:** el ARN de la layer es regional y AWS publica versiones
  nuevas. Si se cambia de región o de versión de Python, hay que actualizar
  `layer_arn` (la tabla oficial está en la documentación de AWS SDK for pandas).
- **El handler se prueba en local** con un S3 falso (`tests/test_handler.py`),
  sin necesidad de AWS.
