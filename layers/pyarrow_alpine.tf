module "pyarrow" {
  source = "../terraform-modules/layers/requirements-only"

  layer_name = "pyarrow"
  lib_location = "./pyarrow"
  aws_s3_bucket_lambda_layers = module.layers.aws_s3_bucket_lambda_layers
  build_script = <<EOF
      set -e
      cd "./pyarrow"
      wget https://files.pythonhosted.org/packages/8b/bd/2fb49a7649095aab6e1f288b0654e68d79cfd232411021f98a8cb3d90140/pyarrow-8.0.0-cp39-cp39-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
      pip3 install pyarrow-8.0.0-cp39-cp39-manylinux_2_17_x86_64.manylinux2014_x86_64.whl -t python
      rm pyarrow-8.0.0-cp39-cp39-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
      pip3 install pandas -t python
      rm -rf python/{__pycache__,easy_install.py,numpy*,pip*,pkg_resources,setuptools*} || true
      zip -r pyarrow.zip python
    EOF
}
