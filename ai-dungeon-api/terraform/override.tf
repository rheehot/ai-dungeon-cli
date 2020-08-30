
resource "aws_lambda_function" "api_handler" {
  environment {
    variables = local.variables
  }
}
