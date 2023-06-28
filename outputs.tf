output "sns_topic_arn" {
  value       = aws_sns_topic.ms_teams_notifications.arn
  description = "The ARN of the SNS topic for MS Teams notifications"
}