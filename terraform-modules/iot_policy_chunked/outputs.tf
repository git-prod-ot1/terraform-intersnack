output "policies" {
  description = "List of created policy"
  value = concat(
    [for policy in aws_iot_policy.clients : policy],
    [aws_iot_policy.read]
  )
}
