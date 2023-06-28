#Encrypted string using default SSM KMS key
resource "aws_ssm_parameter" "ms_teams_webhook_url" {
  name        = "/ms-teams/webhook_url"
  description = "MS Teams Webhook URL"
  type        = "SecureString"
  value       = var.webhook_url

  tags = { Name = "MS-Teams-Webhook-URL" }
}