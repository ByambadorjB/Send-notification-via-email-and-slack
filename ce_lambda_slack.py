import base64
import boto3
import json
from botocore.exceptions import ClientError
import urllib3
import datetime
import csv
import io
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.mime.application import MIMEApplication

# Fetch the logo image URL from S3
bucket_name = "ce-lambda-bucket"
logo_key = "logo.png"

def lambda_handler(event, context):
    # Create a Cost Explorer client in the EU (Ireland) region
    cost_explorer = boto3.client('ce', region_name='ap-southeast-2')
    
    current_time = datetime.datetime.utcnow()

    # Calculate the start and end dates for the current month
    last_month = current_time-datetime.timedelta(days=1)
    start_date = datetime.datetime(last_month.year, last_month.month, 1).strftime('%Y-%m-%d')
    end_date = last_month.strftime('%Y-%m-%d')

    # Retrieve the cost data using the appropriate Cost Explorer API method
    response = cost_explorer.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity='DAILY',
        Metrics=[
            'UnblendedCost',
        ]
    )
    print(response)

    # Transform the cost data as needed
    transformed_data, total_cost = transform_data(response)

    # Calculate the total cost 
    total_cost = sum(entry['cost'] for entry in transformed_data)

    # Set the cost Threshold
    cost_threshold = 10.0

    # send notification if total cost exceeds the threshold
    if total_cost > cost_threshold:
        send_notification(transformed_data, total_cost)

    send_slack(transformed_data, total_cost)

    return {
        'statusCode': 200,
        'body': json.dumps('Cost data retrieved and notifications sent if needed')
    }

def transform_data(data):
    transformed_data = []
    total_cost = 0.0
    for result in data['ResultsByTime']:
        cost = float(result['Total']['UnblendedCost']['Amount'])
        total_cost += cost
        transformed_data.append({
            'time': result['TimePeriod']['Start'],
            'cost': cost
        })
    # transformed_data.append({
    #     'time': 'Total',
    #     'cost': total_cost
    # })
    return transformed_data, total_cost

def send_notification(data, total_cost):
    # Prepare the message text for email and slack
    message = ""
    total_cost_message = f"Your Total Cost for this month: ${total_cost:.2f}\n"

    for entry in data[:-1]: 
        message += f"Time: {entry['time']} Cost: ${entry['cost']:.2f}\n"
        
    # Insert total cost message at the beginning of the message
    message = total_cost_message + message

    # Create a csv file
    csv_file_name = "/tmp/cost_data.csv"
    with open(csv_file_name, mode='w', newline='') as csv_file:
        fieldnames = ['Time', 'Cost']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for entry in data:
            writer.writerow({'Time': entry['time'], 'Cost': entry['cost']})

    send_email(message, csv_file_name)
    # send_slack(message_str) 

# Sending response data to slack
def send_slack(data, total_cost):
    try: 
        http = urllib3.PoolManager()
        message = f"Your Total Cost for this month: ${total_cost:.2f}\n"
        for entry in data:
            message += f"Time: {entry['time']} Cost: ${entry['cost']:.2f}\n"
        messages = {"text": message}
        r = http.request(
            "POST",
            "https://hooks.slack.com/services/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",
            body=json.dumps(messages), 
            headers={"Content-Type": "application/json"}
        )
    except Exception as e:
        print("An error occurred: ", e)
   
def send_email(data, csv_file_name):
    SENDER = "103133909@student.swin.edu.au"
    RECIPIENT = "103133909@student.swin.edu.au"
    AWS_REGION = "ap-southeast-2"
    SUBJECT = "AWS Account Cost Alert"

    #Prepare HTML body with red color for total cost 
    total_cost = data.splitlines()[0]
    total_cost_html = f'<span style="color: red;">{total_cost}</span>'

    CHARSET = "UTF-8"
    client = boto3.client('ses', region_name=AWS_REGION)

    # Create the email message
    msg = MIMEMultipart('mixed')
    msg['Subject'] = SUBJECT
    msg['From'] = SENDER
    msg['To'] = RECIPIENT

    # Get the object (logo.png) from S3 bucket
    s3_client = boto3.client("s3")
    response = s3_client.get_object(Bucket=bucket_name, Key=logo_key)
    logo_data = response["Body"].read()

    # # Encode the logo image data in Base64
    logo_base64 = base64.b64encode(logo_data).decode("utf-8")

    try: 
        # Create the HTML version of the email body with logo
        html_body = f""" 
        <html>
        <head>
            <style>
                /* CSS styles... */
                .container {{
                    font-family: Arial, sans-serif;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    border: 1px solid #ccc;
                }}
                .header {{
                    background-color: #f0f0f0;
                    padding: 10px;
                    text-align: center;
                }}
                .logo {{
                    text-align: center;
                }}
                .logo img {{
                    max-width: 200px;
                    height: auto;
                }}
                .message {{
                    margin-top: 20px;
                }}
                .message h2 {{
                    color: red;
                }}
                .message p {{
                    margin: 10px 0;
                }}
                
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Your AWS Account Cost Alert</h2>
                </div>
                <div class="logo">
                    <img src="data:image/png;base64,{logo_base64}" alt="Your Logo">
                </div>
                <div class="message">
                    <h2> {total_cost_html}</h2>
                    <p>Dear XC3 Customer,</p>
                    <p>Your AWS account cost exceeded 80%. Please find the cost breakdown below:</p>
                </div>
                <div class="message">
                    <p>Please find the attached file for detailed cost information.</p>
                    <p>Best regards,<br>XC3 Team</p>
                </div>
            </div>
        </body>
        </html>
        """

        #Attach the HTML body
        html_part = MIMEText(html_body, 'html', CHARSET)
        msg.attach(html_part)
    except Exception as e:
        print("Error reading logo.png from S3:", str(e))

    try:
    #Attach the csv file
        with open(csv_file_name, 'rb') as attachment:
            csv_part = MIMEApplication(attachment.read())
            csv_part.add_header('Content-Disposition', f'attachment; filename="{csv_file_name}"')
            msg.attach(csv_part)

        response = client.send_raw_email(RawMessage={'Data': msg.as_string()})
        print("Email sent! Message ID: ", response['MessageId'])

    except ClientError as e:
        print(e.response['Error']['Message'])
   

   
    