# terraform/backend.tf
terraform {
  backend "s3" {
    bucket         = "terraform-state-20250610"  # Replace with your S3 bucket
    key            = "passport_verification/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"         # Replace with your DynamoDB table
  }
}


