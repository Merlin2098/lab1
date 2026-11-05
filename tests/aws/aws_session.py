"""Sesión boto3 para las pruebas contra AWS.

Usa la cadena de credenciales por defecto, igual que Terraform y AWS CLI:
AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY del entorno o lo que dejó
`aws configure`. Nunca lee claves desde archivos del repositorio.
"""

from __future__ import annotations

import os

import boto3


def get_session() -> boto3.Session:
    return boto3.Session(region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"))


def get_client(service: str):
    return get_session().client(service)
