import boto3
import urllib3, json, os, logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("Event: {}".format(event))
    try:
        Message = json.loads(event["Records"][0]["Sns"]["Message"])
        NewStateValue = Message["NewStateValue"]
        AlarmName = Message["AlarmName"]
        AlarmDescription = Message["AlarmDescription"]
        NewStateReason = Message["NewStateReason"]
        AWSAccountId = Message["AWSAccountId"]
        Region = Message["Region"]
        StateChangeTime = Message["StateChangeTime"]
        AlarmArn = Message["AlarmArn"]

        message = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "contentUrl": None,
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.3",
                        "body": [
                            {
                                "type": "Container",
                                "padding": "None",
                                "items": [
                                    {
                                        "type": "TextBlock",
                                        "wrap": True,
                                        "size": "Large",
                                        "color": "{}".format(get_color(NewStateValue)),
                                        "text": "{} {}: {}".format(get_emoji(NewStateValue), NewStateValue, AlarmName)
                                    }
                                ]
                            },
                            {
                                "type": "Container",
                                "items": [
                                    {
                                        "type": "TextBlock",
                                        "text": "{}".format(AlarmDescription),
                                        "wrap": True
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": "{}".format(NewStateReason),
                                        "wrap": True
                                    }
                                ],
                                "isVisible": False,
                                "id": "alarm-details"
                            },
                            {
                                "type": "Container",
                                "padding": "None",
                                "items": [
                                    {
                                        "type": "ColumnSet",
                                        "columns": [
                                            {
                                                "type": "Column",
                                                "width": "stretch",
                                                "items": [
                                                    {
                                                        "type": "TextBlock",
                                                        "text": "Account",
                                                        "wrap": True,
                                                        "isSubtle": True,
                                                        "weight": "Bolder"
                                                    },
                                                    {
                                                        "type": "TextBlock",
                                                        "wrap": True,
                                                        "spacing": "Small",
                                                        "text": "{}".format(AWSAccountId)
                                                    }
                                                ]
                                            },
                                            {
                                                "type": "Column",
                                                "width": "stretch",
                                                "items": [
                                                {
                                                    "type": "TextBlock",
                                                    "text": "Region",
                                                    "wrap": True,
                                                    "isSubtle": True,
                                                    "weight": "Bolder"
                                                },
                                                {
                                                    "type": "TextBlock",
                                                    "text": "{}".format(Region),
                                                    "wrap": True,
                                                    "spacing": "Small"
                                                }
                                                ]
                                            },
                                            {
                                                "type": "Column",
                                                "width": "stretch",
                                                "items": [
                                                {
                                                    "type": "TextBlock",
                                                    "text": "UTC Time",
                                                    "wrap": True,
                                                    "weight": "Bolder",
                                                    "isSubtle": True
                                                },
                                                {
                                                    "type": "TextBlock",
                                                    "text": "{}".format(get_date(StateChangeTime)),
                                                    "wrap": True,
                                                    "spacing": "Small"
                                                }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            }
                        ],
                        "padding": "None",
                        "actions": [
                            {
                                "type": "Action.ToggleVisibility",
                                "title": "Show Details",
                                "targetElements": [
                                "alarm-details"
                                ]
                            },
                            {
                                "type": "Action.OpenUrl",
                                "title": "View in CloudWatch",
                                "url": "{}".format(get_alarm_url(AlarmName, AlarmArn))
                            }
                        ]
                    }
                }
            ]
        }
        
        post_message(message)

    except Exception as error:
        #Log the Error:
        logger.error(error)

        #Lambda error response:
        return {
            'statusCode': 400,
            'message': 'An error has occurred',
            'moreInfo': {
                'Lambda Request ID': '{}'.format(context.aws_request_id),
                'CloudWatch log stream name': '{}'.format(context.log_stream_name),
                'CloudWatch log group name': '{}'.format(context.log_group_name)
                }
            }

def get_emoji(NewStateValue):
    checkmarkbutton = "\U00002705"
    policecarsrevolvinglight = "\U0001F6A8"
    warning = "\U000026A0"

    if NewStateValue == "OK":
        return checkmarkbutton
    elif NewStateValue == "ALARM":
        return policecarsrevolvinglight
    elif NewStateValue == "INSUFFICIENT_DATA":
        return warning

def get_color(NewStateValue):
    if NewStateValue == "OK":
        return "Good"
    elif NewStateValue == "ALARM":
        return "Attention"
    elif NewStateValue == "INSUFFICIENT_DATA":
        return "Warning"

def get_alarm_url(AlarmName, AlarmArn):
    RegionCode = AlarmArn.split(":")[3]
    alarm_url = "https://{0}.console.aws.amazon.com/cloudwatch/home?region={0}#alarmsV2:alarm/{1}?".format(RegionCode, AlarmName)
    
    return alarm_url

def get_date(StateChangeTime):
    time_aws = StateChangeTime.split(".")[0]
    utc_time = datetime.strptime(time_aws, "%Y-%m-%dT%H:%M:%S")
    formated_date = utc_time.strftime("%m/%d/%Y %H:%M:%S")

    return formated_date

def post_message(message):
	http = urllib3.PoolManager()
	url = get_parameter()
	encoded_msg = json.dumps(message).encode("utf-8")
	response = http.request("POST", url, body=encoded_msg)

	return {
		"Message": message,
		"StatusCode": response.status,
		"Response": response.data
		}

def get_parameter():
    client = boto3.client('ssm')
    response = client.get_parameter(
        Name='{}'.format(os.environ.get("ms_teams_webhook_url")),
        WithDecryption=True
        )

    return response['Parameter']['Value']