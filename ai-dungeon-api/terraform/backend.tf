terraform {
  backend "remote" {
    hostname = "app.terraform.io"
    organization = "ai-dungeon-api"

    workspaces {
      prefix = "api_"
    }
  }
}
