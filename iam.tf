data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

# IAM Policy Source
data "aws_iam_policy_document" "ms_teams_notifications_policy" {
  statement {
    sid    = "CloudWatchAccess"
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*"]
  }

  statement {
    sid    = "GetParameter"
    effect = "Allow"
    actions = [
      "ssm:GetParameters",
      "ssm:GetParameter"
    ]
    resources = ["arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter${aws_ssm_parameter.ms_teams_webhook_url.name}"]
  }

  statement {
    sid    = "KMSDecrypt"
    effect = "Allow"
    actions = [
      "kms:Decrypt"
    ]
    resources = ["arn:aws:kms:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:key/alias/aws/ssm"]
  }
}

data "aws_iam_policy_document" "ms_teams_notifications_assume" {
  statement {
    sid    = "LambdaAssumeRole"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

# IAM Policy
resource "aws_iam_policy" "ms_teams_notifications" {
  name        = "MS-Teams-Notifications-Lambda-Policy"
  path        = "/"
  description = "Permissions to trigger the Lambda"
  policy      = data.aws_iam_policy_document.ms_teams_notifications_policy.json
  tags        = { Name = "MS-Teams-Notifications-Lambda-Policy" }
}

# IAM Role (Lambda execution role)
resource "aws_iam_role" "ms_teams_notifications" {
  name               = "MS-Teams-Notifications-Lambda-Role"
  assume_role_policy = data.aws_iam_policy_document.ms_teams_notifications_assume.json
  tags               = { Name = "MS-Teams-Notifications-Lambda-Role" }
}

# Attach Role and Policy
resource "aws_iam_role_policy_attachment" "ms_teams_notifications" {
  role       = aws_iam_role.ms_teams_notifications.name
  policy_arn = aws_iam_policy.ms_teams_notifications.arn
}