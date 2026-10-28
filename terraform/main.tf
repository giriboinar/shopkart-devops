# ShopKart EKS infrastructure — SIMULATION / NOT APPLIED.
#
# This Terraform defines a VPC across 3 availability zones and an EKS
# cluster, exactly as the portfolio description states. It is NOT applied:
# EKS and managed node groups are paid AWS services, this project has no
# AWS credentials, and the author's constraint is Free Tier only. Running
# `terraform apply` here would create real, billable resources — do not
# run it without explicit approval and a cost check. The runnable path
# for this repo is the local kind cluster (see README).
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
  # No credentials are stored in this repo. If this is ever applied,
  # credentials must come from the environment / a secure profile.
}

resource "aws_vpc" "shopkart" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  tags = { Name = "shopkart-simulation" }
}

resource "aws_subnet" "shopkart" {
  count                   = 3
  vpc_id                  = aws_vpc.shopkart.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true
  tags = { Name = "shopkart-simulation-${count.index}" }
}

resource "aws_internet_gateway" "shopkart" {
  vpc_id = aws_vpc.shopkart.id
  tags   = { Name = "shopkart-simulation" }
}

resource "aws_eks_cluster" "shopkart" {
  name     = "shopkart-simulation"
  role_arn = var.eks_role_arn
  vpc_config {
    subnet_ids = aws_subnet.shopkart[*].id
  }
  # NOTE: node groups / Fargate profiles intentionally omitted — this
  # file documents the intended production shape; it is not a
  # ready-to-apply production deployment.
}
