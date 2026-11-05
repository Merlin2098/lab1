# AGENTS.md — Bootcamp AWS · Sesión 1 · Laboratorio 1

Contrato de trabajo para agentes de IA en este repositorio. Aplica igual a
Claude Code (ver [CLAUDE.md](CLAUDE.md)) y a cualquier otro agente.

---

## Propósito

Laboratorio de la sesión 1 del *Bootcamp AWS: de Cloud a Data Lakehouse*
(ESAN y Datahackers): **«De cero a tu primer ETL en AWS»**. Con Terraform se
despliega un pipeline que reacciona a eventos:

```text
datos/muestra.json --(AWS CLI)--> s3://<bucket>/entrada/ --(ObjectCreated: entrada/*.json)-->
Lambda (JSON → Parquet) --> s3://<bucket>/salida/      (+ logs en CloudWatch)
```

El ETL es deliberadamente simple: **un solo bucket con dos carpetas** y una
Lambda que reacciona al evento `ObjectCreated`. Lo que se enseña es **cómo se
despliega con Terraform** y **cómo una Lambda reacciona a un evento**. Las
decisiones están en [ADR-0001](docs/internal/adr/0001-pipeline-s3-lambda-parquet.md).

El repositorio tiene dos públicos:

| Público | Qué hace | Qué tiene instalado |
|---|---|---|
| Participantes (sin experiencia en AWS) | **Leen y ejecutan**: no escriben HCL ni Python | Terraform, AWS CLI, editor y Git Bash |
| Ponente y co-facilitador | Preparan, prueban y presentan | Lo anterior, más `uv` y Python 3.12 |

Nada del recorrido del participante puede requerir Python, `uv` ni Git.

**Fricción mínima (obligatorio):** el repositorio es genérico; cualquiera lo
clona y lo replica sin editar nada salvo `.env.credentials`. Toda variable de
Terraform tiene un valor por defecto que funciona; `terraform.tfvars` es
opcional. Antes de añadir un paso manual, buscar cómo evitarlo.

---

## Fuentes de verdad

| Documento | Manda en |
|---|---|
| [docs/idea-base.md](docs/idea-base.md) | La idea del proyecto: público, objetivos de aprendizaje, arquitectura, principios y alcance |
| [docs/internal/adr/](docs/internal/adr/) | Las decisiones de arquitectura y su porqué |
| [README.md](README.md) | El recorrido del participante, paso a paso |
| Este repositorio | El código. Si un documento contradice el código, se corrige el documento |

Al cambiar un nombre, una ruta o un valor del contrato de nombres, hay que
actualizar en el mismo cambio el README y `docs/idea-base.md`.

### Contrato de nombres

| Elemento | Valor |
|---|---|
| Región | `us-east-1` (variable `region`) |
| Variables de Terraform | Todas con valor por defecto: `sufijo` (opcional; si falta, `random_string` de 6 caracteres), `region`, `prefijo_entrada`, `sufijo_entrada`, `prefijo_salida`, `layer_arn` |
| Bucket | `bootcamp-<sufijo>-datos`, con las carpetas `entrada/` y `salida/` |
| Recursos | `aws_s3_bucket.datos`, `aws_iam_role.lambda`, `aws_lambda_function.fn`, `aws_lambda_permission.s3`, `aws_s3_bucket_notification.n`, `aws_cloudwatch_log_group.lambda` |
| Filtro del evento | prefijo `entrada/`, sufijo `.json`. La salida va a `salida/<nombre>.parquet` |
| Outputs | `bucket`, `lambda_name`, `log_group_name`, `log_group_arn`, `resource_arn`, `comando_subida` |
| Función Lambda, rol y log group | `bootcamp-<sufijo>-etl`, `bootcamp-<sufijo>-etl-rol` y `/aws/lambda/bootcamp-<sufijo>-etl`: todo lleva el sufijo del despliegue. El log group lo gestiona Terraform con `skip_destroy = false` y `deletion_protection_enabled = false` (no existe `force_destroy` para log groups). En el README, los comandos usan `$BUCKET`, `$LAMBDA` y `$LOG_GROUP` tomados de `terraform output` |
| Archivos | `datos/muestra.json` (versionada; las muestras `datos/muestra_*.json` se ignoran), `infra/modules/lambda/src/handler.py`, `infra/modules/iam/main.tf`, `infra/modules/lambda/trigger.tf` |

---

## Estructura

