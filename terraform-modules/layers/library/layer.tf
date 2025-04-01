locals {
  checksum = sha1(join("", [for f in var.source_files: filesha1(f)]))
  dir_location = "${var.lib_location}/${var.layer_name}"
  s3_object_key = "${var.layer_name}-${local.checksum}"
}

resource "null_resource" "build_lib" {
  triggers = {
    updated_at=timestamp()
  }
  provisioner "local-exec" {
    interpreter = ["bash","-c"]
    command = <<EOF
      set -e
      cd ${var.lib_location}
      pip3 install -r requirements.txt
      python3 setup.py sdist bdist_wheel
      mkdir -p layer
      cd layer
      pip3 install ../dist/${var.layer_name}-0.1.0-py3-none-any.whl -t python --upgrade
      zip -r ${var.layer_name} python
      rm -rf python
    EOF
  }
}

resource "aws_s3_bucket_object" "this" {
  bucket = var.aws_s3_bucket_lambda_layers.bucket
  key = "${local.s3_object_key}.zip"
  source = "${var.lib_location}/layer/${var.layer_name}.zip"
  depends_on = [null_resource.build_lib]
}

resource "aws_lambda_layer_version" "this" {
  layer_name = var.layer_name
  compatible_runtimes = ["python3.9", "python3.10", "python3.11"]
  s3_bucket = var.aws_s3_bucket_lambda_layers.id
  s3_key = aws_s3_bucket_object.this.key
}
