# Decisiones de arquitectura (ADR)

Cada archivo registra una decisión: su contexto, qué se decidió, qué
alternativas se descartaron y qué consecuencias tiene. Una decisión nueva que
cambie la arquitectura se registra aquí **antes** de implementarla
(ver [AGENTS.md](../../../AGENTS.md)).

| ADR | Decisión | Recursos |
|---|---|---|
| [0001](0001-pipeline-s3-lambda-parquet.md) | Pipeline S3 → Lambda → Parquet: visión general | Todos |
| [0002](0002-terraform-modular.md) | Terraform modular: un módulo por servicio | `infra/` |
| [0003](0003-destroy-completo.md) | Todo se destruye: `force_destroy`, sin versionado, sin protecciones | S3, CloudWatch, IAM |
| [0004](0004-un-bucket-con-carpetas.md) | Un solo bucket con carpetas y filtro anti-bucle | S3 |
| [0005](0005-iam-minimo-privilegio.md) | Rol de mínimo privilegio para la Lambda | IAM, Lambda |
| [0006](0006-empaquetado-lambda-y-layer.md) | Zip con `archive_file` y PyArrow desde una layer pública | Lambda |
| [0007](0007-nombres-con-sufijo-aleatorio.md) | Nombres con sufijo aleatorio y valores por defecto | Todos |
| [0008](0008-log-group-gestionado.md) | Log group gestionado por Terraform | CloudWatch |
| [0009](0009-credenciales-access-key.md) | Credenciales por access key en `.env.credentials` | IAM user |

Formato: título, estado, fecha, contexto, decisión, alternativas descartadas y
consecuencias.
