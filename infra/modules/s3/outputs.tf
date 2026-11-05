output "bucket" {
  description = "Nombre del bucket."
  value       = aws_s3_bucket.datos.id
}

output "resource_arn" {
  description = "ARN del bucket."
  value       = aws_s3_bucket.datos.arn
}
