# Enlaces para preparar tu equipo

Todo lo que necesitas instalar **antes de la sesión**, en el orden recomendado.
Cada herramienta trae su enlace de descarga, un tutorial en video y el comando
para comprobar que quedó instalada. Ejecuta los comandos en **Git Bash** (o en la
terminal de macOS/Linux).

| # | Herramienta | ¿Para el laboratorio 1? | Comprobación |
|---|---|---|---|
| 1 | Git y Git Bash | **Obligatoria** | `git --version` |
| 2 | Visual Studio Code | Recomendada | `code --version` |
| 3 | Cuenta de AWS | **Obligatoria** | Entras a la consola web |
| 4 | AWS CLI v2 | **Obligatoria** | `aws --version` |
| 5 | Terraform ≥ 1.9 | **Obligatoria** | `terraform version` |
| 6 | Python 3.12 | Opcional (pruebas y scripts) | `python --version` |
| 7 | uv | Opcional (pruebas y scripts) | `uv --version` |

---

## 1. Git y Git Bash

Git Bash es la terminal que usamos en todo el bootcamp (en Windows viene con Git).

- Descarga: <https://git-scm.com/install/windows>
- Tutorial — configurar `user.name` y `user.email`:
  [Cómo configurar user.name y user.email por consola con Git Bash](https://www.youtube.com/watch?v=E_l1L6Ayiiw)

```bash
git --version
git config --global user.name "Tu Nombre"
git config --global user.email "tu@correo.com"
```

## 2. Visual Studio Code

Editor para leer el código del laboratorio. El repositorio ya trae Git Bash como
terminal por defecto (`.vscode/settings.json`).

- Descarga: <https://code.visualstudio.com/download>
- Tutorial: [Visual Studio Code: tutorial para principiantes](https://www.youtube.com/watch?v=CxF3ykWP1H4&t=210s)

## 3. Cuenta de AWS

- Crear la cuenta: <https://signin.aws.amazon.com/signup?request_type=register>
- Tutorial: [Crea tu cuenta en AWS gratis y algunos tips](https://www.youtube.com/watch?v=4Ik1OcQR2BE)

> El **IAM user y su access key** se crean en vivo durante la sesión. No los
> crees antes ni compartas tus claves con nadie.

## 4. AWS CLI v2

- Instalación (guía oficial en español):
  <https://docs.aws.amazon.com/es_es/cli/latest/userguide/getting-started-install.html>
- Tutorial: [Instalación y configuración de AWS CLI](https://www.youtube.com/watch?v=Q1jL7ljAuOo)

```bash
aws --version   # debe empezar por aws-cli/2.
```

> En este laboratorio **no** usamos `aws configure`: las claves se cargan desde
> `.env.credentials` (ver el Paso 1 del [README](../../README.md#paso-1--carga-tus-credenciales)).

## 5. Terraform

- Descarga: <https://developer.hashicorp.com/terraform/install>
- Tutorial: [Instalación de Terraform en Windows](https://www.youtube.com/watch?v=ziLybrNqMho)

```bash
terraform version   # 1.9 o superior
```

## 6. Python 3.12

Solo hace falta para ejecutar las pruebas y los scripts (`scripts/`). El
laboratorio funciona sin Python. El proyecto exige **3.12** (`.python-version`).

- Descarga: <https://www.python.org/downloads/>
- Tutorial: [Cómo instalar Python en Windows 10/11 paso a paso](https://www.youtube.com/watch?v=xd_0RN2SyfI)
- Tutorial — añadir Python al PATH: [¿Cómo agregar Python al Path de Windows?](https://www.youtube.com/watch?v=B08TNPt7a-M)

## 7. uv (gestor de paquetes de Python)

Crea el entorno virtual e instala las dependencias del proyecto con un comando
(`uv sync`). Si Python 3.12 no está instalado, uv puede descargarlo.

- Instalación: <https://github.com/astral-sh/uv#installation>

```bash
uv --version
```

---

## Documentación de referencia

- Documentación oficial de AWS: <https://docs.aws.amazon.com/>

## Opcional: asistentes de IA (Claude Code)

No son necesarios para el laboratorio. Son las herramientas que usa el ponente
con Claude Code para consultar documentación y trabajar en el repositorio.

| Herramienta | Para qué sirve | Enlace |
|---|---|---|
| AWS Documentation MCP Server | Consultar la documentación de AWS desde el asistente | <https://awslabs.github.io/mcp/servers/aws-documentation-mcp-server> |
| Terraform MCP Server | Consultar providers y módulos de Terraform | <https://github.com/hashicorp/terraform-mcp-server> |
| Superpowers | Habilidades de flujo de trabajo (planificar, depurar, probar) | <https://github.com/obra/superpowers> |
| gstack | Conjunto de habilidades (revisión, QA, despliegue) | <https://github.com/garrytan/gstack> |
| context-mode | Reduce el contexto que consumen las salidas grandes | <https://github.com/mksglu/context-mode> |
| Edge | Buscador de habilidades públicas para el asistente | <https://github.com/edge-toolkit/core> |
