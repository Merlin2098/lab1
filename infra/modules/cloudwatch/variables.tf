variable "nombre_log_group" {
  type        = string
  description = "Nombre del log group (/aws/lambda/<función>)."
}

variable "retencion_dias" {
  type        = number
  description = "Días de retención de los logs."
}
