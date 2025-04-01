#!/bin/bash

# Replace with your VPC ID
VPC_ID="vpc-0c9d5b63b2f15a91f"

# Get all subnets for the VPC
SUBNETS=$(aws ec2 describe-subnets \
  --filters "Name=vpc-id,Values=${VPC_ID}" \
  --query "Subnets[*].[SubnetId,AvailabilityZone,CidrBlock,State]" \
  --output json)

# Print table header
printf "| %-12s | %-12s | %-15s | %-10s | %-30s |\n" "SubnetId" "AZ" "CIDR" "State" "Type"
printf "|-%-12s-|-%-12s-|-%-15s-|-%-10s-|-%-30s-|\n" "$(printf -- '-%.0s' {1..12})" "$(printf -- '-%.0s' {1..12})" "$(printf -- '-%.0s' {1..15})" "$(printf -- '-%.0s' {1..10})" "$(printf -- '-%.0s' {1..30})"

# Process each subnet
echo "$SUBNETS" | jq -r '.[] | @sh' | while read -r subnet; do
  # Extract subnet details
  eval "subnet_array=($subnet)"
  SUBNET_ID="${subnet_array[0]}"
  AZ="${subnet_array[1]}"
  CIDR="${subnet_array[2]}"
  STATE="${subnet_array[3]}"

  # Get the route table associated with this subnet
  ROUTE_TABLE_ID=$(aws ec2 describe-route-tables \
    --filters "Name=association.subnet-id,Values=${SUBNET_ID}" \
    --query "RouteTables[0].RouteTableId" \
    --output text 2>/dev/null || echo "None")

  # If no direct association, get the main route table for the VPC
  if [ "$ROUTE_TABLE_ID" == "None" ] || [ -z "$ROUTE_TABLE_ID" ]; then
    ROUTE_TABLE_ID=$(aws ec2 describe-route-tables \
      --filters "Name=vpc-id,Values=${VPC_ID}" "Name=association.main,Values=true" \
      --query "RouteTables[0].RouteTableId" \
      --output text)
  fi

  # Check for Internet Gateway route more explicitly
  HAS_IGW=$(aws ec2 describe-route-tables \
    --route-table-ids "$ROUTE_TABLE_ID" \
    --query "RouteTables[0].Routes[?DestinationCidrBlock=='0.0.0.0/0' && GatewayId!=null && contains(GatewayId, 'igw-')].GatewayId" \
    --output text 2>/dev/null)

  # Determine subnet type and include IGW info
  if [ -n "$HAS_IGW" ]; then
    TYPE="Public (rtb: ${ROUTE_TABLE_ID}, igw: ${HAS_IGW})"
  else
    TYPE="Private (rtb: ${ROUTE_TABLE_ID})"
  fi

  # Print row
  printf "| %-12s | %-12s | %-15s | %-10s | %-30s |\n" "$SUBNET_ID" "$AZ" "$CIDR" "$STATE" "$TYPE"
done
