
import os, json, boto3, requests, datetime

s3       = boto3.client('s3')
BUCKET   = os.environ['RAW_BUCKET']
INDICATORS = os.environ['INDICATORS'].split(',')   # ej. "NY.GDP.MKTP.CD,SL.UEM.TOTL.ZS,IT.NET.USER.ZS"
COUNTRIES  = os.environ.get('COUNTRIES', 'COL;BRA;ARG').split(';')

BASE_URL = "https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"

def save(obj, key):
    s3.put_object(Bucket=BUCKET, Key=key, Body=json.dumps(obj).encode())

def handler(event, ctx):
    ts_prefix = datetime.datetime.utcnow().strftime('%Y/%m/%d/%H%M%S')
    saved = 0

    for ind in INDICATORS:
        for cty in COUNTRIES:
            page = 1
            while True:
                url  = BASE_URL.format(country=cty, indicator=ind)
                resp = requests.get(url,
                                    params={"format": "json", "page": page},
                                    timeout=30)
                data = resp.json()

                # data[0] lleva metadatos, data[1] lleva filas
                if len(data) < 2 or not data[1]:
                    break

                key = f"{ts_prefix}/{ind}/{cty}/page_{page}.json"
                save(data, key)
                saved += 1
                page += 1

    return {"objects_saved": saved, "prefix": ts_prefix}

