variable "aws_region" {
    type = string
    default = "us-east-2"
}

variable "vpc_id" {type = string}

variable "subnet_1_id" {type = string}

variable "subnet_2_id" {type = string}

variable "subnet_3_id" {type = string}

variable "route_table_id" {type = string}

variable "security_group_id" {type = string}

variable "domain_bucket" {type = string}

variable "mlflow_uri" {type = string}

variable "domain_name" {type = string}

variable "cf_domain" {type = string}

variable "repo_uri" {type = string}

variable "my_ip" {type = string}

variable "instance_type" {
    type = string
    default = "t4g.medium"
}