
## Alerting New Feature on XC3 (implementing send notification part)

The Alerting New Feature on XC3 extension enhances XC3 with an alerting mechanism using AWS Lambda functions to send notifications via email and Slack channels. This README provides information on setting up and running the extension.


## Before you begin, ensure you have the following prerequisites:

Python 3.9 installed
Terraform installed
An active AWS account
AWS CLI configured with your access credentials
## Installation Guide: Python 3.9 (or Newer)
Python is required to run the scripts and programs for the Alerting New Feature on XC3 extension.

### Windows:
Visit the official Python website: https://www.python.org/downloads/

Download the latest version of Python for Windows.

Run the installer and make sure to check the box that says "Add Python X.X to PATH."

Click "Install Now."

### macOS:
Open the terminal.

Install Homebrew (if not already installed) by running:

    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"


Install Python using Homebrew by running:

    brew install python

## Installation Guide: Terraform

Terraform is used to provision and manage cloud resources for the Alerting New Feature on XC3 extension.

### Windows:

Visit the official Terraform website: https://www.terraform.io/downloads.html

Download the appropriate version of Terraform for Windows.

Extract the downloaded ZIP file to a directory of your choice.

Add the directory containing the Terraform executable to your system's PATH.

### macOS:

Open the terminal.

Install Homebrew (if not already installed) by running:

    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

Install Terraform using Homebrew by running:

    brew tap hashicorp/tap
    brew install hashicorp/tap/terraform

### Verify Installations:

After installation, verify that Python and Terraform are correctly installed by opening a terminal window and running the following commands:

For Python:

    python --version

For Terraform:

    terraform version

If the version numbers are displayed without errors, you have successfully installed Python and Terraform.

That's it! You're now ready to set up and use the Alerting New Feature on XC3 extension.

## Installation and Setup

1. Clone this repository to your local machine.

2. Navigate to the project directory.

## Configuration

Before running the code, you need to configure your AWS CLI, SES email, and Slack webhook:

### AWS CLI Configuration

Configure your AWS CLI by running:

    aws configure

Provide your AWS Access Key ID, Secret Access Key, default region, and output format.

### SES Email Configuration

Follow the attached instructions to configure and subscribe your email address for identifiers on Amazon SES.

### Slack Webhook Configuration

Create a webhook URL for your Slack channel following the attached instructions.


## Customization and Configuration (Lambda Function)

To customize the behavior of the Lambda function for sending notifications:

1. Open the ce_lambda_slack.py file.

2. Locate the send_slack() function:

* Set the desired threshold by modifying the cost_threshold variable.

* Input your Slack webhook URL within the r = http.request(...) call.

3. Locate the send_email() function:

* Input your email for SENDER and RECIPIENT variable.




## Running the Code

Ensure you have the logo.png file in the root directory.

Enable AWS Cost Explorer in your AWS account.

Navigate to the project directory and run the following commands:

    terraform init
    terraform plan
    terraform apply

## Appendix

Tutorial for Creating readme file: 

https://www.youtube.com/watch?v=QcZKsbgsLa4

Cloud watch rule: 

https://www.youtube.com/watch?v=Z2G3tST4d1c&t=462s



