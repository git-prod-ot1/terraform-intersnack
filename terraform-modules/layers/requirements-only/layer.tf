locals {
  source_files         = ["${var.lib_location}/requirements.txt"]
  checksum             = sha1(join("", [for f in local.source_files : filesha1(f)]))
  s3_object_key        = "${var.layer_name}-${local.checksum}"
  default_build_script = <<EOF
      set -e
      cd ${var.lib_location}
      pip3 install --prefer-binary -r requirements.txt -t python
      zip -r ${var.layer_name} python
    EOF
  build_script         = var.build_script == null ? local.default_build_script : var.build_script
}

resource "null_resource" "this" {
  triggers = {
    always = timestamp()
  }
  provisioner "local-exec" {
    interpreter = [
      "bash",
      "-c"
    ]
    command = local.build_script
  }
}

resource "aws_s3_object" "this" {
  bucket     = var.aws_s3_bucket_lambda_layers.bucket
  key        = "${local.s3_object_key}.zip"
  source     = "${var.lib_location}/${var.layer_name}.zip"
  depends_on = [
    null_resource.this
  ]
}

resource "aws_lambda_layer_version" "this" {
  layer_name          = var.layer_name
  compatible_runtimes = [
    "python3.9",
    "python3.10",
    "python3.11"

  ]
  s3_bucket = var.aws_s3_bucket_lambda_layers.bucket
  s3_key    = aws_s3_object.this.key
}
