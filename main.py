import requests
import pandas as pd
from typing import List

BASE_URL = "https://api.worldbank.org/v2"

# Indicadores a consultar
INDICATORS = {
    "pib": "NY.GDP.MKTP.CD",
    "inflacion": "FP.CPI.TOTL.ZG",
    "inversion_extranjera": "BX.KLT.DINV.CD.WD"
}

# Países a usar como muestra de referencia global
# Puedes agregar más: US, CN, BR, DE, JP...
COUNTRIES = ["CO", "US", "CN", "BR", "DE", "JP"]


def fetch_indicator(indicator_code: str, country_code: str, max_records: int = 1000) -> pd.DataFrame:
    url = f"{BASE_URL}/country/{country_code}/indicator/{indicator_code}?format=json&per_page={max_records}"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Error al obtener datos: {response.status_code}")

    try:
        data = response.json()[1]
    except Exception:
        raise Exception(
            "Formato de respuesta inesperado o datos no disponibles.")

    records = []
    for entry in data:
        records.append({
            "country": entry["country"]["value"],
            "date": entry["date"],
            "value": entry["value"]
        })

    return pd.DataFrame(records)


def save_indicator(indicator_name: str, indicator_code: str, countries: List[str]):
    all_data = pd.DataFrame()

    for country in countries:
        print(f"Obteniendo {indicator_name.upper()} para {country}")
        df = fetch_indicator(indicator_code, country)
        df["indicator"] = indicator_name
        all_data = pd.concat([all_data, df], ignore_index=True)

    filename = f"{indicator_name}_multi_country.csv"
    all_data.to_csv(filename, index=False)
    print(f"✅ Guardado como: {filename}")


def main():
    for name, code in INDICATORS.items():
        save_indicator(name, code, COUNTRIES)


if __name__ == "__main__":
    main()
