data "archive_file" "ms_teams_notifications" {
  type        = "zip"
  source_dir  = "${path.module}/lambda_code/"
  output_path = "${path.module}/output_lambda_zip/ms_teams_notifications.zip"
}

resource "aws_lambda_function" "ms_teams_notifications" {
  filename      = data.archive_file.ms_teams_notifications.output_path
  function_name = "MS-Teams-Notifications"
  role          = aws_iam_role.ms_teams_notifications.arn
  handler       = "main_handler.lambda_handler"
  description   = "MS-Teams-Notifications"
  tags          = { Name = "MS-Teams-Notifications" }

  source_code_hash = data.archive_file.ms_teams_notifications.output_path
  runtime          = "python3.9"
  timeout          = "900"

  environment {
    variables = {
      ms_teams_webhook_url = aws_ssm_parameter.ms_teams_webhook_url.name
    }
  }
  tracing_config {
    mode = "Active"
  }
}

resource "aws_lambda_permission" "sns" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ms_teams_notifications.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.ms_teams_notifications.arn
}