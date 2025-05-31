#!/usr/bin/env bash
# publish_json.sh: copiar JSON generado y crear pre-signed URL

BUCKET=$1

# 1. Encontrar el primer JSON en refined/json/
JSON_KEY=$(aws s3 ls s3://$BUCKET/refined/json/ --recursive | head -n1 | awk '{print $4}')

# 2. Copiarlo a refined/summary.json
aws s3 cp s3://$BUCKET/$JSON_KEY s3://$BUCKET/refined/summary.json

# 3. Generar URL pre-firmada (7 días = 604800 segundos)
URL=$(aws s3 presign s3://$BUCKET/refined/summary.json --expires-in 604800)

# 4. Guardar la URL en summary_json_url.txt
echo "$URL" > /tmp/summary_json_url.txt
aws s3 cp /tmp/summary_json_url.txt s3://$BUCKET/refined/summary_json_url.txt

