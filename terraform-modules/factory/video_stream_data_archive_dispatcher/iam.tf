resource "aws_iam_role" "video_dispatcher_role" {
  name = "${local.name_prefix}_video_dispatcher_role"

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

resource "aws_iam_role_policy_attachment" "policy_for_video_dispatcher" {
  policy_arn = aws_iam_policy.video_dispatcher_policy.arn
  role       = aws_iam_role.video_dispatcher_role.name
}

resource "aws_iam_role_policy_attachment" "cloudwatch_for_lambda" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.video_dispatcher_role.name
}

resource "aws_iam_policy" "video_dispatcher_policy" {
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : "sqs:SendMessage",
        "Resource" : "arn:aws:sqs:eu-central-1:${var.aws_user_id}:${var.aws_sqs_queue.name}"
      },
      {
        "Effect" : "Allow",
        "Action" : ["kinesis:PutRecord", "kinesis:PutRecords"],
        "Resource" : "*"
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem",
          "dynamodb:BatchGetItem",
          "dynamodb:BatchWriteItem",
          "dynamodb:DescribeTable",
          "dynamodb:ListTables",
        ],
        "Resource" : "arn:aws:dynamodb:eu-central-1:${var.aws_user_id}:table/${var.aws_dynamodb_table.name}"
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "kinesisvideo:Describe*",
          "kinesisvideo:Get*",
          "kinesisvideo:List*"
        ],
        "Resource" : "*"
      }
    ]
  })
}
