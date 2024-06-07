import json
import pulumi
import pulumi_aws as aws

# Load inputs from a JSON file
with open('config.json') as config_file:
    config = json.load(config_file)

def create_iam_role(role_name: str, service: str, policy_statements: list) -> aws.iam.Role:
    """
    Creates an IAM role for a specified AWS service.
    Args:
        role_name: The name of the IAM role.
        service: The AWS service principal.
        policy_statements: Policy statements for the role's permissions.

    Returns:
        IAM Role resource.
    """
    assume_role_policy = json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Action": "sts:AssumeRole",
            "Principal": {"Service": service},
            "Effect": "Allow",
            "Sid": ""
        }]
    })
    return aws.iam.Role(role_name,
                        assume_role_policy=assume_role_policy)

def attach_policy_to_role(role: aws.iam.Role, policy_name: str, policy: dict) -> aws.iam.RolePolicy:
    """
    Attaches a policy to an IAM role.
    Args:
        role: IAM Role resource to attach the policy to.
        policy_name: Name for the policy.
        policy: Policy document.

    Returns:
        IAM Role Policy resource.
    """
    return aws.iam.RolePolicy(policy_name,
                              role=role.name,
                              policy=json.dumps(policy))

def create_lambda_function(name: str, role_arn: str, handler: str, path_to_code: str) -> aws.lambda_.Function:
    """
    Creates an AWS Lambda function.
    Args:
        name: The name of the Lambda function.
        role_arn: ARN of the IAM role associated with this function.
        handler: The function within your code that Lambda calls to begin execution.
        path_to_code: The path to the Lambda function code.

    Returns:
        Lambda Function resource.
    """
    return aws.lambda_.Function(name,
                                role=role_arn,
                                runtime="python3.12",
                                handler=handler,
                                code=pulumi.FileArchive(path_to_code))

def setup_ses_domain_and_verification(domain: str, hosted_zone_id: str) -> None:
    """
    Sets up SES domain identity and creates necessary DNS records for domain verification.
    Args:
        domain: The email domain to be verified.
        hosted_zone_id: The Route 53 hosted zone ID where the domain is managed.

    Returns:
        None
    """
    ses_domain = aws.ses.DomainIdentity("sesDomain",
                                        domain=domain)

    ses_verification_record = aws.route53.Record("sesVerificationRecord",
        zone_id=hosted_zone_id,
        name=ses_domain.verification_token.apply(lambda token: f"_amazonses.{domain}"),
        type="TXT",
        ttl=1800,
        records=[ses_domain.verification_token.apply(lambda token: f'"{token}"')])

    aws.ses.DomainIdentityVerification("sesDomainIdentityVerification",
                                       domain=ses_domain.id,
                                       opts=pulumi.ResourceOptions(depends_on=[ses_verification_record]))

# Example usage of the functions within the Pulumi script
# IAM Role for Lambda execution
lambda_exec_role = create_iam_role(config["lambdaExecRoleName"], "lambda.amazonaws.com", [{
    "Effect": "Allow",
    "Action": ["logs:*", "ses:SendEmail", "ses:VerifyEmailIdentity"],
    "Resource": "*"
}])

# Lambda Function
lambda_function = create_lambda_function(config["lambda_function_name"], lambda_exec_role.arn, "main.main", "./path_to_your_lambda_code")

# Setup SES Domain and Verification
setup_ses_domain_and_verification(config['email_domain'], config['hosted_zone_id'])

# The rest of the script would follow using similar patterns for creating and configuring other resources
