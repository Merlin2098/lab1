# ADR-0007 — Nombres con sufijo aleatorio y valores por defecto en todo

- **Estado:** aceptada
- **Fecha:** 2026-11-05
- **Decide:** Ricardo Uculmana (ponente)

## Contexto

Los nombres de bucket de S3 son **únicos en todo el mundo**. La primera versión
pedía a cada participante un sufijo propio (iniciales y 4 dígitos) mediante
`terraform.tfvars`. En la práctica, `terraform plan` se detenía a preguntar
`var.sufijo … Enter a value` a quien se saltaba ese paso: fricción innecesaria
en un repositorio que debe funcionar tal cual.

## Decisión

1. **`random_string.sufijo`** (6 caracteres, minúsculas y dígitos, sin símbolos)
   genera el sufijo en el primer `apply`. Se guarda en el state y no cambia hasta
   el `destroy`.
2. **La variable `sufijo` es opcional** (`default = null`). Si se define, gana
   sobre el aleatorio: `coalesce(var.sufijo, random_string.sufijo.result)`.
3. **Todos los nombres del despliegue llevan el sufijo:**

   | Recurso | Nombre |
   |---|---|
   | Bucket | `bootcamp-<sufijo>-datos` |
   | Lambda | `bootcamp-<sufijo>-etl` |
   | Rol IAM | `bootcamp-<sufijo>-etl-rol` |
   | Log group | `/aws/lambda/bootcamp-<sufijo>-etl` |

4. **Todas las variables tienen un valor por defecto que funciona**;
   `terraform.tfvars` es opcional.
5. **Tags comunes en `default_tags` del provider:** `Proyecto`, `Sesion`,
   `Laboratorio`, `CostCenter` y `ManagedBy`, en todos los recursos.
6. **Los comandos del README no copian nombres a mano:** después del `apply` se
   guardan `$BUCKET`, `$LAMBDA` y `$LOG_GROUP` desde `terraform output`.

## Alternativas descartadas

- **Sufijo obligatorio escrito por el participante.** Es el problema que motivó
  esta decisión.
- **ID de la cuenta como sufijo.** Es único y estable, pero aparecería en
  pantallas, capturas y outputs, y no debe mostrarse.
- **Nombres fijos** (`bootcamp-etl`). Dos despliegues en la misma cuenta
  chocarían, y un resto de un intento anterior haría fallar el `apply` con «ya
  existe».

## Consecuencias

- **Clonar y desplegar sin editar nada,** salvo `.env.credentials`.
- **Cada despliegue es dueño exclusivo de sus recursos:** nada choca con restos
  de otros despliegues.
- **Los nombres no se conocen hasta el `apply`.** Por eso el README toma los
  nombres de `terraform output` y el diagrama usa `<sufijo>`.
- **Cambiar el sufijo recrea los recursos.** Si hiciera falta un nombre nuevo
  (muy improbable): `terraform apply -replace=random_string.sufijo`.
