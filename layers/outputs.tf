output "layers" {
  value = merge({
    pyarrow_alpine = module.pyarrow.aws_lambda_layer_version,
  }, module.layers.layers)
}
