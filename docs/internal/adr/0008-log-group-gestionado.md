# ADR-0008 — Log group de CloudWatch gestionado por Terraform

- **Estado:** aceptada
- **Fecha:** 2026-11-05
- **Decide:** Ricardo Uculmana (ponente)

## Contexto

Si no se declara nada, Lambda crea **por su cuenta** el log group
`/aws/lambda/<función>` la primera vez que escribe un log, con **retención
infinita**. Ese log group no lo conoce Terraform: queda huérfano después del
`destroy`, sigue acumulando costo de almacenamiento y hace fallar el siguiente
`apply` si Terraform intenta crear uno con el mismo nombre.

## Decisión

1. **El módulo `cloudwatch` crea el log group** `/aws/lambda/bootcamp-<sufijo>-etl`
   **antes** que la función.
2. **Retención de 3 días** (variable `retencion_logs_dias`): suficiente para la
   sesión y la hora de consultas.
3. **La Lambda escribe explícitamente en ese log group** mediante
   `logging_config { log_group = … }`. Esa referencia también obliga a Terraform
   a crear el log group primero.
4. **El rol no tiene `logs:CreateLogGroup`:** la Lambda no puede crear otro
   ([ADR-0005](0005-iam-minimo-privilegio.md)).
5. **Nada impide borrarlo:** `skip_destroy = false` y
   `deletion_protection_enabled = false`
   ([ADR-0003](0003-destroy-completo.md)).
6. **Formato de log `Text`.** Las líneas que escribe el handler («Evento
   recibido…», «Parquet escrito…») se leen directamente con `aws logs tail`.

## Alternativas descartadas

- **Dejar que Lambda cree el log group.** Es el comportamiento por defecto y la
  causa de los huérfanos y de la retención infinita.
- **Logs en formato JSON.** Útiles para consultas en CloudWatch Logs Insights,
  pero menos legibles en la terminal para un primer contacto.

## Consecuencias

- **`destroy` borra el log group con todos sus logs:** no quedan restos ni costo.
- **La verificación del laboratorio se apoya en los logs:** el README (paso 4.3)
  y `scripts/e2e.py` buscan esas dos líneas en ese log group.
- **Si el log group se borra a mano** con la función viva, la Lambda no puede
  recrearlo (no tiene permiso) y sus logs se pierden hasta el siguiente `apply`.
