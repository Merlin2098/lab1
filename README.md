# Laboratorio 1 — Tu primer ETL en AWS

**Bootcamp AWS: de Cloud a Data Lakehouse · Sesión 1**
ESAN University · Datahackers

Vas a desplegar con Terraform un pipeline que reacciona a eventos. Subes un
archivo JSON a S3 y una función Lambda lo convierte en Parquet **sola**, sin
que nadie la invoque.

```text
datos/muestra.json
   │  aws s3 cp
   ▼
S3 · bootcamp-<sufijo>-datos/entrada/
   │  evento ObjectCreated (solo entrada/*.json)
   ▼
Lambda · bootcamp-<sufijo>-etl   ──►  CloudWatch Logs · /aws/lambda/bootcamp-<sufijo>-etl
   │  JSON → Parquet
   ▼
S3 · bootcamp-<sufijo>-datos/salida/muestra.parquet
```

No vas a escribir código: vas a **leerlo y ejecutarlo**.

---

## Antes de empezar

Necesitas:

- **Git Bash** (Windows; viene con Git for Windows) o la terminal de macOS/Linux.
  Todos los comandos de esta guía se escriben en esa terminal.
- **Terraform** 1.9 o superior: `terraform version`
- **AWS CLI** v2: `aws --version`
- Tu **IAM user con su access key** (se crea en vivo en el bloque 2 de la sesión).

Abre la terminal **en la carpeta del laboratorio** (la que contiene este
README). Todos los comandos se ejecutan desde ahí.

---

## Paso 1 · Carga tus credenciales

Tus claves van en un archivo local, `.env.credentials`, que **nunca** se sube a
Git (ya está en `.gitignore`).

**1.1 Crea el archivo a partir de la plantilla:**

```bash
cp .env.credentials.example .env.credentials
```

**1.2 Ábrelo en tu editor y pega tus claves** en lugar de los textos `PEGA_AQUI_...`:

```text
AWS_ACCESS_KEY_ID=AKIA................
AWS_SECRET_ACCESS_KEY=........................................
AWS_DEFAULT_REGION=us-east-1
```

Sin comillas y sin espacios alrededor del `=`. Guarda el archivo.

**1.3 Carga las claves en la terminal:**

```bash
set -a
source .env.credentials
set +a
```

`set -a` hace que cada variable del archivo se **exporte**, para que AWS CLI y
Terraform puedan verla. `set +a` lo vuelve a desactivar.

**1.4 Comprueba quién eres en AWS:**

```bash
aws sts get-caller-identity
```

