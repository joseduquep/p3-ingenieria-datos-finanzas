#!/usr/bin/env bash
###############################################################################
# run_pipeline.sh  ·  Reusar clúster EMR existente (j-3NGAMTMFCJCT2)
#
# 1) ingest_to_raw.py       →  s3://$BUCKET/raw/
# 2) ETL_RAW_TO_TRUSTED     →  s3://$BUCKET/trusted/
# 3) REFINED_JSON           →  s3://$BUCKET/refined/json/
# 4) PUBLISH_JSON           →  copia JSON y crea summary.json + URL
###############################################################################

BUCKET=juanzuluaga-proyecto3
CLUSTER_ID=j-3NGAMTMFCJCT2    # ← clúster EMR en estado WAITING
REGION=us-east-1

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
INGEST_PY="${SCRIPT_DIR}/ingest_to_raw.py"

###############################################################################
# 1) INGESTA RAW
echo "1) Ingesta RAW (ingest_to_raw.py)…"
python3 "$INGEST_PY" || {
  echo "✖ Falló ingest_to_raw.py"; exit 1;
}
echo "✔ Ingesta RAW completada."

###############################################################################
# 2) AÑADIR STEPS AL CLÚSTER EXISTENTE
echo "2) Añadiendo Steps al clúster $CLUSTER_ID…"
STEP_IDS=$(
  aws emr add-steps --cluster-id "$CLUSTER_ID" --steps \
    'Type=Spark,Name=ETL_RAW_TO_TRUSTED,ActionOnFailure=CANCEL_AND_WAIT,Args=["s3://'"$BUCKET"'/scripts/etl/etl.py","s3://'"$BUCKET"'/raw/","s3://'"$BUCKET"'/trusted/"]' \
    'Type=Spark,Name=REFINED_JSON,ActionOnFailure=CANCEL_AND_WAIT,Args=["s3://'"$BUCKET"'/scripts/refined/refined.py","s3://'"$BUCKET"'/trusted/","s3://'"$BUCKET"'/refined/"]' \
    'Type=CUSTOM_JAR,Name=PUBLISH_JSON,ActionOnFailure=CANCEL_AND_WAIT,Jar=command-runner.jar,Args=["bash","-c","JSON_KEY=$(aws s3 ls s3://'"$BUCKET"'/refined/json/ --recursive | head -n1 | awk '\''{print \$4}'\''); aws s3 cp s3://'"$BUCKET"'/\$JSON_KEY s3://'"$BUCKET"'/refined/summary.json; URL=$(aws s3 presign s3://'"$BUCKET"'/refined/summary.json --expires-in 604800); echo \"\$URL\" > /tmp/summary_json_url.txt; aws s3 cp /tmp/summary_json_url.txt s3://'"$BUCKET"'/refined/summary_json_url.txt"]' \
    --query StepIds --output text
)

echo "   StepIds añadidos: $STEP_IDS"

###############################################################################
# 3) ESPERAR A QUE TERMINE EL ÚLTIMO STEP (PUBLISH_JSON)
PUBLISH_STEP_ID=$(echo "$STEP_IDS" | awk '{print $NF}')
echo "3) Esperando a que el step $PUBLISH_STEP_ID finalice…"
aws emr wait step-complete --cluster-id "$CLUSTER_ID" --step-id "$PUBLISH_STEP_ID" || {
  echo "✖ El step $PUBLISH_STEP_ID finalizó con errores. Detalles:"
  aws emr describe-step --cluster-id "$CLUSTER_ID" --step-id "$PUBLISH_STEP_ID" \
    --query "Step.Status" --output table
  exit 1
}

###############################################################################
# 4) RESULTADO: IMPRIMIR LA URL PRE-FIRMADA
echo "✔ Pipeline completado. URL pre-firmada (válida 7 días):"
aws s3 cp s3://$BUCKET/refined/summary_json_url.txt -
echo ""

