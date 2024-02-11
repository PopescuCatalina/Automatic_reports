import json


class ReportsAggregator:
    def __init__(self, cron_prefix: str, rule_lambda_arn: str, rule_lambda_id: str, cloudwatch_client):
        self._cron_prefix = cron_prefix
        self._rule_lambda_arn = rule_lambda_arn
        self._rule_lambda_id = rule_lambda_id
        self._cloudwatch_client = cloudwatch_client

    @staticmethod
    def _fetch_reports() -> list:
        import os

        reports_directory = "reports/"
        loaded_reports = []

        print(f"# Fetching reports in {reports_directory}")
        for file in os.listdir(reports_directory):
            if file.endswith(".json"):
                file_name_to_read = reports_directory + file
                print(f"# Parsing report: {file_name_to_read}")

                with open(file_name_to_read, 'rU') as f:
                    reader = f.read()
                    report_content = json.loads(reader)
                    loaded_reports.append({
                        "report_name": file.replace(".json", ""),
                        "cron": report_content.get("cron"),
                        "query": report_content.get("query"),
                        "emailSubject": report_content.get("emailSubject"),
                        "emailText": report_content.get("emailText"),
                        "emailTo": report_content.get("emailTo"),
                        "emailCC": report_content.get("emailCC"),
                        "databaseURL": report_content.get("databaseURL"),
                        "databaseUser": report_content.get("databaseUser"),
                        "databasePass": report_content.get("databasePass"),
                        "database": report_content.get("database")
                    })

                print(f"# Successfully parsed report: {file_name_to_read}")

        return loaded_reports

    def _get_active_rules(self):
        print("# We fetch all the active rules in CloudWatch")
        return self._cloudwatch_client.list_rules()

    def _delete_actual_rules(self):
        existent_rules = self._get_active_rules()

        print("# We delete every existent active rule")
        for rule in existent_rules.get("Rules"):
            print(f'# [Rule {rule.get("Name")}] Check if the current rule contains the application prefix')
            targets = self._cloudwatch_client.list_targets_by_rule(
                Rule=rule.get("Name")
            )

            if list(filter(rule.get("Name").startswith, [self._cron_prefix])):
                print(f'# [Rule {rule.get("Name")}] Fetch all the targets bound to the rule')
                rule_targets = [rule.get("Id") for rule in self._cloudwatch_client.list_targets_by_rule(
                    Rule=rule.get("Name")
                ).get("Targets")]

                print(f'# [Rule {rule.get("Name")}] We remove targets only if there is any')
                if len(rule_targets):
                    print(f'# [Rule {rule.get("Name")}] Found {len(rule_targets)} targets')
                    print(rule_targets)
                    self._cloudwatch_client.remove_targets(
                        Rule=rule.get("Name"),
                        Ids=rule_targets
                    )

                print(f'# [Rule {rule.get("Name")}] Deleting rule')
                self._cloudwatch_client.delete_rule(
                    Name=rule.get("Name"),
                    Force=True
                )

    def _create_reports_rules(self):
        active_reports = self._fetch_reports()

        for report in active_reports:
            rule_name = f'{self._cron_prefix}{report.get("report_name")}'

            print(f'# [Rule {rule_name}] We persist the rule in CloudWatch with expression: {report.get("cron")}')
            self._cloudwatch_client.put_rule(
                Name=rule_name,
                ScheduleExpression=f'cron({report.get("cron")})',
                State='ENABLED'
            )

            print(f'# [Rule {rule_name}] We bind the rule to the target [Arn: {self._rule_lambda_arn}')
            self._cloudwatch_client.put_targets(
                Rule=rule_name,
                Targets=[
                    {
                        "Id": self._rule_lambda_id,
                        "Arn": self._rule_lambda_arn,
                        "Input": json.dumps(report)
                    }
                ]
            )

        return self._get_active_rules()

    def deploy_rules(self):
        self._delete_actual_rules()
        self._create_reports_rules()
