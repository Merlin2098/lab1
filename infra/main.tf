# archivo: main.tf
# Cada servicio vive en su propio módulo (infra/modules/<servicio>).
# Sufijo aleatorio por si no defines uno: se guarda en el state
# y no cambia hasta el destroy.
resource "random_string" "sufijo" {
  length  = 6
  special = false
  upper   = false
}

locals {
  sufijo = coalesce(var.sufijo, random_string.sufijo.result)
  # Todos los nombres llevan el sufijo: cada despliegue tiene sus propios
  # bucket, Lambda, rol y log group, y nada choca con restos de otro.
  nombre_bucket = "${var.proyecto}-${local.sufijo}-datos"
  nombre_lambda = "${var.proyecto}-${local.sufijo}-etl"
}

# Un bucket con dos carpetas: entrada/ y salida/.
module "s3" {
  source        = "./modules/s3"
  nombre_bucket = local.nombre_bucket
  carpetas      = [var.prefijo_entrada, var.prefijo_salida]
}

# Log group de la Lambda, con retención corta.
module "cloudwatch" {
  source           = "./modules/cloudwatch"
  nombre_log_group = "/aws/lambda/${local.nombre_lambda}"
  retencion_dias   = var.retencion_logs_dias
}

# Rol de la Lambda: lee entrada/, escribe salida/ y sus logs.
module "iam" {
  source          = "./modules/iam"
  nombre_rol      = "${local.nombre_lambda}-rol"
  bucket_arn      = module.s3.resource_arn
  prefijo_entrada = var.prefijo_entrada
  prefijo_salida  = var.prefijo_salida
  log_group_arn   = module.cloudwatch.log_group_arn
}

# Función y disparador (evento ObjectCreated de S3).
module "lambda" {
  source          = "./modules/lambda"
  nombre          = local.nombre_lambda
  rol_arn         = module.iam.resource_arn
  layer_arn       = var.layer_arn
  log_group_name  = module.cloudwatch.log_group_name
  bucket_id       = module.s3.bucket
  bucket_arn      = module.s3.resource_arn
  prefijo_entrada = var.prefijo_entrada
  sufijo_entrada  = var.sufijo_entrada
  prefijo_salida  = var.prefijo_salida
}
