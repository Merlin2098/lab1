# ADR-0004 — Un solo bucket con carpetas, y un filtro que evita el bucle

- **Estado:** aceptada
- **Fecha:** 2026-11-05
- **Decide:** Ricardo Uculmana (ponente)
- **Detalla:** [ADR-0001](0001-pipeline-s3-lambda-parquet.md), puntos 1 y 2

## Contexto

El patrón habitual separa la zona de entrada (*landing*) y la procesada
(*processed*) en **dos buckets**. En el laboratorio eso significa dos nombres
globales que copiar, dos recursos que explicar y más comandos. La demo necesita
lo mínimo para ver cómo reacciona la Lambda.

El riesgo de un solo bucket es el **bucle recursivo**: si la Lambda escribe en el
mismo lugar que la dispara, cada Parquet nuevo vuelve a invocarla.

## Decisión

1. **Un bucket** `bootcamp-<sufijo>-datos` con dos carpetas (prefijos):
   `entrada/` y `salida/`. Terraform crea ambas como objetos vacíos para que se
   vean en la consola desde el principio.
2. **Notificación** `s3:ObjectCreated:*` hacia la Lambda, con **dos filtros**:
   prefijo `entrada/` **y** sufijo `.json`.
3. **La salida no cumple el filtro por dos motivos a la vez:** va a otra carpeta
   (`salida/`) y con otra extensión (`.parquet`).
4. **Validación en Terraform:** la variable `prefijo_salida` no puede ser igual a
   `prefijo_entrada` y debe terminar en `/`; si no, el `plan` falla con un
   mensaje que explica el riesgo de bucle.
5. **Bucket privado y cifrado:** Block Public Access completo y cifrado SSE-S3
   (`AES256`).
6. Prefijos, sufijo y nombres son **variables con valor por defecto**: se pueden
   cambiar sin tocar el código.

## Alternativas descartadas

- **Dos buckets (*landing* y *processed*).** Aislamiento más fuerte y sin riesgo
  de bucle, pero más fricción para la demo. Se menciona en clase como la práctica
  habitual en producción.
- **Solo filtro por sufijo.** Un `.json` subido a cualquier carpeta dispararía la
  Lambda; el prefijo hace explícito «solo lo que llega a `entrada/`».
- **Cifrado con KMS (SSE-KMS).** Añade una clave, permisos y costo; SSE-S3 basta
  para el laboratorio.

## Consecuencias

- **El mínimo privilegio se enseña por carpeta:** el rol lee solo `entrada/*` y
  escribe solo `salida/*` ([ADR-0005](0005-iam-minimo-privilegio.md)).
- **Un archivo con otra extensión o en otra carpeta no dispara nada.** Es el
  comportamiento esperado, pero confunde si no se explica (por ejemplo, subir el
  JSON a la raíz del bucket).
- **La protección contra el bucle depende de la configuración.** Cambiar a la
  vez prefijo y sufijo de salida para que coincidan con los de entrada
  reactivaría el bucle; la validación cubre el caso del prefijo.
