output "endpoint_url" {
  value = aws_elastic_beanstalk_environment.this.endpoint_url
}

output "environment_security_group_id" {
  value = aws_security_group.env.id
}

