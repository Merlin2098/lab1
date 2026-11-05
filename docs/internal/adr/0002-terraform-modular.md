# ADR-0002 — Terraform modular: un módulo por servicio de AWS

- **Estado:** aceptada
- **Fecha:** 2026-11-05
- **Decide:** Ricardo Uculmana (ponente)
- **Detalla:** [ADR-0001](0001-pipeline-s3-lambda-parquet.md), punto 6

## Contexto

El pipeline usa cuatro servicios: S3, IAM, Lambda y CloudWatch. Todo podría vivir
en un solo `main.tf`, pero el laboratorio quiere que el participante **vea el
mapa de servicios en el propio código**: qué hace cada servicio, qué recibe y qué
entrega a los demás.

## Decisión

Una sola raíz de Terraform en `infra/` que solo **conecta** módulos, y un
módulo por servicio:

| Módulo | Recursos | Recibe | Entrega |
|---|---|---|---|
| `modules/s3` | bucket, Block Public Access, cifrado, carpetas `entrada/` y `salida/` | nombre del bucket, carpetas | `bucket`, `resource_arn` |
| `modules/cloudwatch` | log group de la Lambda | nombre, días de retención | `log_group_name`, `log_group_arn`, `resource_arn` |
| `modules/iam` | rol de la Lambda y su política | ARN del bucket, carpetas, ARN del log group | `resource_arn` (el rol, entregado con su política ya aplicada) |
| `modules/lambda` | función, zip del código, permiso de invocación y notificación de S3 | rol, layer, log group, bucket, filtros | `function_name`, `resource_arn` |

Reglas:

1. **Cada módulo expone `resource_arn`**; el de CloudWatch además
   `log_group_name` y `log_group_arn`.
2. **La raíz no declara recursos de AWS.** Solo calcula nombres en `locals`
   (y el `random_string` del sufijo, ver [ADR-0007](0007-nombres-con-sufijo-aleatorio.md)) y
   pasa salidas de un módulo como entradas de otro.
3. **Regla de ubicación entre módulos.** Un recurso que necesita el ARN de otro
   módulo se declara donde ese ARN existe. Por eso el disparador
   (`aws_lambda_permission` + `aws_s3_bucket_notification`) vive en
   `modules/lambda/trigger.tf` y no en `modules/s3`: así `s3` no depende de
   `lambda` y no hay dependencias circulares.
4. **Sin versiones de módulos ni registro.** Los módulos son carpetas locales
   (`source = "./modules/<servicio>"`); no se publican.

## Alternativas descartadas

- **Todo en el módulo raíz.** Menos archivos, pero los servicios se mezclan y
  el participante pierde el mapa de «un servicio, una carpeta».
- **Una raíz de Terraform por servicio, cada una con su state.** Obligaría a
  hacer `apply` en un orden y a pasar ARNs entre states: demasiada fricción para
  principiantes.
- **Módulos públicos del registro** (por ejemplo `terraform-aws-modules/s3-bucket`).
  Ocultan los recursos reales detrás de decenas de variables: lo contrario de lo
  que se quiere enseñar.

## Consecuencias

- **Un solo `init`/`plan`/`apply`/`destroy`** para todo el laboratorio.
- **Más archivos** (`variables.tf` y `outputs.tf` por módulo) y un salto de
  indirección al leer: hay que seguir el valor desde `main.tf` hasta el módulo.
- **El grafo de dependencias se deduce de las referencias**
  (`module.s3.resource_arn` → `module.iam`): sirve para explicar que Terraform
  ordena el despliegue por referencias, no por el orden de los archivos.
- **Base para crecer:** en la sesión 2 se pueden añadir módulos (Glue, Athena)
  sin tocar los existentes.
