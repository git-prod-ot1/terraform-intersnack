resource "aws_iam_policy" "republish_lambda_policy" {
  name   = "${local.name_prefix}_republisher"
  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Sid" : "",
          "Effect" : "Allow",
          "Action" : [
            "s3:GetObject",
          ],
          "Resource" : [
            "arn:aws:s3:::${var.reference_table_bucket}/${var.unit_name}.json",
          ]
        },
        {
          "Sid" : "",
          "Effect" : "Allow",
          "Action" : [
            "kinesis:GetRecords",
            "kinesis:GetShardIterator",
            "kinesis:DescribeStream",
            "kinesis:ListShards",
            "kinesis:ListStreams",
          ],
          "Resource" : [
            var.kinesis_data_stream.arn,
          ]
        },
        {
          "Effect": "Allow",
          "Action": [
            "iot:Publish"
          ],
          "Resource": [
            "arn:aws:iot:${var.region}:${var.aws_user_id}:topic/${var.republish_topic}",
            "arn:aws:iot:${var.region}:${var.aws_user_id}:topic/${var.republish_topic}/*"
          ]
        },
        {
          "Effect": "Allow",
          "Action": [
            "iot:Connect",
            "iot:DescribeEndpoint"
          ],
          "Resource": [
            "*"
          ]
        }
      ]
    })
}
