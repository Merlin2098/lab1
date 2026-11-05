# ADR-0005 — IAM: rol de mínimo privilegio para la Lambda

- **Estado:** aceptada
- **Fecha:** 2026-11-05
- **Decide:** Ricardo Uculmana (ponente)

## Contexto

En el laboratorio conviven dos identidades:

- **El IAM user del participante**, con `AdministratorAccess`. Es una cuenta
  personal de laboratorio y Terraform necesita crear roles y políticas; no lo
  gestiona este repositorio.
- **El rol de la Lambda**, que sí crea Terraform. Es lo que se enseña como buena
  práctica: una función solo debe poder hacer lo que necesita.

## Decisión

1. **Política de confianza:** solo el servicio `lambda.amazonaws.com` puede
   asumir el rol `bootcamp-<sufijo>-etl-rol`.
2. **Política de permisos en línea** (`aws_iam_role_policy`) con tres
   sentencias, cada una acotada a un recurso concreto:

   | Sid | Acción | Recurso |
   |---|---|---|
   | `LeerEntrada` | `s3:GetObject` | `arn:aws:s3:::<bucket>/entrada/*` |
   | `EscribirSalida` | `s3:PutObject` | `arn:aws:s3:::<bucket>/salida/*` |
   | `EscribirLogs` | `logs:CreateLogStream`, `logs:PutLogEvents` | `<ARN del log group>:*` |

3. **Sin políticas gestionadas por AWS** (ni siquiera
   `AWSLambdaBasicExecutionRole`, que permite escribir en cualquier log group y
   crear log groups).
4. **Sin `logs:CreateLogGroup`:** el log group lo crea Terraform
   ([ADR-0008](0008-log-group-gestionado.md)).
5. **Quién puede invocar la Lambda** no está en el rol: lo define
   `aws_lambda_permission`, limitado al principal `s3.amazonaws.com` y al ARN
   del bucket.
6. **El rol se entrega con su política ya aplicada:** la salida `resource_arn`
   del módulo `iam` depende de la política, así la función nunca se crea con un
   rol sin permisos.
7. **`force_detach_policies = true`** para que `destroy` no falle si alguien
   adjunta otra política desde la consola ([ADR-0003](0003-destroy-completo.md)).

## Alternativas descartadas

- **`s3:*` sobre el bucket.** Más corto, pero la Lambda podría borrar o
  sobrescribir cualquier archivo. Se usa como pregunta en clase: «¿qué podría
  hacer esta Lambda con `s3:*`?».
- **`AWSLambdaBasicExecutionRole`.** Cómoda, pero da permisos de logs sobre
  todos los log groups de la cuenta.

## Consecuencias

- **Si alguien cambia los prefijos,** la política cambia con ellos, porque usa
  las mismas variables que el filtro del evento.
- **Sin `s3:ListBucket`,** leer un objeto que no existe devuelve `AccessDenied`
  en lugar de `NoSuchKey`. Es aceptable: la Lambda solo lee la key que trae el
  evento.
- **Contraste didáctico:** usuario con `AdministratorAccess` (solo por ser un
  laboratorio personal) frente a un rol de mínimo privilegio.
