locals {
  default_partition_keys = [
    {
      name = "factory"
      type = "string"
    },
    {
      name = "year"
      type = "string"
    },
    {
      name = "month"
      type = "string"
    },
    {
      name = "day"
      type = "string"
    }
  ]
  partition_keys = coalesce(var.partition_keys, local.default_partition_keys)

}

resource "aws_glue_catalog_table" "this" {
  name          = var.table_name
  database_name = var.aws_glue_catalog_database_name

  owner      = "owner"
  parameters = {
    "CrawlerSchemaDeserializerVersion" = "1.0"
    "CrawlerSchemaSerializerVersion"   = "1.0"
    "classification"                   = "orc"
    "compressionType"                  = "none"
    "typeOfData"                       = "file"
  }
  retention  = 0
  table_type = "EXTERNAL_TABLE"

  dynamic "partition_keys" {
    for_each = {for idx, pk in local.partition_keys :  idx => pk}
    content {
      name = partition_keys.value.name
      type = partition_keys.value.type
    }
  }

  storage_descriptor {
    bucket_columns    = []
    compressed        = false
    input_format      = "org.apache.hadoop.hive.ql.io.orc.OrcInputFormat"
    location          = var.s3_location
    number_of_buckets = -1
    output_format     = "org.apache.hadoop.hive.ql.io.orc.OrcOutputFormat"
    parameters        = {
      "CrawlerSchemaDeserializerVersion" = "1.0"
      "CrawlerSchemaSerializerVersion"   = "1.0"
      "classification"                   = "orc"
      "compressionType"                  = "none"
      "typeOfData"                       = "file"
    }
    stored_as_sub_directories = false


    dynamic "columns" {
      for_each = local.glue_schema_columns
      content {
        name       = columns.value["name"]
        type       = columns.value["type"]
        parameters = {}
      }
    }

    ser_de_info {
      name       = "OrcSerDe"
      parameters = {
        "serialization.format" = "1"
      }
      serialization_library = "org.apache.hadoop.hive.ql.io.orc.OrcSerde"
    }
  }

  lifecycle {
    ignore_changes = [
      parameters,
      storage_descriptor[0].parameters,
      storage_descriptor[0].ser_de_info[0]
    ]
  }

}
