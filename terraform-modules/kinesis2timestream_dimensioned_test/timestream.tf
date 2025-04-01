locals {
  create_timestream_db         = var.timestream_db == null && var.timestream_db_name == null ? 1 : 0
  timestream_db                = local.create_timestream_db == 1 ? aws_timestreamwrite_database.this[0] : var.timestream_db
  timestream_db_name           = local.create_timestream_db == 1 ? aws_timestreamwrite_database.this[0].database_name : (var.timestream_db_name != null ? var.timestream_db_name : var.timestream_db.database_name)
  table_prefix                 = var.table_skip_prefix ? var.unit_name : (var.table_prefix_override == null ? local.name_prefix : var.table_prefix_override)
  table_names                  = concat(formatlist("${local.table_prefix}_%s", var.timestream_table_names), var.default_table_name_override == null ? [local.table_prefix] : [var.default_table_name_override])
  custom_retention_in_days     = 29 //TODO: Temp solution manually set by M.P., we need to change it in the future
  custom_retention_timestreams = {
    "dev_plcf_glinojeck_gli_ua_purification_1" : local.custom_retention_in_days,
    "dev_plcf_glinojeck_gli_ua_purification_2" : local.custom_retention_in_days
  }
}

resource "aws_timestreamwrite_database" "this" {
  count         = local.create_timestream_db
  database_name = local.name_prefix
}

resource "aws_timestreamwrite_table" "this" {
  for_each = toset(local.table_names)

  database_name = local.timestream_db_name
  table_name    = each.value

  magnetic_store_write_properties {
    enable_magnetic_store_writes = true
  }

  retention_properties {
    //TODO: Temp solution manually set by M.P., we need to change it in the future
    magnetic_store_retention_period_in_days = lookup(local.custom_retention_timestreams, each.value, var.timestream_magnetic_retention)
    memory_store_retention_period_in_hours = var.timestream_memory_retention
  }

  schema {
    composite_partition_key {
      enforcement_in_record = "REQUIRED"
      name                  = "datapointid"
      type                  = "DIMENSION"
    }
  }
}
