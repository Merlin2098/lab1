# archivo: modules/lambda/main.tf
# Terraform arma el zip: nadie tiene que empaquetar a mano.
data "archive_file" "codigo" {
  type        = "zip"
  source_file = "${path.module}/src/handler.py"
  output_path = "${path.module}/build/handler.zip"
}

resource "aws_lambda_function" "fn" {
  function_name    = var.nombre
  role             = var.rol_arn
  runtime          = "python3.12"
  architectures    = ["x86_64"]
  handler          = "handler.handler"
  filename         = data.archive_file.codigo.output_path
  source_code_hash = data.archive_file.codigo.output_base64sha256

  # PyArrow viene de la layer gestionada AWS SDK for pandas.
  layers      = [var.layer_arn]
  memory_size = var.memoria_mb
  timeout     = var.timeout_s

  environment {
    variables = {
      PREFIJO_SALIDA = var.prefijo_salida
    }
  }

  # Escribe en el log group que creó Terraform.
  logging_config {
    log_format = "Text"
    log_group  = var.log_group_name
  }
}
