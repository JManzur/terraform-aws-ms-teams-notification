resource "aws_sns_topic" "ms_teams_notifications" {
  name              = "MS-Teams-Notification"
  kms_master_key_id = "alias/aws/sns" #tfsec:ignore:aws-sns-topic-encryption-use-cmk
}

resource "aws_sns_topic_subscription" "ms_teams_notifications" {
  topic_arn = aws_sns_topic.ms_teams_notifications.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.ms_teams_notifications.arn
}
