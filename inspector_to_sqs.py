import json
import boto3
import sys
import logging
import datetime
from botocore.exceptions import ClientError

# Initialize the InspectorV2 client
inspector_client = boto3.client('inspector2', region_name='eu-central-1')
# Initialize SQS client
sqs = boto3.client('sqs', region_name='eu-central-1')


def load_config():
    """
    Load configuration from a local JSON file (config.json).
    """
    try:
        with open('config.json') as config_file:
            config = json.load(config_file)
            return config
    except Exception as e:
        logging.error(f"Failed to load configuration: {e}")
        sys.exit(1)


def send_to_sqs(queue_name, account_id, message_body):
    """
    Sends a JSON message to an AWS SQS queue.

    Parameters:
        queue_name (str): The name of the SQS queue.
        message_body (dict): The JSON payload to send.

    Returns:
        dict: Response from SQS send_message call.
    """

    try:
        response = sqs.get_queue_url(QueueName=queue_name, QueueOwnerAWSAccountId=account_id)
        queue_url = response['QueueUrl']
    except ClientError as e:
        logging.error(f"Failed to get queue URL for {queue_name}: {e}")
        sys.exit(1)

    try:
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message_body)
        )
        logging.info(f"Message sent to SQS queue {queue_name}, MessageId: {response['MessageId']}")
        return response
    except ClientError as e:
        logging.error(f"Failed to send message to {queue_name}: {e}")
        sys.exit(1)


def get_findings(config):
    findings = []
    next_token = None

    try:
        while True:
            # Build the filter criteria based on config
            params = {
                'filterCriteria': {
                    'severity': [
                        {'comparison': 'EQUALS', 'value': sev} for sev in config['severity']
                    ],
                    'resourceType': [
                        {'comparison': 'EQUALS', 'value': rt} for rt in config['resourceType']
                    ],
                    'findingStatus': [
                        {'comparison': 'EQUALS', 'value': 'ACTIVE'}
                    ]
                }
            }

            if next_token:
                params['nextToken'] = next_token

            response = inspector_client.list_findings(**params)
            findings_list = response.get('findings', [])
            if findings_list:
                findings.extend(findings_list)

            next_token = response.get('nextToken')
            if not next_token:
                break

        return findings

    except Exception as e:
        logging.error(f"Error fetching findings: {e}")
        return []

def enrich_item(item):
    """
    Enrich findings with additional fields.

    Parameters:
        item (dict): The original finding item.

    Returns:
        dict: The enriched finding item.
    """
    item["DocumentType"] = "EC2"
    return item


def convert_datetime(obj):
    if isinstance(obj, dict):
        return {k: convert_datetime(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_datetime(item) for item in obj]
    elif isinstance(obj, datetime.datetime):
        return obj.isoformat()
    else:
        return obj


def main():
    # Load config for SQS queue and account ID
    config = load_config()

    findings = get_findings(config)

    queue_name = config.get('queue_name')
    account_id = config.get('account_id')

    logging.info(f"Total critical findings retrieved: {len(findings)}")

    if findings:
        for item in findings:
            item = enrich_item(item)
            item = convert_datetime(item)
            send_to_sqs(queue_name, account_id, item)


if __name__ == "__main__":
    main()