```text
lab1/
├── README.md                 # Guía del participante (pasos 1–5 y plan B)
├── .env.credentials.example  # Plantilla de credenciales (la copia real no se versiona)
├── infra/                    # UNA raíz de Terraform
│   ├── providers.tf variables.tf main.tf outputs.tf terraform.tfvars.example
│   ├── backend.tf.example    # Solo referencia: backend remoto en S3 (sesión 2)
│   └── modules/              # Un módulo por servicio
│       ├── s3/               # bucket, Block Public Access, cifrado, carpetas
│       ├── cloudwatch/       # log group con retención
│       ├── iam/              # rol y política de mínimo privilegio
│       └── lambda/           # main.tf (función + zip), trigger.tf, src/handler.py
├── datos/                    # muestra.json (20 000 filas, la que usan los participantes)
├── scripts/                  # generar_muestra.py, con_credenciales.sh, e2e.py (ponente)
├── tests/                    # test_handler.py (local) y aws/ (pruebas cloud)
└── docs/                     # idea-base.md, architecture/architecture.dot e internal/adr/
```

- **Un módulo por servicio.** Cada uno expone `resource_arn`; el de CloudWatch
  expone además `log_group_name` y `log_group_arn`. La raíz (`main.tf`) solo los
  conecta.
- **El disparador vive en `modules/lambda/trigger.tf`**, que es donde se conoce el
  ARN de la función. Regla general: un recurso que necesita un ARN de otro módulo
  se declara en el módulo donde ese ARN existe, y se pasa lo demás por variables.
  Así no hay dependencias circulares.
- **Una sola raíz para toda la sesión:** la explicación de Terraform (`init` y
  `plan`) y el laboratorio (`apply` y `destroy`) usan este mismo código.

---

## Shell y comandos

- **Git Bash** es el shell del proyecto (Claude Code: `defaultShell: bash`; VS Code:
  perfil por defecto `Git Bash` en `.vscode/settings.json`).
