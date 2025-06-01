#!/usr/bin/env python3
import boto3, requests, pandas as pd, os, tempfile
from datetime import date

BUCKET = os.environ.get("BUCKET")
PREFIX = os.environ.get("PREFIX_RAW", "raw/")

s3 = boto3.client("s3")

# Mapa nombre de archivo → URL de API
API_MAP = {
    "inflacion_multi_country.csv":
        "https://api.worldbank.org/v2/country/CO;BR;CN;DE;JP;US/indicator/FP.CPI.TOTL.ZG?format=json&per_page=1000",
    "inversion_extranjera_multi_country.csv":
        "https://api.worldbank.org/v2/country/CO;BR;CN;DE;JP;US/indicator/BX.KLT.DINV.CD.WD?format=json&per_page=1000"
}

def fetch_and_upload(name, url):
    print(f"Descargando {name} …")
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()[1]
    df = pd.DataFrame([{
        "country": e["country"]["value"],
        "date":    e["date"],
        "value":   e["value"]
    } for e in data])
    # Guarda en temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        df.to_csv(tmp.name, index=False)
        key = PREFIX + name
        print(f"Subiendo a s3://{BUCKET}/{key}")
        s3.upload_file(tmp.name, BUCKET, key)
        os.unlink(tmp.name)

def main():
    # 1) Descarga desde API y sube
    for fname, url in API_MAP.items():
        fetch_and_upload(fname, url)

    # 2) Sube CSV locales que ya tengas en tu directorio home
    local_csvs = [
        "Índice de Precios al Consumidor (IPC).csv",
        "Tasas de interés de política monetaria.csv"
    ]
    for f in local_csvs:
        if os.path.exists(f):
            print(f"Subiendo local {f} → s3://{BUCKET}/{PREFIX}{f}")
            s3.upload_file(f, BUCKET, PREFIX + f)

    print("✔ Ingesta completa:", date.today())

if __name__ == "__main__":
    main()
