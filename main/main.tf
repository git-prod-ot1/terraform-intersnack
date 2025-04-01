locals {
  main_maintenance_tags = {
    Company        = "Intersnack"
    Department     = null
    Factory        = "Wevelinghoven"
    CostCenter     = null
    Product        = "Base Module"
    Project        = "PoC data pipelines"
    Process        = "Live"
    ProductOwner   = "Volker Deckers"
    TechnicalOwner = var.TechnicalOwner
    CreatedBy      = var.CreatedBy
  }
}


module "base" {
  source            = "../terraform-modules/base"
  company_namespace = var.company_namespace
  aws_user_id       = var.aws_user_id
  region            = var.region

  layers                              = data.terraform_remote_state.layers.outputs.layers
  grafana_enabled                     = true
  # enable_grafana_networking           = true
  # enable_monitoring                   = true
  enable_video_streams_data_processor = false

  vpc     = var.vpc
  subnets = var.subnets

  glue_schema_columns = [
    {
      name = "datapointid"
      type = "string"
    },
    {
      name = "value"
      type = "string"
    },
    {
      name = "takenat"
      type = "timestamp"
    },
    {
      name = "takenatend"
      type = "timestamp"
    },
    {
      name = "postedat"
      type = "timestamp"
    },
    {
      name = "receivedat"
      type = "timestamp"
    },
    {
      name = "originatedat"
      type = "timestamp"
    },
    {
      name = "hour"
      type = "string"
    },
    {
      name = "invocationid"
      type = "string"
    },
    {
      name = "algorithmversion"
      type = "string"
    },
    {
      name = "processtype"
      type = "string"
    },
    {
      name = "additionaldata"
      type = "string"
    },
    {
      name = "streamid"
      type = "string"
    }
  ]

  sns_alarms_recipients = var.sns_alarms_recipients

  video_feed_s3_lifecycle_configuration = terraform.workspace == "dev" ? [
    {
      storage_class        = "STANDARD_IA"
      transition_time_days = 365
    },
    {
      storage_class        = "GLACIER_IR"
      transition_time_days = 548
    },
    {
      storage_class        = "DEEP_ARCHIVE"
      transition_time_days = 730
    },
  ] : []

  picture_feed_s3_lifecycle_configuration = terraform.workspace == "dev" ? [
    {
      storage_class        = "STANDARD_IA"
      transition_time_days = 365
    },
    {
      storage_class        = "GLACIER_IR"
      transition_time_days = 548
    },
  ] : []

  maintenance_tags = local.main_maintenance_tags
  tags             = local.tags
}


module "republish_reference_settings_bucket" {
  source = "../terraform-modules/s3"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  bucket_name       = "iot-republish-reference-files"
  tags              = local.tags
}


module "wevelinghoven" {
  //  FIXED
  source            = "../terraform-modules/factory"
  base              = module.base.base_outputs
  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  layers = data.terraform_remote_state.layers.outputs.layers

  //  CONFIGURE
  unit_name     = "wevelinghoven"
  factory_short = "wh"
  data_destinations = ["ATHENA", "TIMESTREAM"]
  no_of_things  = 5

  measurement_samples_bucket                = module.base.measurement_samples_bucket
  measurement_samples_glue_catalog_database = module.base.measurement_samples_glue_catalog_database
  measurement_samples_glue_table            = module.base.measurement_samples_glue_table
  sns_alarms_recipients                     = var.sns_alarms_recipients
  iot_error_actions_bucket                  = module.base.iot_error_action_bucket
  errors_bucket_name                        = module.error_data_bucket[0].aws_s3_bucket.bucket


  enable_video_streams_data_dispatcher = false
  video_streams_aws_sqs_queue          = module.base.video_stream_aws_sqs_queue
  video_stream_aws_dynamodb_table      = module.base.video_stream_aws_dynamodb_table

  iot2s3_cloudwatch_alarms_config = {
    datapoints_to_alarm : 2
    evaluation_periods : 3
    period : 5*60
  }


  timestream = {
    partition_field = "deviceNameDummy123"
  }



  maintenance_tags = merge(local.main_maintenance_tags, {
    Factory : "wevelinghoven"
  })

  tags = local.tags



  #   DEBUG
  local_secrets = true
}

module "wevelinghoven_republish" {
  source = "../terraform-modules/republisher"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  unit_name         = "wevelinghoven"
  region            = var.region

  kinesis_data_stream    = module.wevelinghoven.data_stream
  reference_table_bucket = module.republish_reference_settings_bucket.aws_s3_bucket.bucket
  republish_topic        = module.wevelinghoven.aws_iot_data_topic
  layers                 = data.terraform_remote_state.layers.outputs.layers

  maintenance_tags = merge(local.main_maintenance_tags, {
    Factory : "wevelinghoven"
  })

  tags = local.tags
}

resource "aws_s3_object" "wevelinghoven_republish_config" {
  bucket = module.republish_reference_settings_bucket.aws_s3_bucket.bucket
  key    = "wevelinghoven.json"

  content = jsonencode({
    "defaultTopic" : "${module.wevelinghoven.aws_iot_data_topic}/republished/$${datapointid}",
    "republish_all" : false,
    "KS_V26_Rate" : {
      "republish" : true
    }
  })
}
