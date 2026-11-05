variable "nombre" {
  type        = string
  description = "Nombre de la función."
}

variable "rol_arn" {
  type        = string
  description = "ARN del rol que asume la función."
}

variable "layer_arn" {
  type        = string
  description = "ARN de la layer con PyArrow."
}

variable "log_group_name" {
  type        = string
  description = "Log group donde escribe la función."
}

variable "bucket_id" {
  type        = string
  description = "Nombre del bucket que dispara la función."
}

variable "bucket_arn" {
  type        = string
  description = "ARN del bucket que puede invocar la función."
}

variable "prefijo_entrada" {
  type        = string
  description = "Solo los objetos de esta carpeta disparan la función."
}

variable "sufijo_entrada" {
  type        = string
  description = "Solo los objetos con esta extensión disparan la función."
}

variable "prefijo_salida" {
  type        = string
  description = "Carpeta donde la función escribe el Parquet."
}

variable "memoria_mb" {
  type        = number
  description = "Memoria de la función (PyArrow necesita más que los 128 MB por defecto)."
  default     = 512
}

variable "timeout_s" {
  type        = number
  description = "Tiempo máximo de ejecución (el arranque en frío de PyArrow tarda)."
  default     = 60
}
