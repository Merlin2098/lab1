# ADR-0003 — Todo se destruye: force_destroy, sin versionado y sin protecciones

- **Estado:** aceptada
- **Fecha:** 2026-11-05
- **Decide:** Ricardo Uculmana (ponente)
- **Detalla:** [ADR-0001](0001-pipeline-s3-lambda-parquet.md), punto 7

## Contexto

Cada participante despliega en **su propia cuenta** y debe terminar el
laboratorio con un solo comando, `terraform destroy`, sin pasos manuales ni
recursos huérfanos que generen costo. Un `destroy` que falla a mitad de la sesión
deja al participante sin saber qué borrar a mano.

Bloqueos típicos de `destroy` en AWS:

- un bucket con objetos (`BucketNotEmpty`);
- un bucket con versionado: borrar los objetos deja versiones y marcadores de
  borrado;
- un log group creado por la propia Lambda, que Terraform no conoce;
- un rol IAM con políticas adjuntadas a mano desde la consola (`DeleteConflict`);
- argumentos que evitan el borrado (`prevent_destroy`, `skip_destroy`,
  protección contra borrado).

## Decisión

| Recurso | Configuración | Efecto en `destroy` |
|---|---|---|
| `aws_s3_bucket.datos` | `force_destroy = true` | Vacía el bucket (entradas y Parquet) y lo borra |
| Versionado de S3 | **No se declara** `aws_s3_bucket_versioning` | No quedan versiones ni marcadores de borrado |
| `aws_cloudwatch_log_group.lambda` | `skip_destroy = false`, `deletion_protection_enabled = false` | Se borra con todos sus logs (los log groups no tienen `force_destroy`: borrar el grupo borra su contenido) |
| `aws_iam_role.lambda` | `force_detach_policies = true` | Quita las políticas adjuntadas a mano antes de borrar el rol |
| Todo el código | Ningún `lifecycle { prevent_destroy }` | Nada puede vetar el `destroy` |
| State | Backend local (`backend.tf.example` es solo una referencia) | No hay bucket de state que proteger |

Complementos que evitan huérfanos:

- **El log group lo crea Terraform** y el rol de la Lambda **no** tiene
  `logs:CreateLogGroup`: la Lambda no puede crear otro log group fuera del
  control de Terraform (ver [ADR-0008](0008-log-group-gestionado.md)).
- **Todos los nombres llevan el sufijo del despliegue**
  ([ADR-0007](0007-nombres-con-sufijo-aleatorio.md)): un resto de un intento
  anterior no choca con un despliegue nuevo.

## Alternativas descartadas

- **Versionado activado** (buena práctica en producción). Rompe el «borra todo
  con un comando» y no aporta nada a un laboratorio efímero.
- **Limpieza manual** (vaciar el bucket con `aws s3 rm --recursive` antes del
  `destroy`). Es un paso más que los participantes olvidan o ejecutan sobre el
  bucket equivocado.

## Consecuencias

- **`terraform destroy` deja la cuenta sin recursos del laboratorio.** El README
  incluye la comprobación (`state list` vacío, sin buckets `bootcamp-…`, sin log
  groups `/aws/lambda/bootcamp-…`).
- **Riesgo aceptado:** `force_destroy` borra datos sin preguntar. Es correcto
  aquí porque los datos son de prueba y se regeneran; **no es una configuración
  para producción**, y así se explica en clase.
- **Caso límite:** si una ejecución de la Lambda escribe un Parquet justo
  mientras corre el `destroy`, el borrado del bucket puede fallar con
  `BucketNotEmpty`. Se resuelve volviendo a ejecutar `terraform destroy`.
- **Lo que no se borra:** el IAM user y su access key del participante. No los
  gestiona este Terraform y se usan en la sesión 2.
