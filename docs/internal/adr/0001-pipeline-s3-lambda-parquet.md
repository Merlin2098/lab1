# ADR-0001 — Pipeline S3 → Lambda → Parquet en un solo bucket, con un módulo de Terraform por servicio

- **Estado:** aceptada
- **Fecha:** 2026-11-05
- **Decide:** Ricardo Uculmana (ponente)
- **Detallada en:** [ADR-0002 a ADR-0009](README.md) (una decisión por tema)

## Contexto

La sesión 1 necesita un ETL mínimo para mostrar dos ideas: cómo se despliega
infraestructura con Terraform y cómo una Lambda reacciona a un evento de S3. El
público no tiene experiencia en AWS y solo lee y ejecuta (no escribe HCL).

El borrador inicial de la sesión proponía dos buckets (*landing* y *processed*),
entrada NDJSON y todo el código en el módulo raíz. La idea vigente del proyecto
está en [docs/idea-base.md](../../idea-base.md).

## Decisión

1. **Un solo bucket** `<proyecto>-<sufijo>-datos`, con dos carpetas (prefijos):
   - `entrada/`: el participante sube archivos `.json`.
   - `salida/`: la Lambda escribe el `.parquet`.
2. **Disparo:** `s3:ObjectCreated:*` con filtro de prefijo `entrada/` y sufijo
   `.json`. La salida va a otro prefijo y con otra extensión, así que la Lambda no
   se vuelve a disparar con su propio resultado.
3. **Formato de entrada:** JSON estándar (un objeto o un arreglo de objetos). La
   Lambda lo convierte a Parquet con PyArrow (`Table.from_pylist`).
4. **PyArrow** viene de la layer gestionada *AWS SDK for pandas*:
   `arn:aws:lambda:us-east-1:336392948345:layer:AWSSDKPandas-Python312:32`
   (versión 3.18.0, Python 3.12, x86_64). El ARN está en una variable.
   **Empaquetado del código:** `data "archive_file"` genera
   `modules/lambda/build/handler.zip` en la máquina que ejecuta Terraform, y
   `aws_lambda_function` (`filename` + `source_code_hash`) lo envía directo a la
   API de Lambda, que guarda la copia en su almacenamiento interno. No hay un
   bucket de artefactos. Límite: 50 MB por subida directa; por encima, usar
   `s3_bucket`/`s3_key` o una imagen de contenedor en ECR.
5. **Región única:** `us-east-1`.
6. **Terraform:** una sola raíz en `infra/`, con **un módulo por servicio**:
   `modules/s3`, `modules/iam`, `modules/cloudwatch` y `modules/lambda`. El
   disparador (`aws_lambda_permission` + `aws_s3_bucket_notification`) vive en
   `modules/lambda/trigger.tf`, donde se conoce el ARN de la función; así se evita
   que `s3` dependa de `lambda` (regla de ubicación entre módulos de AGENTS.md).
7. **Bucket sin versionado y con `force_destroy = true`**, Block Public Access y
   cifrado SSE-S3. Los tags comunes van en `default_tags` del provider.
8. **Una sola raíz para toda la sesión:** la explicación de Terraform (`init` y
   `plan`) usa el mismo código que el laboratorio (`apply` y `destroy`). No hay
   una raíz aparte para una demo del bucket.

## Consecuencias

- **Más simple para la demo:** un bucket, un nombre que copiar y las dos carpetas
  visibles en la consola.
- **El mínimo privilegio se enseña por prefijo:** la Lambda solo puede
  `GetObject` en `entrada/*` y `PutObject` en `salida/*`. La pregunta 2 de la
  lectura guiada («¿por qué dos buckets?») cambia a «¿por qué dos carpetas y un
  filtro?».
- **Riesgo de bucle:** si alguien cambia el prefijo de salida a `entrada/` o la
  extensión de salida a `.json`, la Lambda se invocaría a sí misma. Las variables
  lo validan y el riesgo se menciona en la lectura guiada.
- **Los módulos añaden indirección** (variables y outputs por módulo). A cambio,
  cada servicio queda en su carpeta, que es justo el mapa que se explica en
  clase.
- **No hay un `apply`/`destroy` de un recurso suelto** antes del laboratorio: el
  ciclo completo de Terraform (objetivo R3 de la idea base) se practica con el
  pipeline.
