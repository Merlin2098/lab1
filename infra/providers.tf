# archivo: providers.tf
terraform {
  required_version = ">= 1.9"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.7"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

# Aquí NO van claves: el provider las toma del entorno
# (AWS_ACCESS_KEY_ID y AWS_SECRET_ACCESS_KEY) o de aws configure.
provider "aws" {
  region = var.region

  # Tags comunes para todos los recursos.
  default_tags {
    tags = {
      Proyecto    = var.proyecto
      Sesion      = "s1"
      Laboratorio = "lab1"
      CostCenter  = var.cost_center
      ManagedBy   = "Terraform"
    }
  }
}
