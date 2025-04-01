module "republisher_store" {
  count  = var.republisher_store == null ? 0 : 1
  source = "./republisher_store"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  unit_name         = "${var.republisher_store.factory_short}_re_store"
  region            = var.region

  republished_data_topic = "${var.republish_topic}/republished/#"
  data_stream_shards     = var.republisher_store.data_stream_shards

  measurement_samples_glue_catalog_database = var.republisher_store.measurement_samples_glue_catalog_database
  measurement_samples_bucket                = var.republisher_store.measurement_samples_bucket
  measurement_samples_glue_table            = var.republisher_store.measurement_samples_glue_table
  sns_alarms_recipients                     = var.republisher_store.sns_alarms_recipients
  error_bucket                              = var.republisher_store.error_bucket
  factory_name                              = var.unit_name

  maintenance_tags = var.maintenance_tags
  tags             = local.tags
}
