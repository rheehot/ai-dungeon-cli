variable "AI_ACCESS_TOKEN" {
  description = "ai dungeon access token"
  default = ""
}


locals {
  variables = {
    SessionDB = aws_dynamodb_table.session.name
    PromptDB = aws_dynamodb_table.prompt.name
    AI_ACCESS_TOKEN = var.AI_ACCESS_TOKEN
    CHALICE_STAGE = data.null_data_source.chalice.inputs.stage
  }
}