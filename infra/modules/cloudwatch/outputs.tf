output "log_group_name" {
  description = "Nombre del log group."
  value       = aws_cloudwatch_log_group.lambda.name
}

output "log_group_arn" {
  description = "ARN del log group."
  value       = aws_cloudwatch_log_group.lambda.arn
}

output "resource_arn" {
  description = "ARN del log group (convención común de los módulos)."
  value       = aws_cloudwatch_log_group.lambda.arn
}
