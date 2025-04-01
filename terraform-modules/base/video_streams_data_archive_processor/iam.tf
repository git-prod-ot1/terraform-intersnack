resource "aws_iam_role" "video_processor_role" {
  name = "${local.company_name_prefix}_video_processor_role"

  assume_role_policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Action" : "sts:AssumeRole",
          "Principal" : {
            "Service" : "lambda.amazonaws.com"
          },
          "Effect" : "Allow",
          "Sid" : ""
        }
      ]
    }
  )
}

resource "aws_iam_role_policy_attachment" "policy_for_video_processor" {
  policy_arn = aws_iam_policy.video_processor_policy.arn
  role       = aws_iam_role.video_processor_role.name
}

resource "aws_iam_role_policy_attachment" "cloudwatch_for_lambda" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.video_processor_role.name
}

resource "aws_iam_policy" "video_processor_policy" {
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:ChangeMessageVisibility",
          "sqs:ListQueues",
          "sqs:GetQueueAttributes",
        ],
        "Resource" : aws_sqs_queue.videostreams_tasks_queue.arn
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "kinesis:PutRecord",
          "kinesis:PutRecords"
        ],
        "Resource" : "*"
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "s3:Put*",
          "s3:List*",
        ],
        "Resource" : "*"
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem",
          "dynamodb:BatchGetItem",
          "dynamodb:DescribeTable",
          "dynamodb:ListTables",
        ],
        "Resource" : aws_dynamodb_table.videostreams_tasks_table.arn
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "kinesisvideo:Describe*",
          "kinesisvideo:Get*",
          "kinesisvideo:List*"
        ],
        "Resource" : "*"
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "firehose:PutRecord"
        ],
        "Resource" : "*"
      }
    ]
  })
}
