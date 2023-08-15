data "archive_file" "lambda_zip"{
    type = "zip"
    source_file = "ce_lambda_slack.py"
    output_path = "ce_lambda_slack.zip"
}

resource "aws_lambda_function" "ce_lambda_slack" {
  function_name    = "ce_lambda_slack"
  runtime          = "python3.9"
  handler          = "ce_lambda_slack.lambda_handler"
  timeout          = 60
  memory_size      = 128
  role             = aws_iam_role.lambda_role.arn
  filename         = data.archive_file.lambda_zip.output_path

}

# Create an IAM role for the Lambda function
resource "aws_iam_role" "lambda_role" {
  name = "lambda_read_send_email_slack"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

# Attach the necessary policies to the IAM role
resource "aws_iam_role_policy_attachment" "lambda_basic_execution_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_policy" "custom_policy_CE" {
  name        = "CustomCostExplorerPolicy"  # Name of the custom policy
  description = "Custom policy for Cost Explorer access"

  # Define the policy document allowing ce:GetCostAndUsage action on all resources
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "ce:GetCostAndUsage",
      "Resource": "*"
    }
  ]
}
EOF
}

# Define a custom IAM policy for additional permissions
resource "aws_iam_policy" "custom_policy" {
  name        = "CombinedLambdaCustomPolicy"
  description = "Custom IAM policy for combined Lambda function"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ses:SendEmail"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}

# Attach the custom policy to the IAM role Cost explorer policy
resource "aws_iam_role_policy_attachment" "cost_explorer_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.custom_policy_CE.arn
}

# Attach the custom policy to the IAM role SES policy
resource "aws_iam_role_policy_attachment" "custom_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.custom_policy.arn
}

resource "aws_iam_role_policy_attachment" "lambda_ses_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSESFullAccess"
}

resource "aws_cloudwatch_event_rule" "lambda-alert" {
  name        = "trigger_lambda"
  description = "Trigger lambda 10 mins regularly for alerting"

  schedule_expression = "rate(2 minutes)"
}

resource "aws_cloudwatch_event_target" "lambda-function" {
  rule      = aws_cloudwatch_event_rule.lambda-alert.name
  target_id = "lambda"
  arn       = aws_lambda_function.ce_lambda_slack.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ce_lambda_slack.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.lambda-alert.arn
  
}

#Create s3 bucket
resource "aws_s3_bucket" "ce_lambda_bucket"{
  bucket = "ce-lambda-bucket"
  acl = "private"
}

# Upload the logo.png file to the S3 bucket
resource "aws_s3_object" "logo"{
  bucket = aws_s3_bucket.ce_lambda_bucket.bucket
  key = "logo.png"
  source = "logo.png"
  acl = "private"
}

# Attach AmazonS3ReadOnlyAccess policy to the IAM Role
resource "aws_iam_role_policy_attachment" "s3_readonly_policy_attachment"{
  role = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}