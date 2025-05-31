#!/usr/bin/env python3
"""
ingest_to_raw.py
----------------
• Descarga (o actualiza) dos CSV generados con main.py
  – inflacion_multi_country.csv
  – inversion_extranjera_multi_country.csv
• Sube esos dos CSV + los tres locales (IPC, COLCAP, tasas de interés)
  al bucket S3, prefijo raw/.

Los archivos locales deben estar junto a este script.
"""

import os
import sys
import datetime
import boto3
import requests

BUCKET = "juanzuluaga-proyecto3"
RAW_PREFIX = "raw"

# URLs generadas previamente por main.py (o desde GitHub RAW si quisieras)
#REMOTE = {
#    "inflacion_multi_country.csv":
#        "https://raw.githubusercontent.com/joseduquep/p3-ingenieria-datos-finanzas/main/inflacion_multi_country.csv",
#    "inversion_extranjera_multi_country.csv":
#        "https://raw.githubusercontent.com/joseduquep/p3-ingenieria-datos-finanzas/main/inversion_extranjera_multi_country.csv",
#}

LOCAL_ONLY = [
    "indice_precios_consumidor.csv",
    "tasas_interes_politica.csv",
]


s3 = boto3.client("s3")


def download(url: str, dest: str):
    print(f"Descargando {dest} …")
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    with open(dest, "wb") as f:
        f.write(r.content)


def upload(file_name: str):
    key = f"{RAW_PREFIX}/{file_name}"
    print(f"Subiendo a s3://{BUCKET}/{key}")
    s3.upload_file(file_name, BUCKET, key)


def main():
    # 1) Descarga/actualiza remotos
#    for fname, url in REMOTE.items():
#       download(url, fname)
#        upload(fname)

    # 2) Sube los CSV locales
    for fname in LOCAL_ONLY:
        if not os.path.isfile(fname):
            print(f"⚠️  Archivo local no encontrado: {fname}", file=sys.stderr)
            continue
        print(f"Subiendo local {fname} → s3://{BUCKET}/{RAW_PREFIX}/{fname}")
        upload(fname)

    print(f"✔ Ingesta completa: {datetime.date.today()}")


if __name__ == "__main__":
    main()

