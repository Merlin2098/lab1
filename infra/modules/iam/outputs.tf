output "resource_arn" {
  description = "ARN del rol de la Lambda."
  value       = aws_iam_role.lambda.arn

  # El rol se entrega con su política ya aplicada.
  depends_on = [aws_iam_role_policy.lambda]
}
