output "monitoring_samples_glue_table" {
  value = module.glue.table
}

output "monitoring_samples_bucket" {
  value = module.measurement_samples.aws_s3_bucket
}
