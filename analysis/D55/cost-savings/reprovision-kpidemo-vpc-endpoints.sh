#!/bin/bash
# Reprovision VPC Endpoints for KPI Demo VPC (SageMaker Unified Studio)
#
# Account: 922850913962
# Region: eu-west-1
# VPC: vpc-0dbd787844fe0861e (D55-kpidemo-financials-dev-vpc)
#
# These endpoints are required for SageMaker Unified Studio domains
# running in VpcOnly mode. They were removed to save ~$154/month
# when the demo environment is idle.
#
# NOTE: If endpoints were recently deleted, wait ~60 seconds before running
# this script. The private DNS zones need to fully clear first.
#
# Usage: ./reprovision-kpidemo-vpc-endpoints.sh [profile]
# Example: ./reprovision-kpidemo-vpc-endpoints.sh d55-demo

set -euo pipefail

PROFILE="${1:-d55-demo}"
REGION="eu-west-1"
VPC_ID="vpc-0dbd787844fe0861e"
SUBNETS="subnet-0e425cf7560bbb1d8,subnet-01d5cfc1b17da87a1"
SG_PRIMARY="sg-0f5ea0bae3ac7f873"
SG_STS_EXTRA="sg-00e83cfa2ee44ad69"

# Services to create endpoints for
SERVICES=(
  "com.amazonaws.${REGION}.logs"
  "com.amazonaws.${REGION}.sagemaker.runtime"
  "com.amazonaws.${REGION}.sagemaker.api"
  "com.amazonaws.${REGION}.glue"
  "com.amazonaws.${REGION}.secretsmanager"
  "com.amazonaws.${REGION}.sts"
  "com.amazonaws.${REGION}.ecr.api"
  "com.amazonaws.${REGION}.ecr.dkr"
  "com.amazonaws.${REGION}.ec2"
  "aws.sagemaker.${REGION}.studio"
  "com.amazonaws.${REGION}.datazone"
)

echo "Reprovisioning VPC endpoints for KPI Demo VPC..."
echo "Profile: ${PROFILE}"
echo "Region: ${REGION}"
echo "VPC: ${VPC_ID}"
echo ""

for SERVICE in "${SERVICES[@]}"; do
  echo "Creating endpoint for: ${SERVICE}"

  # STS needs an extra security group
  if [[ "${SERVICE}" == *".sts" ]]; then
    SG_IDS="${SG_PRIMARY},${SG_STS_EXTRA}"
  else
    SG_IDS="${SG_PRIMARY}"
  fi

  aws ec2 create-vpc-endpoint \
    --vpc-id "${VPC_ID}" \
    --vpc-endpoint-type Interface \
    --service-name "${SERVICE}" \
    --subnet-ids ${SUBNETS//,/ } \
    --security-group-ids ${SG_IDS//,/ } \
    --private-dns-enabled \
    --profile "${PROFILE}" \
    --region "${REGION}" \
    --output text \
    --query "VpcEndpoint.VpcEndpointId"

  echo "  Done."
done

echo ""
echo "All endpoints created. SageMaker Unified Studio should be accessible within a few minutes."
