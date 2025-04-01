output "measurement_samples_bucket" {
  value = module.measurement_samples.aws_s3_bucket
}

output "error_bucket" {
  value = module.errors_bucket.aws_s3_bucket
}

output "measurement_samples_glue_table" {
  value = module.measurement_samples_glue.table
}