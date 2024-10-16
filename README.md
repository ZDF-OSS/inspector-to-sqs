# AWS Inspector Findings to SQS

This project provides a Python script that retrieves AWS Inspector V2 findings and sends them as JSON messages to an AWS SQS queue. The script allows configuration of the SQS queue name, target AWS account, and filtering criteria (severity and resource type) via a local configuration file.

## Features

- Retrieves findings from AWS Inspector V2.
- Filters findings based on severity and resource type (configurable).
- Sends findings as messages to an AWS SQS queue.
- Queue name, AWS account ID, severity, and resource types are configurable through a `config.json` file.
- Flexible enrichment of findings before sending them to SQS (additional fields can be added).

## Prerequisites

- Python 3.x
- AWS credentials with sufficient permissions to access AWS Inspector V2 and SQS.
- `boto3` library installed (`pip install boto3`).

## Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-repo/aws-inspector-sqs.git
   cd aws-inspector-sqs
   ```

2. **Install required dependencies**:
   ```bash
   pip install -r requirements
   ```

3. **Create a local configuration file**:
   Create a `config.json` file in the root directory of the project. This file should be excluded from version control by ensuring it is listed in the `.gitignore` file.

   Example `config.json`:
   ```json
   {
       "queue_name": "your-sqs-queue-name",
       "account_id": "123456789012",
       "severity": ["HIGH", "CRITICAL"],
       "resourceType": ["AWS_EC2_INSTANCE"]
   }
   ```

4. **AWS Configuration**:
   Ensure that your AWS credentials are set up, either through environment variables, an AWS credentials file, or an instance profile (if running on EC2).

## Configuration

The configuration file (`config.json`) allows you to specify:
- `queue_name`: The name of the SQS queue where findings will be sent.
- `account_id`: The AWS account ID owning the SQS queue.
- `severity`: A list of severity levels to filter findings (`HIGH`, `CRITICAL`, etc.).
- `resourceType`: A list of resource types to filter findings (e.g., `AWS_EC2_INSTANCE`, `AWS_LAMBDA_FUNCTION`).

### Example `config.json`:

```json
{
    "queue_name": "my-sqs-queue",
    "account_id": "123456789012",
    "severity": ["HIGH", "CRITICAL"],
    "resourceType": ["AWS_EC2_INSTANCE", "AWS_LAMBDA_FUNCTION"]
}
```

### Notes:
- **`queue_name`**: The SQS queue name must exist in your AWS account.
- **`account_id`**: Ensure that you have the necessary permissions in this AWS account.
- **`severity`**: You can customize the severity filter by adding/removing values.
- **`resourceType`**: Specify which AWS resources to filter on (e.g., EC2 instances, Lambda functions).

## Usage

1. **Run the script**:
   After configuring the `config.json` file, run the script to fetch the AWS Inspector findings and send them to the specified SQS queue.

   ```bash
   python inspector_to_sqs.py
   ```

2. **Output**:
   The script will log how many findings were retrieved and sent to the SQS queue. 

   Example:
   ```bash
   Total critical EC2 findings retrieved: 10
   Message sent to SQS queue my-sqs-queue, MessageId: <message-id>
   ```

## Customization

The script can be extended by modifying the `enrich_item` function to add additional fields to each finding before it is sent to SQS.

```python
def enrich_item(item):
    item["DocumentType"] = "EC2"
    # Add more fields here
    return item
```

## Logging and Error Handling

The script uses basic logging to provide information about errors that occur when fetching findings or sending messages to SQS. Make sure to monitor the logs for any issues.

## Contributing

Feel free to open issues or submit pull requests if you have any improvements or suggestions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
