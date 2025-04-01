locals {
  bucket_name = coalesce(var.bucket_name_override, "${local.name_prefix_dashed}-${var.bucket_name}")
  policies    = concat(
    var.use_ssl ? [
      {
        Sid       = "AllowSSLRequestsOnly"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource  = [
          "${aws_s3_bucket.this.arn}/*",
          aws_s3_bucket.this.arn,
        ]
        Condition = {
          Bool = {
            "aws:SecureTransport" = "false"
          }
        }
      }
    ] : [],
    var.bucket_policy_statements
  )
}

resource "aws_s3_bucket" "this" {
  bucket = local.bucket_name
  tags   = merge(
    local.tags.default,
    try(local.tags.typed["aws_s3_bucket"], {}),
    try(local.tags.named["aws_s3_bucket"][local.bucket_name], {})
  )
}

resource "aws_s3_bucket_server_side_encryption_configuration" "example" {
  bucket = aws_s3_bucket.this.bucket

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "this" {
  count  = var.block_public_access ? 1 : 0
  bucket = aws_s3_bucket.this.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_policy" "this" {
  bucket = aws_s3_bucket.this.id

  policy = jsonencode({
    Version   = "2012-10-17"
    Id        = "AllowSSLRequestsOnly-POLICY"
    Statement = local.policies
  })
}

resource "aws_s3_bucket_versioning" "this" {
  count  = var.enable_versioning ? 1 : 0
  bucket = aws_s3_bucket.this.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "lifecycle" {
  count  = length(var.bucket_lifecycle_configuration) == 0 ? 0 : 1
  bucket = aws_s3_bucket.this.bucket

  rule {
    id     = "LifecycleRule"
    status = "Enabled"

    dynamic "transition" {
      for_each = var.bucket_lifecycle_configuration
      content {
        storage_class = transition.value.storage_class
        days          = transition.value.transition_time_days
      }
    }
  }
}
