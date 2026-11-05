# archivo: variables.tf
variable "sufijo" {
  type        = string
  description = "Opcional. Hace único el nombre del bucket; si no lo defines, se genera uno aleatorio."
  default     = null

  validation {
    condition     = var.sufijo == null || can(regex("^[a-z0-9]{3,12}$", var.sufijo))
    error_message = "Usa de 3 a 12 letras minúsculas o dígitos, sin espacios (ej. ab1234)."
  }
}

variable "region" {
  type        = string
  description = "Región única del bootcamp."
  default     = "us-east-1"
}

variable "proyecto" {
  type        = string
  description = "Prefijo de los nombres de los recursos."
  default     = "bootcamp"
}

variable "cost_center" {
  type        = string
  description = "Tag CostCenter para identificar los costos del laboratorio."
  default     = "bootcamp-aws"
}

variable "prefijo_entrada" {
  type        = string
  description = "Carpeta donde se suben los JSON. Solo esta carpeta dispara la Lambda."
  default     = "entrada/"
}

variable "sufijo_entrada" {
  type        = string
  description = "Extensión de los archivos que disparan la Lambda."
  default     = ".json"
}

variable "prefijo_salida" {
  type        = string
  description = "Carpeta donde la Lambda escribe los Parquet."
  default     = "salida/"

  validation {
    condition     = var.prefijo_salida != var.prefijo_entrada && endswith(var.prefijo_salida, "/")
    error_message = "La salida debe ser otra carpeta (terminada en /): si fuera la de entrada, la Lambda se dispararía a sí misma."
  }
}

variable "layer_arn" {
  type        = string
  description = "Layer gestionada AWS SDK for pandas (trae PyArrow). Debe coincidir con región, Python 3.12 y x86_64."
  # aws-sdk-pandas 3.18.0 · us-east-1 · Python 3.12 · x86_64
  default = "arn:aws:lambda:us-east-1:336392948345:layer:AWSSDKPandas-Python312:32"
}

variable "retencion_logs_dias" {
  type        = number
  description = "Días que CloudWatch guarda los logs de la Lambda."
  default     = 3
}
