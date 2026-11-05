output "function_name" {
  description = "Nombre de la función."
  value       = aws_lambda_function.fn.function_name
}

output "resource_arn" {
  description = "ARN de la función."
  value       = aws_lambda_function.fn.arn
}