Debe mostrar tu usuario (`"Arn": "arn:aws:iam::<cuenta>:user/<tu usuario>"`).
Si da error, mira [Problemas frecuentes](#problemas-frecuentes).

> **Importante:** las variables solo viven en **esa** terminal. Si abres otra
> terminal (o la cierras), repite el paso 1.3.

---

## Paso 2 · Prepara y revisa el plan

```bash
terraform -chdir=infra init
terraform -chdir=infra plan
```

- `init` descarga los plugins de Terraform (la primera vez tarda un poco).
- `plan` muestra lo que **se va a crear**, sin tocar nada todavía.

Hoy esperas ver solo `+` (crear) y al final algo como
`Plan: 12 to add, 0 to change, 0 to destroy.` Si aparece algo que se destruye
(`-`) y no lo esperabas, **no sigas** y pregunta.

> **¿Y el nombre del bucket?** Los nombres de bucket son únicos en todo el mundo,
> así que Terraform le añade un sufijo aleatorio de 6 caracteres
> (`bootcamp-x7k2qd-datos`). No tienes que configurar nada.

---

## Paso 3 · Despliega

```bash
terraform -chdir=infra apply
```

Revisa el plan, escribe `yes` y espera. Al final Terraform muestra los nombres de
lo que creó:

```text
bucket         = "bootcamp-x7k2qd-datos"
lambda_name    = "bootcamp-x7k2qd-etl"
log_group_name = "/aws/lambda/bootcamp-x7k2qd-etl"
```

Todo lleva el mismo sufijo aleatorio (`x7k2qd` en el ejemplo): son **tus**
recursos de este laboratorio. Guarda sus nombres en variables para los
siguientes pasos:

```bash
BUCKET=$(terraform -chdir=infra output -raw bucket)
LAMBDA=$(terraform -chdir=infra output -raw lambda_name)
LOG_GROUP=$(terraform -chdir=infra output -raw log_group_name)
echo $BUCKET $LAMBDA $LOG_GROUP
```

---

## Paso 4 · Sube el archivo y observa

**4.1 Sube el JSON a la carpeta `entrada/`:**

```bash
aws s3 cp datos/muestra.json s3://$BUCKET/entrada/
```

S3 emite el evento y la Lambda se ejecuta sola. Espera unos 10–20 segundos (la
primera ejecución es más lenta).

**4.2 Mira el Parquet en la carpeta `salida/` y compara tamaños:**

```bash
aws s3 ls s3://$BUCKET/salida/ --human-readable
ls -lh datos/muestra.json
```

El JSON pesa unos 3 MB; el Parquet, cerca de 200 KB: el mismo dato, mucho más
liviano.

**4.3 Lee los logs de la Lambda:**

```bash
MSYS_NO_PATHCONV=1 aws logs tail $LOG_GROUP --since 10m
```

Debes ver `Evento recibido: entrada/muestra.json` y
`Parquet escrito: salida/muestra.parquet (20000 filas)`.

> `MSYS_NO_PATHCONV=1` evita que Git Bash convierta `/aws/lambda/...` en una ruta
> de Windows. En macOS/Linux no hace falta, pero tampoco molesta.

### Qué debes ver

- Un archivo `muestra.parquet` en `salida/`.
- En los logs, la línea «Evento recibido» con el nombre de tu archivo.
- La Lambda corrió **sola**: tú solo subiste el archivo.

---

## Paso 5 · Destruye todo

```bash
terraform -chdir=infra destroy
```

Escribe `yes`. Luego comprueba que no quedó nada:

```bash
terraform -chdir=infra state list
aws s3 ls | grep bootcamp
MSYS_NO_PATHCONV=1 aws logs describe-log-groups --log-group-name-prefix /aws/lambda/bootcamp-
```

Lo esperado: `state list` sin salida, ningún bucket `bootcamp-...` y
`"logGroups": []`. El bucket se borra aunque tenga archivos (`force_destroy`) y
el log group se borra con todos sus logs: los creó Terraform para este
laboratorio y no tienen versionado ni protección contra borrado.

**Tu IAM user y tu access key NO se borran:** los usarás en la sesión 2.

---

## Plan B · Si el evento no dispara la Lambda

Invócala a mano con un evento de prueba igual al que enviaría S3. Apunta al
archivo que ya subiste en el paso 4.1:

```bash
echo '{"Records":[{"s3":{"bucket":{"name":"'$BUCKET'"},"object":{"key":"entrada/muestra.json"}}}]}' > evento-mio.json
aws lambda invoke \
  --function-name $LAMBDA \
  --payload file://evento-mio.json \
  --cli-binary-format raw-in-base64-out \
  salida.json
cat salida.json
```

Si así funciona, la Lambda está bien y el problema es el disparo. Avisa al
facilitador.

---

## Problemas frecuentes

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| `Unable to locate credentials` | No cargaste las claves en **esta** terminal | Repite el paso 1.3 |
| Terraform pide `var.sufijo … Enter a value` | Estás usando una versión antigua del repositorio | Descarga la versión actual (el sufijo ya es opcional) o pulsa Enter para dejarlo vacío |
| `SignatureDoesNotMatch` o `InvalidClientTokenId` | Clave mal copiada, espacios o comillas, o el archivo se guardó con saltos de línea de Windows | Revisa `.env.credentials`; luego ejecuta `sed -i 's/\r$//' .env.credentials` y repite el paso 1.3 |
| `AccessDenied` | Tu IAM user no tiene la política del laboratorio | Revisa el bloque 2: el usuario necesita `AdministratorAccess` |
| `BucketAlreadyExists` | Muy improbable con el sufijo aleatorio | Ejecuta `terraform -chdir=infra apply -replace=random_string.sufijo` para generar otro |
| `x509: certificate signed by unknown authority` en `init`, `plan` o `validate` | Tu antivirus (AVG, Avast…) inspecciona HTTPS y corta la conexión de Terraform con sus plugins | Desactiva el escaneo HTTPS del antivirus durante el laboratorio o excluye `terraform.exe` |
| `aws logs` dice que el log group no existe y muestra una ruta `C:/Program Files/Git/...` | Git Bash convirtió la ruta | Antepón `MSYS_NO_PATHCONV=1` al comando |
| No aparece el Parquet | Archivo fuera de `entrada/`, extensión distinta de `.json` o arranque en frío | Espera 30 s, revisa los logs (4.3) o usa el [Plan B](#plan-b--si-el-evento-no-dispara-la-lambda) |
| ¿Quiero otro nombre de bucket? | El sufijo es opcional | `cp infra/terraform.tfvars.example infra/terraform.tfvars` y define `sufijo` (3–12 minúsculas o dígitos) |

---

## Reglas de oro con tus credenciales

- **Nunca** pongas tus claves en el código, en Terraform, en el chat ni en una
  captura de pantalla. Solo en `.env.credentials`.
- **Nunca** subas `.env.credentials` a GitHub: hay bots que encuentran claves
  expuestas en minutos.
- Tu usuario tiene `AdministratorAccess` **solo** porque es tu cuenta personal de
  laboratorio. En una empresa se usa el mínimo privilegio y credenciales
  temporales.
- **Al terminar el bootcamp:** desactiva y elimina la access key y el IAM user, y
  borra `.env.credentials`.

---

## ¿De dónde saca la Lambda su código?

**No de tu bucket.** El código nunca pasa por S3:

1. **Terraform arma el zip en tu PC.** En `infra/modules/lambda/main.tf`, el
   bloque `data "archive_file"` comprime `src/handler.py` en
   `infra/modules/lambda/build/handler.zip` en cada `plan` o `apply` (esa carpeta
   no se sube a Git).
2. **Terraform envía el zip directo a Lambda.** `aws_lambda_function` tiene
   `filename = …handler.zip`. Durante el `apply`, Terraform manda el contenido
   del zip en la misma llamada a la API que crea o actualiza la función.
3. **Lambda guarda su propia copia** en un almacenamiento interno de AWS, que no
   aparece en tu cuenta. Compruébalo con
   `aws lambda get-function --function-name $LAMBDA --query Code.Location`:
   devuelve un enlace temporal a un bucket de AWS, no al tuyo.
4. **Las actualizaciones se detectan solas.** `source_code_hash` es la huella del
   zip: si cambias `handler.py`, el siguiente `apply` sube el código nuevo; si no,
   no sube nada.

**PyArrow tampoco viene de tu cuenta.** Lo aporta la *layer* pública
[AWS SDK for pandas](https://aws-sdk-pandas.readthedocs.io/en/stable/layers.html),
publicada por AWS. Tu función solo hace referencia a ella por su ARN (variable
`layer_arn`).

> **¿Y si el código fuera más grande?** Subirlo directo funciona para zips de
> hasta 50 MB (el nuestro pesa menos de 1 KB). Los paquetes más grandes se suben
> primero a un bucket S3 (`s3_bucket` y `s3_key` en lugar de `filename`) o se
> empaquetan como imagen de contenedor en Amazon ECR.

---

## Qué hay en este repositorio

| Ruta | Qué es |
|---|---|
| `infra/` | El Terraform: `main.tf` conecta un módulo por servicio |
| `infra/modules/s3/` | El bucket privado y cifrado, con las carpetas `entrada/` y `salida/` |
| `infra/modules/iam/` | El rol de la Lambda: lee `entrada/`, escribe `salida/` y sus logs |
| `infra/modules/cloudwatch/` | El log group de la Lambda, con retención de 3 días |
| `infra/modules/lambda/` | La función, su código (`src/handler.py`) y el disparador (`trigger.tf`) |
| `datos/` | `muestra.json`: 20 000 ventas ficticias, el archivo que subes en el paso 4 |
| `scripts/` | Herramientas del ponente: generar muestras, cargar credenciales y la prueba e2e |
| `docs/` | `idea-base.md` (la idea del proyecto: público, objetivos, arquitectura y principios), el diagrama `architecture/architecture.dot` (Graphviz) y las decisiones de arquitectura ([`internal/adr/`](docs/internal/adr/README.md): Terraform modular, `force_destroy`, IAM, empaquetado, nombres, logs y credenciales) |

---

## Para el ponente

Herramientas solo para preparar y probar (requiere [`uv`](https://docs.astral.sh/uv/)
y Python 3.12):

```bash
uv sync                                    # entorno local
uv run pytest                              # prueba local del handler (sin AWS)
uv run python scripts/generar_muestra.py   # genera datos/muestra_AAAAMMDD-HHMMSS.json

# e2e contra AWS (tras apply). El wrapper carga .env.credentials solo para ese comando:
bash scripts/con_credenciales.sh uv run python scripts/e2e.py [--archivo datos/<archivo>.json]
```

`e2e.py` sube el archivo a `entrada/`, espera el Parquet y valida que cada cosa
llegó a su recurso: el JSON solo en `entrada/`, el Parquet en `salida/` con las
mismas filas y columnas, y los logs de esa ejecución en el log group de la
Lambda. Termina con `RESULTADO: PASA` o `FALLA` y borra lo que subió (salvo con
`--conservar`). Si el Parquet no aparece, muestra las métricas de la Lambda y la
invoca a mano para separar «la Lambda falla» de «el disparo de S3 falla».

`con_credenciales.sh` ejecuta cualquier comando con tus claves cargadas, sin
dejarlas en la terminal: `bash scripts/con_credenciales.sh aws s3 ls`.

`generar_muestra.py` nunca sobrescribe `datos/muestra.json`: cada ejecución crea
un archivo nuevo con la fecha y hora en el nombre (git los ignora). Para que
los participantes usen una muestra nueva, renómbrala a `datos/muestra.json`.

### Cómo ejecutar los scripts

Ejecútalos siempre **desde la raíz del repositorio** (la carpeta que contiene
`pyproject.toml`) y con rutas relativas:

```bash
# Opción A (recomendada): uv usa el entorno .venv sin activarlo
uv run python scripts/generar_muestra.py

# Opción B: con el entorno activado
source .venv/Scripts/activate     # Git Bash en Windows (macOS/Linux: .venv/bin/activate)
python scripts/generar_muestra.py
```

En PowerShell, la activación es `.venv\Scripts\Activate.ps1` y el comando es el
mismo: `python scripts\generar_muestra.py`.

`--help` muestra las opciones de cada script; por ejemplo,
`uv run python scripts/generar_muestra.py --filas 5000` genera una muestra más
pequeña.

> **Evita el botón ▶ «Run Python File» de VS Code si tu terminal es Git Bash.**
> La ruta del proyecto tiene espacios (`5. Webinars`), así que VS Code la envuelve
> en comillas dobles y Git Bash la vuelve a envolver en comillas simples
> (`'"c:/.../generar_muestra.py"'`). Python recibe las comillas como parte del
> nombre del archivo y falla con
> `can't open file '...\"c:\...\generar_muestra.py"': [Errno 22] Invalid argument`.
> Usa los comandos de arriba, cambia la terminal por defecto de VS Code a
> PowerShell (*Terminal: Select Default Profile*) o ejecuta con
> *Run → Run Without Debugging* (Ctrl+F5).
