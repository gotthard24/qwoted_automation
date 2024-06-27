terraform {
    required_version = ">= 0.12.0"    
}

provider "aws" {
    region = "us-east-1"
}

provider "aws" {
    alias = "east1"
    region = "us-east-1"
}

module "vpc" {
    source = "terraform-aws-modules/vpc/aws"
    version = "2.9.0"
    
    name = "${var.project}-${terraform.workspace}-vpc"
    cidr = "${var.cidr}"
    azs = "${var.azs}"
    private_subnets = "${var.private_subnets}"
    public_subnets = "${var.public_subnets}"

    enable_nat_gateway = "${var.enable_nat_gateway}"

    tags = {
        Terraform = "true"
        Environment = "${terraform.workspace}"
        Project = "${var.project}"
    }
}
