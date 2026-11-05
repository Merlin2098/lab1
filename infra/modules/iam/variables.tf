variable "nombre_rol" {
  type        = string
  description = "Nombre del rol de la Lambda."
}

variable "bucket_arn" {
  type        = string
  description = "ARN del bucket del laboratorio."
}

variable "prefijo_entrada" {
  type        = string
  description = "Carpeta que la Lambda puede leer."
}

variable "prefijo_salida" {
  type        = string
  description = "Carpeta donde la Lambda puede escribir."
}

variable "log_group_arn" {
  type        = string
  description = "ARN del log group donde la Lambda escribe."
}
