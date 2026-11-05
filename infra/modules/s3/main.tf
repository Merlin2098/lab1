# archivo: modules/s3/main.tf
# Sin versionado. force_destroy permite borrar el bucket aunque tenga objetos.
resource "aws_s3_bucket" "datos" {
  bucket        = var.nombre_bucket
  force_destroy = true
}

# Privado: nadie puede hacerlo público.
resource "aws_s3_bucket_public_access_block" "datos" {
  bucket                  = aws_s3_bucket.datos.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Cifrado en reposo con claves de S3 (SSE-S3).
resource "aws_s3_bucket_server_side_encryption_configuration" "datos" {
  bucket = aws_s3_bucket.datos.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Carpetas vacías para que se vean en la consola desde el inicio.
resource "aws_s3_object" "carpeta" {
  for_each = toset(var.carpetas)

  bucket  = aws_s3_bucket.datos.id
  key     = each.value
  content = ""
}
