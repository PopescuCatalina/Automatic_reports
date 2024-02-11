from modules.ReportsAggregator import ReportsAggregator
from modules.EmailSender import EmailSender
import boto3
import os


# noinspection PyUnusedLocal
def deploy_cron_jobs(events, context):
    Reports = ReportsAggregator(
        cron_prefix=os.environ.get("CRON_PREFIX"),
        rule_lambda_arn=os.environ.get("LAMBDA_ARN"),
        rule_lambda_id=os.environ.get("LAMBDA_ID"),
        cloudwatch_client=boto3.client('events')
    )
    print(Reports.deploy_rules())


# noinspection PyUnusedLocal
def run_cron_jobs(events, context):
    report_instance = EmailSender(
        config=events,
        client=boto3.client('ses'),
        report_file_name=os.environ.get("REPORT_FILE_NAME"),
        temporary_directory_path=os.environ.get("TEMPORARY_DIRECTORY_PATH")
    )
    report_instance.run_sending_report_routine()
