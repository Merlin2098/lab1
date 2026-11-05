# ADR-0009 — Credenciales por access key en .env.credentials, sin perfiles

- **Estado:** aceptada
- **Fecha:** 2026-11-05
- **Decide:** Ricardo Uculmana (ponente)

## Contexto

El participante necesita que Terraform y AWS CLI usen las claves de su IAM user.
Las opciones habituales son un perfil nombrado (`aws configure --profile`),
`aws configure` sin perfil o variables de entorno. Además, las claves no pueden
acabar nunca en el repositorio, el código ni las capturas.

## Decisión

1. **Las claves van en `.env.credentials`,** copiado de la plantilla versionada
   `.env.credentials.example` (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`,
   `AWS_DEFAULT_REGION=us-east-1`).
2. **Se cargan en la terminal** con:

   ```bash
   set -a
   source .env.credentials
   set +a
   ```

3. **Terraform, AWS CLI y boto3 las toman del entorno** (cadena de credenciales
   por defecto). El provider de AWS **no** tiene `profile`, `access_key` ni
   `secret_key`, y no hay variables de Terraform para ellas.
4. **`.env.credentials` está en `.gitignore`**; la plantilla no (excepción
   `!.env.credentials.example`), y sus marcadores (`PEGA_AQUI_…`) no usan `<` ni
   `>` porque bash los interpreta como redirección.
5. **Para scripts del ponente,** `scripts/con_credenciales.sh <comando>` carga el
   archivo solo para ese comando, sin dejar las claves exportadas en la terminal.

## Alternativas descartadas

- **Perfil nombrado** (`--profile bootcamp`). Exige añadir `--profile` a cada
  comando y `profile` al provider; la propuesta inicial lo usaba y se cambió por
  simplicidad.
- **`aws configure` sin perfil.** Funciona igual con este código, pero guarda las
  claves en `~/.aws/credentials` sin que el participante vea dónde ni por qué.
- **Claves en `terraform.tfvars` o en el provider.** Prohibido: acaban en Git o
  en el state.

## Consecuencias

- **Las variables solo viven en esa terminal:** al abrir otra hay que repetir el
  `source`. El README lo destaca.
- **El archivo está dentro de la carpeta del repo;** solo `.gitignore` evita que
  se suba. Por eso se insiste en no forzar su inclusión ni compartirlo.
- **Saltos de línea de Windows:** Git Bash los tolera al hacer `source`; en
  macOS/Linux romperían la clave. El README trae el arreglo
  (`sed -i 's/\r$//' .env.credentials`).
- **Al terminar el bootcamp,** el participante desactiva y elimina la access key y
  borra `.env.credentials`.
