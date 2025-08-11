import boto3
from botocore.exceptions import ClientError

from src import AppConfig
from src.configs import BusinessLogicConfig

SES_SENDER = AppConfig.AWS_SES_SENDER
SES_REGION = AppConfig.AWS_REGION

email_client = boto3.client('ses', region_name=SES_REGION)


class SimpleEmailService:

    @staticmethod
    def send_email(recipient: str, subject: str, body: str):
        try:
            response = email_client.send_email(
                Source=SES_SENDER,
                Destination={
                    'ToAddresses': [
                        recipient,
                    ],
                },
                Message={
                    'Subject': {
                        'Charset': 'UTF-8',
                        'Data': subject,
                    },
                    'Body': {
                        'Text': {
                            'Charset': 'UTF-8',
                            'Data': body,
                        }
                    },
                },
            )
        except ClientError as e:
            raise Exception("Failed to send email: {}".format(e.response['Error']['Message']))
        else:
            return response['MessageId']

    @staticmethod
    def send_activate_account_link(recipient: str, name: str, link: str):
        subject = 'Activate Your Account'
        body = BusinessLogicConfig.get_register_email_template().format(name=name, link=link)
        return SimpleEmailService.send_email(recipient=recipient, subject=subject, body=body)

    @staticmethod
    def send_reset_password_link(recipient: str, name: str, link: str):
        subject = 'Reset Your Password'
        body = BusinessLogicConfig.get_reset_password_email_template().format(name=name, link=link)
        return SimpleEmailService.send_email(recipient=recipient, subject=subject, body=body)
