resource "aws_ce_cost_allocation_tag" "company" {
  provider = aws.billing
  tag_key = "company"
  status  = "Active"
}

resource "aws_ce_cost_allocation_tag" "unit" {
  provider = aws.billing
  tag_key = "unit"
  status  = "Active"
}

resource "aws_ce_cost_allocation_tag" "factory" {
  provider = aws.billing
  tag_key = "factory"
  status  = "Active"
}

resource "aws_ce_cost_allocation_tag" "environment" {
  provider = aws.billing
  tag_key = "environment"
  status  = "Active"
}
