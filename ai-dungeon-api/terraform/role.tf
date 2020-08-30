resource "aws_iam_policy" "lambda_policy" {
  name        = "ai_dungeon_${data.null_data_source.chalice.inputs.stage}"
  description = "ai_dungeon lambda resource access policy"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "dynamodb:*",
        "cloudwatch:*",
        "events:*"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "test-attach" {
  role       = aws_iam_role.default-role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}