terraform {
    required_providers {
        aws = {
            source = "hashicorp/aws"
            version = "~> 5"
        }
    }
    required_version = ">= 1.2"
}

provider "aws" {
    region = var.aws_region
}

provider "aws" {
    alias = "us-east-1"
    region = "us-east-1"
}

locals {
    domains = [var.domain_name, "www.${var.domain_name}"]
    subnet_ids = [var.subnet_1_id, var.subnet_2_id, var.subnet_3_id]
}

data "aws_acm_certificate" "cf_cert" {
    provider = aws.us-east-1
    domain = var.domain_name
    statuses = ["ISSUED"]
}

data "aws_acm_certificate" "api_cert" {
    domain = var.domain_name
    statuses = ["ISSUED"]
}

data "aws_s3_bucket" "website" {
    bucket = var.domain_bucket
}

data "aws_ecr_image" "image" {
    repository_name = "fashion/backend"
    image_tag = "latest"
}

resource "aws_cloudfront_origin_access_control" "website" {
    name = "website-oac"
    origin_access_control_origin_type = "s3"
    signing_behavior = "always"
    signing_protocol = "sigv4"
}

resource "aws_wafv2_web_acl" "cloudfront" {
    provider = aws.us-east-1
    name = "cloudfront-web-acl"
    scope = "CLOUDFRONT"

    visibility_config {
        cloudwatch_metrics_enabled = false
        metric_name = "cf-metric"
        sampled_requests_enabled = false
    }

    default_action {
        allow {}
    }
}

resource "aws_cloudfront_distribution" "website" {
    aliases = local.domains
    enabled = true
    is_ipv6_enabled = true
    web_acl_id = aws_wafv2_web_acl.cloudfront.arn
    default_root_object = "index.html"

    origin {
        domain_name = data.aws_s3_bucket.website.bucket_regional_domain_name
        origin_id = "s3-website"
        origin_access_control_id = aws_cloudfront_origin_access_control.website.id
    }

    default_cache_behavior {
        allowed_methods = ["GET", "HEAD", "OPTIONS"]
        cached_methods = ["GET", "HEAD"]
        target_origin_id = "s3-website"

        cache_policy_id = "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"
        viewer_protocol_policy = "redirect-to-https"
    }

    ordered_cache_behavior {
        path_pattern = "/assets/*"
        allowed_methods = ["GET", "HEAD"]
        cached_methods = ["GET", "HEAD"]

        cache_policy_id = "658327ea-f89d-4fab-a63d-7e88639e58f6"

        target_origin_id = "s3-website"
        viewer_protocol_policy = "redirect-to-https"
    }

    ordered_cache_behavior {
        path_pattern = "*.svg"
        allowed_methods = ["GET", "HEAD"]
        cached_methods = ["GET", "HEAD"]

        cache_policy_id = "658327ea-f89d-4fab-a63d-7e88639e58f6"

        target_origin_id = "s3-website"
        viewer_protocol_policy = "redirect-to-https"
    }    

    viewer_certificate {
        acm_certificate_arn = data.aws_acm_certificate.cf_cert.arn
        ssl_support_method = "sni-only"
    }

    custom_error_response {
        error_code         = 403
        response_code      = 200
        response_page_path = "/index.html"
    }

    custom_error_response {
        error_code         = 404
        response_code      = 200
        response_page_path = "/index.html"
    }

    restrictions {
        geo_restriction {
            restriction_type = "none"
            locations = []
        }
    } 
}

resource "aws_security_group" "lambda-sg" {
    vpc_id = var.vpc_id
}

resource "aws_vpc_security_group_egress_rule" "lambda" {
    security_group_id = aws_security_group.lambda-sg.id
    cidr_ipv4 = "0.0.0.0/0"
    ip_protocol = -1
}

data "aws_route53_zone" "my_domain" {
    name = var.domain_name
}

resource "aws_route53_record" "cloudfront" {
    for_each = aws_cloudfront_distribution.website.aliases
    zone_id = data.aws_route53_zone.my_domain.zone_id
    name = each.value
    type = "A"

    alias {
        name = aws_cloudfront_distribution.website.domain_name
        zone_id = aws_cloudfront_distribution.website.hosted_zone_id
        evaluate_target_health = false
    }
}

resource "aws_iam_role" "lambda" {
    name = "lambda"

    assume_role_policy = jsonencode({
        Version = "2012-10-17"
        Statement = [{
            Effect = "Allow"
            Action = "sts:AssumeRole"
            Principal = {Service = "lambda.amazonaws.com"}
        }]
    })
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
    role = aws_iam_role.lambda.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_vpc_attachment" {
    role       = aws_iam_role.lambda.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_cloudwatch_log_group" "lambda_api" {
    name = "/aws/lambda/api"
    retention_in_days = 30
}

