import json
import os
import pulumi
import pulumi_aws as aws
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve GitHub token from environment variable
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise ValueError("GitHub token is not set in the environment variables")

# Load inputs from a JSON file
with open('config.json') as config_file:
    config = json.load(config_file)
    print("Configuration loaded from 'config.json'.")

def create_iam_role(role_name: str, service: str, policy_statements: list) -> aws.iam.Role:
    print(f"Creating IAM role: {role_name}")
    role = aws.iam.Role(role_name,
                        assume_role_policy=json.dumps({
                            "Version": "2012-10-17",
                            "Statement": [{
                                "Action": "sts:AssumeRole",
                                "Principal": {"Service": service},
                                "Effect": "Allow",
                                "Sid": ""
                            }]
                        }))
    for idx, statement in enumerate(policy_statements):
        aws.iam.RolePolicy(f"{role_name}-policy-{idx}",
                           role=role.id,
                           policy=json.dumps({
                               "Version": "2012-10-17",
                               "Statement": [statement]
                           }))
    print(f"IAM role '{role_name}' created.")
    return role

def create_lambda_function(name: str, role_arn: str, handler: str, path_to_code: str) -> aws.lambda_.Function:
    print(f"Creating Lambda function: {name}")
    lambda_function = aws.lambda_.Function(name,
                                           role=role_arn,
                                           runtime="python3.12",
                                           handler=handler,
                                           code=pulumi.FileArchive(path_to_code))
    print(f"Lambda function '{name}' created.")
    return lambda_function

def setup_ses_domain_and_verification(domain: str, hosted_zone_id: str) -> None:
    print(f"Setting up SES domain and verification for: {domain}")
    ses_domain_identity = aws.ses.DomainIdentity("sesDomain", domain=domain)
    print(f"SES domain '{domain}' created for verification.")

    ses_verification_record = aws.route53.Record("sesVerificationRecord",
                                                 zone_id=hosted_zone_id,
                                                 name=ses_domain_identity.verification_token.apply(lambda token: f"_amazonses.{domain}"),
                                                 type="TXT",
                                                 ttl=1800,
                                                 records=[ses_domain_identity.verification_token.apply(lambda token: f'{token}')])
    print(f"DNS record for SES domain verification created.")

    aws.ses.DomainIdentityVerification("sesDomainIdentityVerification",
                                       domain=ses_domain_identity.id,
                                       opts=pulumi.ResourceOptions(depends_on=[ses_verification_record]))
    print("SES domain verification process initiated.")

def create_iam_user_for_github_actions(lambda_function_arn: str, username: str) -> aws.iam.AccessKey:
    user = aws.iam.User("githubActionsUser",
                        name=username,
                        path="/",
                        force_destroy=True)
    print(f"IAM user '{username}' created.")

    policy = aws.iam.UserPolicy("githubActionsUserPolicy",
                                user=user.name,
                                policy=lambda_function_arn.apply(lambda arn: json.dumps({
                                    "Version": "2012-10-17",
                                    "Statement": [{
                                        "Effect": "Allow",
                                        "Action": [
                                            "lambda:UpdateFunctionCode",
                                            "lambda:GetFunctionConfiguration"
                                        ],
                                        "Resource": arn
                                    }]
                                })))
    print("Policy attached to GitHub Actions user.")

    access_key = aws.iam.AccessKey("githubActionsAccessKey",
                                   user=user.name,
                                   opts=pulumi.ResourceOptions(depends_on=[policy]))
    print("Access key for GitHub Actions user created.")

    return access_key

def create_api_gateway(lambda_function: aws.lambda_.Function) -> (aws.apigateway.RestApi, aws.apigateway.Deployment):
    api = aws.apigateway.RestApi("apiGateway",
                                 name="ApiGatewayForLambda",
                                 description="API Gateway to trigger Lambda function")

    resource = aws.apigateway.Resource("apiResource",
                                       rest_api=api.id,
                                       parent_id=api.root_resource_id,
                                       path_part="{proxy+}")

    method = aws.apigateway.Method("apiMethod",
                                   rest_api=api.id,
                                   resource_id=resource.id,
                                   http_method="ANY",
                                   authorization="NONE")

    integration = aws.apigateway.Integration("apiIntegration",
                                             rest_api=api.id,
                                             resource_id=resource.id,
                                             http_method=method.http_method,
                                             integration_http_method="POST",
                                             type="AWS_PROXY",
                                             uri=lambda_function.invoke_arn)

    deployment = aws.apigateway.Deployment("apiDeployment",
                                           rest_api=api.id,
                                           stage_name="prod",
                                           opts=pulumi.ResourceOptions(depends_on=[integration]))

    return api, deployment

# Main execution starts here
print("Starting Pulumi script execution...")

# Define and deploy resources
print("Deploying resources...")

lambda_exec_role = create_iam_role(
    config["lambdaExecRoleName"],
    "lambda.amazonaws.com",
    [
        {
            "Effect": "Allow",
            "Action": ["logs:*"],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": ["ses:SendEmail", "ses:VerifyEmailIdentity"],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": ["lambda:InvokeFunction"],
            "Resource": "*"  # You can specify specific ARNs here if needed
        }
    ]
)

lambda_function = create_lambda_function(config["lambda_function_name"], lambda_exec_role.arn, config["lambda_handler"], config["lambda_code_folder"])
setup_ses_domain_and_verification(config['email_domain'], config['hosted_zone_id'])

lambda_function.arn.apply(lambda arn: aws.iam.RolePolicy("lambdaExecRolePolicy",
                   role=lambda_exec_role.id,
                   policy=json.dumps({
                       "Version": "2012-10-17",
                       "Statement": [
                           {
                               "Effect": "Allow",
                               "Action": [
                                   "logs:*",
                                   "ses:SendEmail",
                                   "ses:VerifyEmailIdentity",
                                   "lambda:InvokeFunction"
                               ],
                               "Resource": arn
                           }
                       ]
                   })))

api_gateway, deployment = create_api_gateway(lambda_function)

github_actions_user_username = config["github_actions_user_username"]
github_actions_access_key = create_iam_user_for_github_actions(lambda_function.arn, github_actions_user_username)

# Export outputs
api_gateway_url = deployment.invoke_url.apply(lambda url: f"{url}/prod")
pulumi.export('api_gateway_url', api_gateway_url)
pulumi.export('lambda_function_name', lambda_function.name)

# Output the secrets to the console
pulumi.export('LAMBDA_AWS_ACCESS_KEY_ID', github_actions_access_key.id)
pulumi.export('LAMBDA_AWS_SECRET_ACCESS_KEY', github_actions_access_key.secret)

print("Resource deployment completed.")
