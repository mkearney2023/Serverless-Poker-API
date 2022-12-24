terraform {
	required_providers {
		aws = {
			source = "hashicorp/aws"
			version = "~> 4.16"
		}
	}
	required_version = ">= 1.2.0"
}
provider "aws" {
	region = "us-east-1"
}
resource "aws_dynamodb_table" "poker_users" {
	name = "poker_users"
	attribute {
		name = "id"
		type = "S"
	}
	hash_key = "id"
	billing_mode = "PROVISIONED"
	read_capacity = 30
	write_capacity = 30
}
resource "aws_dynamodb_table" "poker_lobbies" {
	name = "poker_lobbies"
	attribute {
		name = "id"
		type = "S"
	}
	hash_key = "id"
	billing_mode = "PROVISIONED"
	read_capacity = 30
	write_capacity = 30
}
resource "aws_dynamodb_table" "poker_debts" {
	name = "poker_debts"
	attribute {
		name = "id"
		type = "S"
	}
	hash_key = "id"
	billing_mode = "PROVISIONED"
	read_capacity = 30
	write_capacity = 30
}
resource "aws_iam_role" "poker" {
	name = "poker"
	assume_role_policy = jsonencode ({
		"Version": "2012-10-17",
		"Statement": [{
			"Action": "sts:AssumeRole",
			"Principal": {
				"Service": "lambda.amazonaws.com"
			},
			"Effect": "Allow",
			"Sid": ""
		}]
	})
}
resource "aws_iam_policy" "poker" {
	name = "poker"
	policy = jsonencode({
		"Version": "2012-10-17",
		"Statement": [{"Effect": "Allow", "Action": ["*"], "Resource": "*"}]
	})
}
resource "aws_iam_role_policy_attachment" "poker" {
	role = "poker"
	policy_arn = aws_iam_policy.poker.arn
	depends_on = [aws_iam_role.poker, aws_iam_policy.poker]
}
data "archive_file" "poker" {
	type = "zip"
	source_dir = "source/lambda"
	output_path = "archive/lambda.zip"
}
resource "aws_lambda_function" "poker" {
	filename = "archive/lambda.zip"
	function_name = "poker"
	role = aws_iam_role.poker.arn
	handler = "controller.lambda_handler"
	runtime = "python3.7"
	source_code_hash = data.archive_file.poker.output_base64sha256
	depends_on = [data.archive_file.poker]
}
resource "aws_api_gateway_rest_api" "poker" {
	name = "poker"
}
data "aws_region" "region" {
}
data "aws_caller_identity" "caller_identity" {
}
resource "aws_lambda_permission" "poker" {
	statement_id = "AllowExecutionFromAPIGateway"
	action = "lambda:InvokeFunction"
	function_name = aws_lambda_function.poker.function_name
	principal = "apigateway.amazonaws.com"
	source_arn = "arn:aws:execute-api:${data.aws_region.region.name}:${data.aws_caller_identity.caller_identity.account_id}:${aws_api_gateway_rest_api.poker.id}/*"
}
resource "aws_api_gateway_resource" "proxy" {
	parent_id = aws_api_gateway_rest_api.poker.root_resource_id
	path_part = "{proxy+}"
	rest_api_id = aws_api_gateway_rest_api.poker.id
}
resource "aws_api_gateway_method" "proxy" {
	authorization = "NONE"
	http_method = "ANY"
	resource_id = aws_api_gateway_resource.proxy.id
	rest_api_id = aws_api_gateway_rest_api.poker.id
}
resource "aws_api_gateway_integration" "proxy" {
	rest_api_id = aws_api_gateway_rest_api.poker.id
	resource_id = aws_api_gateway_resource.proxy.id
	http_method = "ANY"
	integration_http_method = "POST"
	type = "AWS_PROXY"
	uri = aws_lambda_function.poker.invoke_arn
}
resource "aws_api_gateway_deployment" "poker" {
	rest_api_id = aws_api_gateway_rest_api.poker.id
	triggers = {
		redeployment = sha1(jsonencode([
			aws_api_gateway_resource.proxy.id,
			aws_api_gateway_method.proxy.id,
			aws_api_gateway_integration.proxy.id,
		]))
	}
}
resource "aws_api_gateway_stage" "poker" {
	deployment_id = aws_api_gateway_deployment.poker.id
	rest_api_id = aws_api_gateway_rest_api.poker.id
	stage_name = "v1"
}
resource "local_file" "url" {
	content = aws_api_gateway_stage.poker.invoke_url
	filename = "url"
}
