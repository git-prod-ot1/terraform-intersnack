resource "local_file" "this" {
  count    = var.local_secrets ? 1 : 0
  filename = "${path.root}/secrets/${local.name_prefix}.json"

  content = jsonencode(
    {
      "topic" : local.data_topic_name,
      "clientId" : aws_iot_thing.this[0].name,
      "url" : data.aws_iot_endpoint.default.endpoint_address,
      "cert" : aws_iot_certificate.this.certificate_pem,
      "privateKey" : aws_iot_certificate.this.private_key
    }
  )
}
