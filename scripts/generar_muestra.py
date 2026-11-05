"""Genera ventas ficticias para el laboratorio (solo el ponente).

Cada ejecución escribe un archivo nuevo, datos/muestra_AAAAMMDD-HHMMSS.json, para
no sobrescribir datos/muestra.json (el archivo que usan los participantes y el
README). Para publicar una muestra nueva, renómbrala a muestra.json.

Es un arreglo JSON con un objeto por línea, para que se pueda abrir y leer.
Tiene decenas de miles de filas: con pocas, el Parquet puede pesar más que el JSON.

Cada ejecución usa una semilla aleatoria, así que los datos cambian. La semilla
se imprime al final: con --semilla N se reproduce esa misma muestra
(--semilla 2026 regenera la de datos/muestra.json).

Uso: uv run python scripts/generar_muestra.py [--filas 20000] [--semilla N]
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

DIRECTORIO = Path(__file__).resolve().parents[1] / "datos"

TIENDAS = ["Lima Centro", "Miraflores", "San Isidro", "Arequipa", "Trujillo", "Cusco"]
PRODUCTOS = {
    "cafe": ("bebidas", 12.5),
    "te": ("bebidas", 8.0),
    "chocolate": ("snacks", 6.5),
    "galletas": ("snacks", 4.2),
    "quinua": ("granos", 15.9),
    "arroz": ("granos", 5.3),
}


def generar(filas: int, semilla: int = 2026) -> list[dict]:
    rng = random.Random(semilla)
    inicio = date(2026, 1, 1)
    registros = []
    for i in range(1, filas + 1):
        producto = rng.choice(list(PRODUCTOS))
        categoria, precio = PRODUCTOS[producto]
        cantidad = rng.randint(1, 10)
        registros.append(
            {
                "id_venta": i,
                "fecha": (inicio + timedelta(days=rng.randint(0, 299))).isoformat(),
                "tienda": rng.choice(TIENDAS),
                "producto": producto,
                "categoria": categoria,
                "cantidad": cantidad,
                "precio_unitario": precio,
                "total": round(cantidad * precio, 2),
            }
        )
    return registros


def ruta_salida(ahora: datetime | None = None) -> Path:
    """datos/muestra_AAAAMMDD-HHMMSS.json, con la hora local de la ejecución."""
    ahora = ahora or datetime.now()
    return DIRECTORIO / f"muestra_{ahora:%Y%m%d-%H%M%S}.json"


def main() -> None:
    # La consola de Windows no siempre usa UTF-8: evita que las tildes salgan como «�».
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--filas", type=int, default=20000)
    parser.add_argument(
        "--semilla",
        type=int,
        default=None,
        help="Semilla del generador. Sin ella, cada ejecución genera datos distintos; "
        "con ella, se repiten (la muestra versionada usa 2026).",
    )
    args = parser.parse_args()

    semilla = (
        args.semilla
        if args.semilla is not None
        else random.SystemRandom().randrange(10**6)
    )
    registros = generar(args.filas, semilla)
    lineas = ",\n".join(json.dumps(r, ensure_ascii=False) for r in registros)
    salida = ruta_salida()
    salida.parent.mkdir(exist_ok=True)
    # Modo "x": falla en lugar de sobrescribir si el archivo ya existe
    # (dos ejecuciones dentro del mismo segundo).
    with salida.open("x", encoding="utf-8", newline="\n") as f:
        f.write(f"[\n{lineas}\n]\n")
    print(
        f"{salida} · {len(registros)} filas · {salida.stat().st_size / 1024:.0f} KB"
        f" · semilla {semilla} (repítela con --semilla {semilla})"
    )


if __name__ == "__main__":
    main()
