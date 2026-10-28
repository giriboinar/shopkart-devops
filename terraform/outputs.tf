output "vpc_id" {
  value = aws_vpc.shopkart.id
}

output "subnet_ids" {
  value = aws_subnet.shopkart[*].id
}

output "eks_cluster_name" {
  value = aws_eks_cluster.shopkart.name
}