resource "aws_lambda_function" "fastapi_lambda" {
    function_name = "backend_function"
    role = aws_iam_role.lambda.arn
    image_uri = data.aws_ecr_image.image.image_uri
    package_type = "Image"
    source_code_hash = trimprefix(data.aws_ecr_image.image.id, "sha256:")
    memory_size = 2048
    timeout = 60

    environment {
        variables = {
            ALLOWED_ORIGINS = "https://${var.domain_name}"
            MLFLOW_TRACKING_URI = var.mlflow_uri
        }
    }

    image_config {
        command = ["main.ping_handler"]
    }
    
    vpc_config {
        security_group_ids = [aws_security_group.lambda-sg.id]
        subnet_ids = local.subnet_ids
    }

    depends_on = [ 
        aws_iam_role_policy_attachment.lambda_logs,
        aws_cloudwatch_log_group.lambda_api
    ]   
}

resource "aws_api_gateway_rest_api" "rest_api" {
    name = "my_rest_api"

    endpoint_configuration {
        types = ["REGIONAL"]
        ip_address_type = "ipv4"
    }
}

resource "aws_api_gateway_domain_name" "domain" {
    domain_name = var.domain_name
    regional_certificate_arn = data.aws_acm_certificate.api_cert.arn

    endpoint_configuration {
        types = ["REGIONAL"]
    }
}

resource "aws_api_gateway_resource" "resource" {
    rest_api_id = aws_api_gateway_rest_api.rest_api.id
    path_part = "predict"
    parent_id = aws_api_gateway_rest_api.rest_api.root_resource_id
}


resource "aws_api_gateway_method" "options" {
    resource_id = aws_api_gateway_resource.resource.id
    authorization = "NONE"
    rest_api_id = aws_api_gateway_rest_api.rest_api.id
    http_method = "OPTIONS"
}

resource "aws_api_gateway_method" "lambda" {
    resource_id = aws_api_gateway_resource.resource.id
    authorization = "NONE"
    rest_api_id = aws_api_gateway_rest_api.rest_api.id
    http_method = "POST"
}

resource "aws_api_gateway_method_response" "options" {
    rest_api_id = aws_api_gateway_rest_api.rest_api.id
    resource_id = aws_api_gateway_resource.resource.id
    http_method = aws_api_gateway_method.options.http_method
    status_code = "200"

    response_models = {
        "application/json" = "Empty"
    }

    response_parameters = {
        "method.response.header.Access-Control-Allow-Headers" = true
        "method.response.header.Access-Control-Allow-Methods" = true
        "method.response.header.Access-Control-Allow-Origin"  = true
    }
}

resource "aws_api_gateway_integration" "lambda_integration" {
    http_method = aws_api_gateway_method.lambda.http_method
    integration_http_method = "POST"
    type = "AWS_PROXY"
    uri = aws_lambda_function.fastapi_lambda.invoke_arn
    resource_id = aws_api_gateway_resource.resource.id
    rest_api_id = aws_api_gateway_rest_api.rest_api.id
}

resource "aws_api_gateway_integration" "options" {
    http_method = "OPTIONS"
    type = "MOCK"
    resource_id = aws_api_gateway_resource.resource.id
    rest_api_id = aws_api_gateway_rest_api.rest_api.id

    request_templates = {
        "application/json" : "{\"statusCode\": 200}"
    }
}

resource "aws_api_gateway_integration_response" "options" {
    status_code = "200"
    http_method = aws_api_gateway_integration.options.http_method
    resource_id = aws_api_gateway_resource.resource.id
    rest_api_id = aws_api_gateway_rest_api.rest_api.id

    response_parameters = {
        "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
        "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
        "method.response.header.Access-Control-Allow-Origin"  = "'https://${var.domain_name}'"
    }
}

resource "aws_api_gateway_deployment" "rest_api" {
    rest_api_id = aws_api_gateway_rest_api.rest_api.id  

    triggers = {
        redeployment = sha1(jsonencode([
            aws_api_gateway_rest_api.rest_api,
            aws_api_gateway_integration.options,
            aws_api_gateway_integration.lambda_integration]))
    }

    lifecycle {
        create_before_destroy = true
    }
} 

resource "aws_api_gateway_stage" "rest_api" {
    stage_name = "production"
    deployment_id = aws_api_gateway_deployment.rest_api.id
    rest_api_id = aws_api_gateway_rest_api.rest_api.id
}

resource "aws_lambda_permission" "api_permission" {
    statement_id = "APILambdaInvoke"
    action = "lambda:InvokeFunction"
    function_name = aws_lambda_function.fastapi_lambda.function_name
    principal = "apigateway.amazonaws.com"
    source_arn = "${aws_api_gateway_rest_api.rest_api.execution_arn}/*"
}

resource "aws_cloudwatch_event_rule" "ping" {
    name = "PingLambda"
    schedule_expression = "rate(2 minutes)"
}

resource "aws_cloudwatch_event_target" "lambda" {
    rule = aws_cloudwatch_event_rule.ping.name
    arn = aws_lambda_function.fastapi_lambda.arn
}

resource "aws_lambda_permission" "cloudwatch_invoke" {
    statement_id = "EvenLambdaInvoke"
    principal = "events.amazonaws.com"
    function_name = aws_lambda_function.fastapi_lambda.function_name
    action = "lambda:InvokeFunction"
    source_arn = "${aws_cloudwatch_event_rule.ping.arn}"
}