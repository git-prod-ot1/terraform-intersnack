locals {
  # this is for now calculated together with glue/base! do not change
  glue_partitioner_function_name = {
    1 : "${local.company_name_prefix}_glue_partitions_updater",
    2 : "${local.company_name_prefix}_glue_partitions_updater_v2"
  }
  glue_partitioner_function_arn = {
    1 : "arn:aws:lambda:${var.region}:${var.aws_user_id}:function:${local.glue_partitioner_function_name.1}",
    2 : "arn:aws:lambda:${var.region}:${var.aws_user_id}:function:${local.glue_partitioner_function_name.2}"
  }
}

resource "aws_cloudwatch_event_rule" "glue_partitions_updater" {
  name                = var.table_name
  description         = "Triggers search and update of partitions in Glue Table"
  schedule_expression = "rate(1 hour)"
  tags                = local.tags.default
}

resource "aws_cloudwatch_event_target" "this" {
  rule  = aws_cloudwatch_event_rule.glue_partitions_updater.name
  arn   = lookup(local.glue_partitioner_function_arn, var.partitioning_lambda_version, local.glue_partitioner_function_arn.1)
  input = jsonencode(
    {
      glue_database = aws_glue_catalog_table.this.database_name
      glue_table    = aws_glue_catalog_table.this.name
      s3_location   = var.s3_location
    }
  )

}

resource "aws_lambda_permission" "this" {
  action        = "lambda:InvokeFunction"
  function_name = lookup(local.glue_partitioner_function_name, var.partitioning_lambda_version, local.glue_partitioner_function_name.1)
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.glue_partitions_updater.arn
}
