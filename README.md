# 🚀 Proyecto 3 — Arquitectura Batch para Big Data  
**Curso:** Tópicos Especiales en Telemática  
**Universidad EAFIT**  

**Equipo:**  
- José Alejandro Duque  
- Pedro Saldarriaga  
- Juan Pablo Zuluaga  

---

## 📖 Descripción General

Este proyecto desarrolla un **pipeline batch completo** para el procesamiento de datos económicos, desplegado en servicios cloud de **AWS**.  

El pipeline sigue todas las etapas del **ciclo de vida del dato**:

1️⃣ **Captura**  
2️⃣ **Ingesta en S3**  
3️⃣ **Procesamiento ETL (Spark sobre EMR)**  
4️⃣ **Generación de datasets refinados** (Parquet / CSV / JSON)  
5️⃣ **Exposición de resultados (URL pre-firmada)**  

---

## 🗺️ Arquitectura del Sistema

### Diagrama General

![image](https://github.com/user-attachments/assets/adb646e1-5c5b-46a5-89a1-61fb9409acf4)  

![image](https://github.com/user-attachments/assets/e582f511-0c58-47c0-b389-7866fbc3b2d6)  

### Tecnologías y Servicios

| Tecnología | Uso |
|------------|-----|
| **AWS S3** | Almacenamiento en zonas `raw/`, `trusted/` (Parquet), `refined/` (CSV + JSON) |
| **AWS EMR (Elastic MapReduce)** | Procesamiento distribuido con Spark |
| **Apache Spark** | ETL: limpieza, transformación, agregación (con formato Parquet columnar) |
| **Athena** | Validación de resultados mediante consultas SQL |
| **Bash** | Automatización con `run_pipeline.sh` |

---

## ⚙️ Ejecución del Pipeline

### 🚀 Prerrequisitos

- Bucket S3 creado (ejemplo: `juanzuluaga-proyecto3`)  
- Clúster EMR en estado `WAITING`  
- CSV de entrada ubicados en `~/`:

  - `inflacion_multi_country.csv`  
  - `inversion_extranjera_multi_country.csv`  
  - `indice_precios_consumidor.csv`  
  - `tasas_interes_politica.csv`  

---

### 📋 Pasos de Ejecución

1️⃣ **Subir scripts Spark actualizados a S3**  
2️⃣ **Ingestar datos a zona `raw/`**  
3️⃣ **Lanzar Steps en EMR**:  

    - ETL → genera zona `trusted/` (Parquet)  
    - Agregación → genera zona `refined/` (CSV + JSON)  

4️⃣ **Publicar URL pre-firmada con resultados**  

---

### 🖥️ Comando Único

```bash
./run_pipeline.sh

```
Este script realiza automáticamente:

✅ Subida de scripts  
✅ Ingesta a S3  
✅ Ejecución de Steps en EMR  
✅ Monitoreo de ejecución  
✅ Presentación de URL pre-firmada (válida por 7 días)  

---

## 📝 Uso de Formato Parquet

Utilizamos **Parquet** en `trusted/` por sus ventajas:

- Formato columnar  
- Alta compresión  
- Optimizado para consultas analíticas  
- Compatible con Spark y Athena  

### Ejemplo de estructura en `trusted/`:

```
trusted/indicator=inflacion_anual/country=Colombia/part-.parquet
trusted/indicator=inversion_extranjera_directa/country=Brasil/part-.parquet
```


---

## 🚧 Retos Abordados

- Manejo de columnas con tildes y espacios en los CSV  
- Coordinación entre zonas `raw → trusted → refined`  
- Depuración de errores en Steps de EMR  
- Adaptación a restricciones de AWS Academy  
- Construcción de un pipeline **100% automatizado**  

---

## ✅ Estado Final del Proyecto

- Pipeline probado y funcional en AWS  
- Resultados expuestos vía URL pre-firmada  
- Ejecución automática con `run_pipeline.sh`  
- Listo para **escalado** o integración con nuevas fuentes de datos  

---

¡Gracias por revisar nuestro proyecto! 🚀✨  
