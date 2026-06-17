#!/bin/bash
# Teardown VPC Endpoints for KPI Demo VPC (SageMaker Unified Studio)
#
# Account: 922850913962
# Region: eu-west-1
# VPC: vpc-0dbd787844fe0861e (D55-kpidemo-financials-dev-vpc)
#
# Removes all Interface VPC endpoints from the KPI Demo VPC.
# Saves ~$154/month. Studio will NOT work until endpoints are reprovisioned.
#
# Usage: ./teardown-kpidemo-vpc-endpoints.sh [profile]
# Example: ./teardown-kpidemo-vpc-endpoints.sh d55-demo

set -euo pipefail

PROFILE="${1:-d55-demo}"
REGION="eu-west-1"
VPC_ID="vpc-0dbd787844fe0861e"

echo "Finding Interface VPC endpoints in KPI Demo VPC..."

ENDPOINT_IDS=$(aws ec2 describe-vpc-endpoints \
  --profile "${PROFILE}" \
  --region "${REGION}" \
  --filters "Name=vpc-id,Values=${VPC_ID}" "Name=vpc-endpoint-type,Values=Interface" \
  --query "VpcEndpoints[].VpcEndpointId" \
  --output text)

if [ -z "${ENDPOINT_IDS}" ]; then
  echo "No Interface endpoints found. Nothing to do."
  exit 0
fi

echo "Found endpoints: ${ENDPOINT_IDS}"
echo ""
echo "Deleting..."

aws ec2 delete-vpc-endpoints \
  --vpc-endpoint-ids ${ENDPOINT_IDS} \
  --profile "${PROFILE}" \
  --region "${REGION}" \
  --output json

echo ""
echo "All Interface VPC endpoints deleted. Saving ~\$154/month."
echo "Run reprovision-kpidemo-vpc-endpoints.sh before the next demo."
