terraform {
  required_version = ">= 1.6.0"
}

provider "aws" {
  region = "eu-central-1"
}

resource "aws_db_instance" "legacy_postgres2" {
  identifier              = "legacy-postgres-demo"
  engine                  = "postgres"
  engine_version          = "12.4"
  instance_class          = "db.t3.micro"
  allocated_storage       = 20
  username                = "postgres"
  password                = "example-password"
  publicly_accessible     = true
  storage_encrypted       = false
  backup_retention_period = 1
  skip_final_snapshot     = true
  performance_insights_enabled = false
}
