variable "region" {
  description = "AWS region for the (not applied) EKS definition"
  type        = string
  default     = "ap-south-1"
}

variable "vpc_cidr" {
  description = "VPC CIDR for the (not applied) EKS definition"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Exactly 3 AZs, matching the portfolio description"
  type        = list(string)
  default     = ["ap-south-1a", "ap-south-1b", "ap-south-1c"]
}

variable "eks_role_arn" {
  description = "IAM role ARN for EKS (must be supplied at apply time, never committed)"
  type        = string
  default     = ""
}
