terraform {
  required_version = ">= 1.6.0"
}

provider "aws" {
  region = "eu-central-1"
}

resource "aws_db_instance" "legacy_postgres" {
  identifier              = "legacy-postgres-demo"
  engine                  = "postgres"
  engine_version          = "14.10"
  instance_class          = "db.t3.micro"
  allocated_storage       = 20
  username                = "postgres"
  password                = "example-password"
  publicly_accessible     = true
  storage_encrypted       = true
  backup_retention_period = 7
  skip_final_snapshot     = true
  performance_insights_enabled = false
}
