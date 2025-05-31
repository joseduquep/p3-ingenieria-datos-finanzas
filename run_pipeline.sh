#!/usr/bin/env bash
###############################################################################
# run_pipeline.sh · Añade los 3 steps con un JSON seguro
###############################################################################

BUCKET=juanzuluaga-proyecto3
CLUSTER_ID=j-2JIDZVMMKY5VX

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
INGEST_PY="$SCRIPT_DIR/ingest_to_raw.py"

###############################################################################
# 1) INGESTA RAW
echo "1) Ingesta RAW …"
python3 "$INGEST_PY" || { echo "✖ Falló ingest_to_raw.py"; exit 1; }
echo "✔ Ingesta RAW completada."

###############################################################################
# 2) Crear steps.json seguro (SIN escapes de más)
TMP_JSON=$(mktemp /tmp/steps-XXXX.json)

cat > "$TMP_JSON" <<EOF
[
  {
    "Type": "Spark",
    "Name": "ETL_RAW_TO_TRUSTED",
    "ActionOnFailure": "CANCEL_AND_WAIT",
    "Args": [
      "s3://$BUCKET/scripts/etl/etl.py",
      "s3://$BUCKET/raw/",
      "s3://$BUCKET/trusted/"
    ]
  },
  {
    "Type": "Spark",
    "Name": "REFINED_JSON",
    "ActionOnFailure": "CANCEL_AND_WAIT",
    "Args": [
      "s3://$BUCKET/scripts/refined/refined.py",
      "s3://$BUCKET/trusted/",
      "s3://$BUCKET/refined/"
    ]
  },
  {
    "Type": "CUSTOM_JAR",
    "Name": "PUBLISH_JSON",
    "Jar": "command-runner.jar",
    "ActionOnFailure": "CANCEL_AND_WAIT",
    "Args": [
      "bash", "-c",
      "set -e; JSON_KEY=\$(aws s3 ls s3://$BUCKET/refined/ --recursive | grep '.json$' | head -n1 | awk '{print \$4}'); aws s3 cp s3://$BUCKET/\$JSON_KEY s3://$BUCKET/refined/summary.json; URL=\$(aws s3 presign s3://$BUCKET/refined/summary.json --expires-in 604800); echo \$URL > /tmp/summary_json_url.txt; aws s3 cp /tmp/summary_json_url.txt s3://$BUCKET/refined/summary_json_url.txt"
    ]
  }
]
EOF

echo "2) Añadiendo steps al clúster $CLUSTER_ID…"
STEP_IDS=$(aws emr add-steps \
             --cluster-id "$CLUSTER_ID" \
             --steps file://"$TMP_JSON" \
             --query 'StepIds' --output text)
echo "   StepIds: $STEP_IDS"
rm -f "$TMP_JSON"

###############################################################################
# 3) ESPERAR AL ÚLTIMO STEP (PUBLISH_JSON)
LAST_STEP=$(echo "$STEP_IDS" | awk '{print $NF}')
echo "3) Esperando a que el step $LAST_STEP finalice…"
aws emr wait step-complete --cluster-id "$CLUSTER_ID" --step-id "$LAST_STEP" || {
  echo "✖ El step $LAST_STEP finalizó con errores:"
  aws emr describe-step --cluster-id "$CLUSTER_ID" --step-id "$LAST_STEP" \
        --query "Step.Status" --output table
  exit 1
}

###############################################################################
# 4) MOSTRAR URL PRE-FIRMADA
echo "✔ Pipeline completo. URL pre-firmada (7 días):"
aws s3 cp "s3://$BUCKET/refined/summary_json_url.txt" -
echo ""

