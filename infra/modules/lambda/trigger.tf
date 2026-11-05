# archivo: modules/lambda/trigger.tf
# El rol dice qué puede hacer la Lambda.
# Este permiso dice quién puede llamarla: S3.
resource "aws_lambda_permission" "s3" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.fn.arn
  principal     = "s3.amazonaws.com"
  source_arn    = var.bucket_arn
}

# Cuando se crea un .json en entrada/, S3 llama a la Lambda.
resource "aws_s3_bucket_notification" "n" {
  bucket = var.bucket_id

  lambda_function {
    lambda_function_arn = aws_lambda_function.fn.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = var.prefijo_entrada
    filter_suffix       = var.sufijo_entrada
  }

  depends_on = [aws_lambda_permission.s3]
}
