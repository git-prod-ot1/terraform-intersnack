resource "aws_iam_role" "iot_role" {
  name               = "${local.name_prefix}_iot"
  assume_role_policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Sid" : "",
          "Effect" : "Allow",
          "Principal" : {
            "Service" : "iot.amazonaws.com"
          },
          "Action" : "sts:AssumeRole"
        }
      ]
    }
  )
}

resource "aws_iam_role_policy_attachment" "AWSIoTThingsRegistration_iot" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSIoTThingsRegistration"
  role       = aws_iam_role.iot_role.name
}

resource "aws_iam_role_policy_attachment" "AWSIoTLogging_iot" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSIoTLogging"
  role       = aws_iam_role.iot_role.name
}