- Los comandos de la documentación usan sintaxis bash con `\` para continuar línea.
  Los participantes también usan Git Bash (o la terminal de macOS/Linux): no hay
  variante de PowerShell.
- Todos los comandos del participante se ejecutan **desde la raíz del repo**
  (ahí están `.env.credentials` y `datos/`); Terraform con `-chdir=infra`.
- En Git Bash, los argumentos que empiezan por `/` se convierten en rutas de
  Windows. Para `aws logs tail /aws/lambda/...` y `--log-group-name-prefix`, usar
  `MSYS_NO_PATHCONV=1 aws logs ...`. No exportarlo de forma global: rompe otras
  rutas.
- Terraform se ejecuta de forma explícita desde `infra/` (`cd infra && terraform
  plan`) o con `terraform -chdir=infra`.
- **Antivirus con inspección HTTPS (AVG, Avast…)** rompe el canal TLS local entre
  Terraform y sus providers («x509: certificate signed by unknown authority» al
  cargar esquemas). Hay que excluir `terraform.exe` y la carpeta `.terraform/` del
  escaneo HTTPS, o desactivar esa función mientras dura el laboratorio.
- Herramientas del ponente: `uv sync`, `uv run pytest`, `uv run ruff check`.
  Sin wrappers ni automatización oculta.
- **Python 3.12 obligatorio**, igual que el runtime `python3.12` de la Lambda.
  Está fijado en `.python-version` y en `requires-python = "==3.12.*"` de
  `pyproject.toml`. Si se cambia, hay que cambiar a la vez esos dos archivos y el
  runtime de la Lambda (guarda de abajo), o no cambiar ninguno. No usar
  el Python del sistema si es otra versión: con 3.15, por ejemplo, `uv sync`
  intenta compilar `pyarrow==23.0.1` (no hay wheel) y falla por falta de cmake.
  Si `uv sync` falla así, revisar `.venv/pyvenv.cfg` y ejecutar
  `uv sync --python 3.12`.

---

## Credenciales

- El participante se autentica con la **access key y la secret access key** de su
  IAM user, guardadas en `.env.credentials` (copiado de
  `.env.credentials.example`; está en `.gitignore`) y cargadas en la terminal con:

  ```bash
  set -a
  source .env.credentials
  set +a
  ```

  Terraform, AWS CLI y boto3 las toman del entorno (cadena de credenciales por
  defecto). No se usan perfiles nombrados. Las variables solo existen en esa
  terminal.
- El provider de AWS **nunca** lleva `access_key`/`secret_key`, y no se añaden
  variables de Terraform para ellas.
- Las claves solo viven en `.env.credentials`: nunca en el código, `*.tfvars`,
  el chat ni las capturas. Los agentes no leen `.env`, `.env.credentials` ni
  `~/.aws/`; la plantilla `.env.credentials.example` sí se puede editar (solo
  marcadores).
- En el material, las cuentas y los ARNs se escriben con marcadores (`<sufijo>`,
  `<bucket>`, `<tu access key id>`); nunca IDs de cuenta reales.
- El IAM user del participante tiene `AdministratorAccess` **solo** porque es un
  laboratorio personal. El rol de la Lambda sí aplica mínimo privilegio.

---

## Límites de aprobación

### Nunca sin aprobación explícita

- `terraform apply`, `terraform destroy`, `terraform import` y `terraform state rm`
- Cualquier cambio en recursos reales de AWS
- Sobrescribir datos o artefactos que pertenecen al usuario

### Preguntar antes

- Cambios en IAM (rol y política de la Lambda)
- Servicios de AWS de pago o fuera del free tier
- Cambios en el contrato de nombres (tabla de arriba) o en el formato de los datos
- Borrar log groups de CloudWatch o reducir su retención

---

## Guardas de AWS y Terraform

El agente DEBE:

- fijar `required_version` y las versiones de los providers, y versionar
  `.terraform.lock.hcl`;
- usar la **región única** `us-east-1`, definida por variable;
- aplicar los tags comunes (incluido `CostCenter`) mediante `default_tags` del
  provider;
- declarar `aws_cloudwatch_log_group` de la Lambda con `retention_in_days` corto;
  si no se declara, queda huérfano tras `destroy`;
- crear el bucket **sin versionado**, con `force_destroy = true`, *Block Public
  Access*, cifrado SSE-S3 y un sufijo único (`var.sufijo`), porque los nombres
  son globales;
- mantener un **solo bucket** con las carpetas `entrada/` y `salida/`. El filtro
  de prefijo y sufijo, más una salida con otra carpeta y otra extensión, evita
  que la Lambda se dispare con su propia salida;
- limitar el rol de la Lambda por prefijo: `GetObject` en `entrada/*`,
  `PutObject` en `salida/*` y logs solo en su log group;
- declarar `aws_lambda_permission` y `aws_s3_bucket_notification` con
  `depends_on` del permiso;
- empaquetar el handler con `data "archive_file"` (el participante no ejecuta
  ningún paso de build) y tomar PyArrow de la layer gestionada *AWS SDK for
  pandas*, con su ARN en una variable;
- usar runtime `python3.12` y x86_64, con timeout y memoria validados en la
  prueba previa (orientativo: 30–60 s y 512 MB);
- exponer los outputs del contrato y además `log_group_name`, `log_group_arn` y
  `resource_arn`;
- mantener la prueba local del handler (`tests/test_handler.py`, sin AWS) y las
  pruebas boto3 de lo desplegado en `tests/aws/` (marcador `cloud`).

El agente NO DEBE:

- crear presupuestos ni alertas de coste (`aws_budgets_budget`): el laboratorio
  cabe en la capa gratuita y se destruye al terminar;
- activar el versionado de S3 ni ninguna protección que impida el `destroy`;
- asumir permisos IAM implícitos: todo permiso se declara en Terraform;
- borrar ni sobrescribir `terraform.tfstate`;
- crear recursos sin tags ni log groups sin `retention_in_days`.

Para la sintaxis de recursos, las versiones vigentes, los límites o el ARN de la
layer, consultar en vivo los servidores MCP de documentación de AWS y de
Terraform. No confiar en la memoria ni mantener copias locales de esa
documentación.

---

## Gobernanza

- **Spec antes del código (recomendado):** para cambios significativos, partir de
  una spec; para arreglos pequeños es opcional.
- **ADR antes de cambiar la arquitectura (obligatorio):** añadir un servicio,
  sustituir una tecnología o cambiar el contrato de nombres o de datos se
  registra antes en `docs/internal/adr/` (título, estado, contexto, decisión y
  consecuencias).
- **Configuración en lugar de valores fijos (obligatorio):** la región, el
  sufijo, el ARN de la layer y los prefijos y sufijos del filtro van en
  variables, nunca fijos en el código.
- **Seguridad por defecto (obligatorio):** todo recurso nace privado y con
  mínimo privilegio.
- **No enviar archivos sensibles a servicios externos (obligatorio):** `.env*`,
  claves (`.pem`, `.key`…), CSV de access keys y el contenido de `~/.aws`,
  `~/.ssh` y similares.
- **La solución más simple que funcione (recomendado):** ¿hace falta?, ¿lo
  resuelve la biblioteca estándar o una función nativa de la plataforma?, ¿una
  dependencia ya instalada?, ¿cabe en una línea? Solo entonces, el código mínimo.
  Para el público, menos archivos y menos pasos es mejor.

---

## Estilo del material

- Español en la documentación, los comentarios y los mensajes que ve el
  participante. Los identificadores siguen el contrato de nombres.
- El código que se lee en clase (`handler.py`, `modules/iam/main.tf`,
  `trigger.tf`, `providers.tf`, `modules/s3/main.tf`) debe leerse casi como
  pseudocódigo: líneas cortas y un handler breve, con comentarios en español.
- Todo comando para el participante debe poder copiarse y pegarse tal cual.

---

## Filosofía

Simple. Explícito. Reproducible. La IA es una ayuda para este laboratorio, no el
sistema en sí.
