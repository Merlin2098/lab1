# archivo: modules/iam/main.tf
# Quién puede "ponerse" el rol: solo el servicio Lambda.
data "aws_iam_policy_document" "confianza" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda" {
  name               = var.nombre_rol
  assume_role_policy = data.aws_iam_policy_document.confianza.json

  # Si alguien adjunta otra política desde la consola, destroy la quita
  # antes de borrar el rol (sin esto falla con DeleteConflict).
  force_detach_policies = true
}

# Qué puede hacer la Lambda: lo mínimo necesario.
data "aws_iam_policy_document" "lambda" {
  statement {
    sid       = "LeerEntrada"
    actions   = ["s3:GetObject"]
    resources = ["${var.bucket_arn}/${var.prefijo_entrada}*"]
  }

  statement {
    sid       = "EscribirSalida"
    actions   = ["s3:PutObject"]
    resources = ["${var.bucket_arn}/${var.prefijo_salida}*"]
  }

  statement {
    sid       = "EscribirLogs"
    actions   = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["${var.log_group_arn}:*"]
  }
}

resource "aws_iam_role_policy" "lambda" {
  name   = "${var.nombre_rol}-politica"
  role   = aws_iam_role.lambda.id
  policy = data.aws_iam_policy_document.lambda.json
}
