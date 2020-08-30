variable "AI_ACCESS_TOKEN" {
  description = "ai dungeon access token"
  default = ""
}


locals {
  variables = {
    SessionDB = aws_dynamodb_table.session.name
    SceneDB = aws_dynamodb_table.scene.name
    AI_ACCESS_TOKEN = var.AI_ACCESS_TOKEN
    CHALICE_STAGE = data.null_data_source.chalice.inputs.stage
  }
}