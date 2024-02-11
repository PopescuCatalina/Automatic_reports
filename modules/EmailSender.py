from modules.DatabaseConnection import DatabaseConnector
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


class EmailSender:
    DEFAULT_MAIL_FROM = "noreply@tazz.ro"

    def __init__(self, config, client, report_file_name, temporary_directory_path):
        self._config_data = config
        self._connection = DatabaseConnector().connect(config_data=self._config_data)
        self._temporary_directory_path = temporary_directory_path
        self._report_file_name = report_file_name
        self._report_file = self._temporary_directory_path + self._report_file_name
        self._client = client

    def _send_email(self, message_from, message_to, message, attachment=None):
        if attachment is not None:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition',
                            "attachment; filename= %s" % f'{self._report_file_name}')

            message.attach(part)

        text = message.as_string()

        print(f"# Attempting to send report from {message_from} to {message_to}")
        response = self._client.send_raw_email(
            Source=message_from,
            Destinations=message_to,
            RawMessage={
                'Data': text
            }
        )
        print('# Email successfully sent')

    def _get_email_parameters(self):
        email_parameters = MIMEMultipart()
        email_parameters['From'] = self.DEFAULT_MAIL_FROM
        email_parameters['To'] = self._config_data.get('emailTo')
        email_parameters['Cc'] = self._config_data.get('emailCC')
        email_parameters['Subject'] = self._config_data.get('emailSubject')
        email_parameters.attach(MIMEText(self._config_data.get('emailText'), 'plain'))

        return email_parameters

    def run_sending_report_routine(self):
        import pandas as pd
        print(f"# Executing report {self._report_file}")

        message = self._get_email_parameters()
        message_to = message['To'].split(',')
        message_to = [el.strip() for el in message_to]

        # In case this is not a Health Check Rule only, we will run the normal routine
        if not self._config_data.get('isHealthCheckRule'):
            print("# Building DataFrame using the following query:")
            print(self._config_data.get('query'))

            frame = pd.read_sql_query(self._config_data.get('query'), self._connection)
            pd.set_option('display.expand_frame_repr', False)

            if len(frame) != 0:
                writer = pd.ExcelWriter(self._report_file)
                frame.to_excel(writer)

                print("# Saving DataFrame as Excel file")
                writer.save()

                attachment = open(self._report_file, "rb+")
                self._send_email(
                    message_from=message['From'],
                    message_to=message_to,
                    message=message,
                    attachment=attachment
                )
        else:
            self._send_email(
                message_from=message['From'],
                message_to=message_to,
                message=message
            )
