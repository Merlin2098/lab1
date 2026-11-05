# archivo: modules/cloudwatch/main.tf
# Lo crea Terraform (y no la Lambda) para que destroy también lo borre.
# Los log groups no tienen force_destroy: al destruirlos se borran con
# todos sus logs. Lo que podría impedirlo queda desactivado a propósito:
resource "aws_cloudwatch_log_group" "lambda" {
  name              = var.nombre_log_group
  retention_in_days = var.retencion_dias

  skip_destroy                = false # destroy SÍ lo borra (no solo del state)
  deletion_protection_enabled = false # sin protección contra borrado
}
