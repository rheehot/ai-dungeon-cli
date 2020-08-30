resource "aws_dynamodb_table" "scene" {
  name = "ai-scene-db-${data.null_data_source.chalice.inputs.stage}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key = "name"

  attribute {
    name = "name"
    type = "S"
  }

  tags = {
    Project = "ai-dungeon-api"
  }
}

resource "aws_dynamodb_table" "session" {
  name = "ai-session-db-${data.null_data_source.chalice.inputs.stage}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    Project = "ai-dungeon-api"
  }

}
