output "timestream_table" {
  #  Left for backwards compatibility
  value = element(local.table_names, length(local.table_names)-1)
}

output "timestream_tables" {
  value = local.table_names
}

output "timestream_lambda" {
  value = module.kinesis2timestream.aws_lambda_function
}
