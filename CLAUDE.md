# CLAUDE.md

El contrato de este repositorio está en [AGENTS.md](AGENTS.md). Léelo antes de
cualquier tarea: sus reglas, límites de aprobación y guardas aplican igual a Claude.

## Específico de Claude Code

- **Shell:** Git Bash (`defaultShell: bash` en `.claude/settings.json`). Rutas con
  `/`, sintaxis POSIX y `MSYS_NO_PATHCONV=1` solo en los comandos `aws logs`.
- **Credenciales:** el ponente las carga en su terminal con
  `set -a; source .env.credentials; set +a` antes de abrir Claude Code, y Claude
  las hereda del entorno. Para pruebas contra AWS que el ponente pida, Claude
  usa `bash scripts/con_credenciales.sh <comando>`, que carga el archivo en un
  subproceso sin mostrarlo. Claude no lee, no escribe ni pide claves, y enmascara
  el ID de cuenta en lo que muestra. Si faltan, se detiene y avisa. `AWS_DEFAULT_REGION=us-east-1` viene de la configuración.
- **Permisos:** `.claude/settings.json` deniega `terraform apply`, `destroy`,
  `import` y `state rm`, y la lectura de `.env`, `.env.credentials` y `~/.aws/`.
  No buscar rodeos: pedir al ponente que los ejecute.
- **Validación sin desplegar:** `terraform -chdir=infra fmt -recursive`,
  `validate` y `plan`; `uv run pytest` (solo pruebas locales); `uv run ruff check`.
  `uv run pytest -m cloud` solo con aprobación y con el pipeline desplegado.
- **Documentación de AWS y Terraform:** usar los MCP de documentación cuando
  estén conectados. Si no lo están, decirlo y marcar el dato como pendiente de
  verificar en lugar de inventarlo.
- **Documentación:** cualquier cambio que toque un elemento del contrato de
  nombres actualiza en el mismo cambio el README y `docs/idea-base.md`.
- **Idioma:** responder en español.
