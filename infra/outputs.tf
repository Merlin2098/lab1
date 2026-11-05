# archivo: outputs.tf
output "bucket" {
  description = "Bucket del laboratorio (carpetas entrada/ y salida/)."
  value       = module.s3.bucket
}

output "lambda_name" {
  description = "Nombre de la función Lambda."
  value       = module.lambda.function_name
}

output "log_group_name" {
  description = "Log group de CloudWatch de la Lambda."
  value       = module.cloudwatch.log_group_name
}

output "log_group_arn" {
  description = "ARN del log group de la Lambda."
  value       = module.cloudwatch.log_group_arn
}

output "resource_arn" {
  description = "ARN de la función Lambda."
  value       = module.lambda.resource_arn
}

output "comando_subida" {
  description = "Comando listo para copiar: sube la muestra y dispara la Lambda."
  value       = "aws s3 cp datos/muestra.json s3://${module.s3.bucket}/${var.prefijo_entrada}"
}
