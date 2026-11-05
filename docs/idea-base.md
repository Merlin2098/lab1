# Idea base — Laboratorio 1: tu primer ETL en AWS

**Bootcamp AWS: de Cloud a Data Lakehouse · Sesión 1**
ESAN University (Ingeniería de Software) · Datahackers · Ponente: Ricardo Uculmana

Este documento resume **qué es el proyecto y por qué está hecho así**. El paso a
paso para ejecutarlo está en el [README](../README.md); las reglas para quien
modifique el repositorio, en [AGENTS.md](../AGENTS.md); y las decisiones de
arquitectura, con su porqué y las alternativas descartadas, en el
[índice de ADR](internal/adr/README.md).

---

## 1. La idea en una frase

Desplegar con Terraform un pipeline mínimo en el que **subir un JSON a S3 hace
que una Lambda lo convierta en Parquet sola**, y después destruirlo todo con un
comando.

## 2. Para quién es

Estudiantes universitarios y profesionales con programación básica, **sin
experiencia previa en AWS**. No se asume Python, SQL, terminal ni Git.

Por eso el participante **lee y ejecuta**: no escribe HCL ni Python. El
repositorio debe funcionar tal cual, sin editar nada salvo sus credenciales.

## 3. Qué debe aprender

| # | Al terminar, el participante puede… | Cómo se comprueba |
|---|---|---|
| R1 | Explicar qué es AWS (región, servicio, API) y el papel de S3, IAM, Lambda y CloudWatch en un pipeline de datos | Responde preguntas durante la lectura guiada del código |
| R2 | Crear un IAM user con access key y usarla desde la terminal de forma segura | `aws sts get-caller-identity` devuelve su usuario |
| R3 | Ejecutar el ciclo de Terraform: `init → plan → apply → destroy` | Crea el entorno y luego lo deja sin recursos |
| R4 | Ver cómo una Lambda reacciona a un evento de S3 y verificar su resultado | Aparece el Parquet en `salida/` y el log en CloudWatch |

La certificación **AWS DEA-C01** es la ruta de aprendizaje posterior, no el
objetivo de la sesión.

## 4. El caso: ventas ficticias

`datos/muestra.json` contiene 20 000 ventas ficticias de tiendas en Perú
(fecha, tienda, producto, cantidad, precio y total). Es lo bastante grande para
que se note la diferencia de formato: **unos 3,2 MB en JSON frente a ~190 KB en
Parquet**, con los mismos datos.

## 5. Arquitectura

Diagrama completo en Graphviz: [architecture/architecture.dot](architecture/architecture.dot).

```text
datos/muestra.json
   │  aws s3 cp
   ▼
S3 · bootcamp-<sufijo>-datos/entrada/
   │  evento ObjectCreated (solo entrada/*.json)
   ▼
Lambda · bootcamp-<sufijo>-etl  ──►  CloudWatch Logs · /aws/lambda/bootcamp-<sufijo>-etl
   │  JSON → Parquet (PyArrow, layer AWS SDK for pandas)
   ▼
S3 · bootcamp-<sufijo>-datos/salida/<nombre>.parquet
```

| Servicio | Papel | Módulo de Terraform |
|---|---|---|
| Amazon S3 | Un bucket privado y cifrado con dos carpetas: `entrada/` (JSON) y `salida/` (Parquet) | `infra/modules/s3` |
| AWS Lambda | Lee el JSON, lo convierte con PyArrow y escribe el Parquet. Se dispara solo con `.json` en `entrada/` | `infra/modules/lambda` |
| AWS IAM | Rol de mínimo privilegio: lee `entrada/*`, escribe `salida/*` y sus logs | `infra/modules/iam` |
| Amazon CloudWatch | Log group de la Lambda, con retención corta | `infra/modules/cloudwatch` |

**El código de la Lambda no pasa por S3.** Terraform lo comprime en la máquina
del participante (`archive_file`) y lo envía directo a la API de Lambda. PyArrow
lo aporta una *layer* pública de AWS.

## 6. Principios de diseño

1. **Fricción mínima.** Clonar, cargar credenciales y ejecutar. Todas las
   variables tienen valor por defecto; el nombre del bucket lleva un sufijo
   aleatorio para ser único sin configurar nada.
2. **Simple a propósito.** Un bucket, una función, una transformación. Lo que se
   enseña es el despliegue y el evento, no el ETL.
3. **Todo se destruye.** Bucket con `force_destroy`, sin versionado; log group
   gestionado por Terraform y sin protección contra borrado. `destroy` no deja
   nada.
4. **Seguro por defecto.** Bucket privado y cifrado, rol de mínimo privilegio,
   claves solo en `.env.credentials` (fuera de Git) y nunca en el código.
5. **Costo prácticamente cero.** Todo cabe en la capa gratuita y se destruye al
   terminar.
6. **Reproducible.** Versiones de Terraform y providers fijadas, código en Git y
   una prueba de punta a punta (`scripts/e2e.py`) que valida el pipeline.

## 7. Alcance

**Incluye:** cuenta y credenciales listas, Terraform de punta a punta, el
pipeline S3 → Lambda → S3 con logs, verificación y destrucción.

**No incluye (sesión 2):** catálogo de datos (Glue Data Catalog), consultas SQL
(Athena), particionado, orquestación de varias etapas y backend remoto de
Terraform.

## 8. Recorrido del participante

| Paso | Qué hace | Resultado |
|---|---|---|
| 1 | Carga su access key desde `.env.credentials` | `aws sts get-caller-identity` muestra su usuario |
| 2 | `terraform init` y `plan` | Ve los 12 recursos que se van a crear |
| 3 | `terraform apply` | Recibe los nombres de su bucket, Lambda y log group |
| 4 | Sube `datos/muestra.json` a `entrada/` | Aparece el Parquet en `salida/` y el log en CloudWatch |
| 5 | `terraform destroy` | No queda ningún recurso |

Si el evento no dispara la Lambda, el **plan B** es invocarla a mano con
`aws lambda invoke`.

## 9. Cómo sabemos que funciona

- `uv run pytest`: prueba local del handler, sin AWS.
- `scripts/e2e.py` contra el despliegue real: sube un JSON, espera el Parquet y
  valida que el JSON quede en `entrada/`, el Parquet en `salida/` con las mismas
  filas y columnas, y el log de esa ejecución en el log group de la Lambda.
  Termina en `PASA` o `FALLA`.

## 10. Puente a la sesión 2

Preguntas con las que cierra la sesión:

- ¿Qué cambiaría si llegaran miles de archivos?
- ¿Cómo catalogaríamos estos datos y los consultaríamos con SQL?
- ¿Cómo coordinaríamos varias etapas?
- ¿Cómo elegiríamos los servicios a partir de un requerimiento de negocio?
