variable "nombre_bucket" {
  type        = string
  description = "Nombre global y único del bucket."
}

variable "carpetas" {
  type        = list(string)
  description = "Prefijos que se crean como carpetas (terminan en /)."
}
