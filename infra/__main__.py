import json
from pathlib import Path

import pulumi
import pulumi_aws as aws


def get_config() -> dict:
    config_path = Path(f"config.{pulumi.get_stack()}.json")
    if not config_path.exists():
        raise FileNotFoundError(f"Missing Pulumi config file: {config_path}")

    with config_path.open() as config_file:
        return json.load(config_file)


def require_keys(config_data: dict, keys: list[str]) -> None:
    missing_keys = [key for key in keys if key not in config_data]
    if missing_keys:
        raise ValueError(f"Missing required config keys: {', '.join(missing_keys)}")


def site_domain(config_data: dict) -> str:
    env = config_data["environment"]
    domain = config_data["domain"]
    return domain if env == "prod" else f"{env}.{domain}"


def tags(config_data: dict, name: str, extra: dict | None = None) -> dict:
    base_tags = {
        "Name": name,
        "Project": config_data["domain"],
        "Client": config_data["client"],
        "Tenant": config_data["tenant"],
        "Application": config_data["application"],
        "Environment": config_data["environment"],
        "Repository": config_data["repository"],
        "ManagedBy": "pulumi",
        "PulumiStack": pulumi.get_stack(),
    }
    if extra:
        base_tags.update(extra)
    return base_tags


def make_provider(name: str, region: str, config_data: dict) -> aws.Provider:
    return aws.Provider(
        name,
        region=region,
        default_tags=aws.ProviderDefaultTagsArgs(
            tags=tags(config_data, f"{config_data['resourcePrefix']}-{name}")
        ),
    )


def create_dns_validated_certificate(
    name: str,
    domain_name: str,
    hosted_zone_id: str,
    config_data: dict,
    cert_provider: aws.Provider,
    dns_provider: aws.Provider,
    subject_alternative_names: list[str] | None = None,
) -> aws.acm.CertificateValidation:
    certificate = aws.acm.Certificate(
        name,
        domain_name=domain_name,
        subject_alternative_names=subject_alternative_names or [],
        validation_method="DNS",
        tags=tags(config_data, name),
        opts=pulumi.ResourceOptions(provider=cert_provider),
    )

    validation_records = certificate.domain_validation_options.apply(
        lambda options: [
            aws.route53.Record(
                f"{name}-validation-{idx}",
                zone_id=hosted_zone_id,
                name=option.resource_record_name,
                type=option.resource_record_type,
                records=[option.resource_record_value],
                ttl=300,
                allow_overwrite=True,
                opts=pulumi.ResourceOptions(provider=dns_provider),
            )
            for idx, option in enumerate(options)
        ]
    )

    return aws.acm.CertificateValidation(
        f"{name}-certificate-validation",
        certificate_arn=certificate.arn,
        validation_record_fqdns=validation_records.apply(
            lambda records: [record.fqdn for record in records]
        ),
        opts=pulumi.ResourceOptions(provider=cert_provider),
    )


def setup_backend(config_data: dict, provider: aws.Provider, dns_provider: aws.Provider) -> dict:
    env = config_data["environment"]
    prefix = config_data["resourcePrefix"]
    domain = config_data["domain"]
    api_domain = config_data["apiDomainName"]
    hosted_zone = aws.route53.get_zone(
        name=domain,
        opts=pulumi.InvokeOptions(provider=dns_provider),
    )
    account_id = config_data["awsAccountId"]
    backend_region = config_data["backendRegion"]
    lambda_function_name = config_data["lambdaFunctionName"]

    lambda_log_group = aws.cloudwatch.LogGroup(
        f"{prefix}-contact-api-logs",
        name=f"/aws/lambda/{lambda_function_name}",
        retention_in_days=30,
        tags=tags(config_data, f"{prefix}-contact-api-logs"),
        opts=pulumi.ResourceOptions(provider=provider),
    )

    lambda_role = aws.iam.Role(
        f"{prefix}-lambda-role",
        name=f"{prefix}-lambda-role",
        assume_role_policy=json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Principal": {"Service": "lambda.amazonaws.com"},
                        "Effect": "Allow",
                    }
                ],
            }
        ),
        tags=tags(config_data, f"{prefix}-lambda-role"),
        opts=pulumi.ResourceOptions(provider=provider),
    )

    ses_identity_arn = f"arn:aws:ses:{backend_region}:{account_id}:identity/{domain}"
    aws.iam.RolePolicy(
        f"{prefix}-lambda-policy",
        role=lambda_role.id,
        policy=lambda_log_group.arn.apply(
            lambda log_group_arn: json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "WriteContactApiLogs",
                            "Effect": "Allow",
                            "Action": [
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                            ],
                            "Resource": f"{log_group_arn}:*",
                        },
                        {
                            "Sid": "CreateContactApiLogGroupIfNeeded",
                            "Effect": "Allow",
                            "Action": "logs:CreateLogGroup",
                            "Resource": f"arn:aws:logs:{backend_region}:{account_id}:*",
                        },
                        {
                            "Sid": "SendContactEmail",
                            "Effect": "Allow",
                            "Action": [
                                "ses:SendEmail",
                                "ses:SendRawEmail",
                            ],
                            "Resource": ses_identity_arn,
                        },
                    ],
                }
            )
        ),
        opts=pulumi.ResourceOptions(provider=provider),
    )

    lambda_function = aws.lambda_.Function(
        lambda_function_name,
        name=lambda_function_name,
        runtime="python3.12",
        role=lambda_role.arn,
        handler=config_data["lambdaHandler"],
        code=pulumi.AssetArchive({".": pulumi.FileArchive("./placeholder_lambda/")}),
        environment=aws.lambda_.FunctionEnvironmentArgs(
            variables={
                "ENVIRONMENT_CONFIG": config_data["lambdaEnvironmentConfig"],
                "CONTACT_SOURCE_EMAIL": config_data["sourceEmail"],
                "CONTACT_RECIPIENTS": ",".join(config_data["contactRecipients"]),
            }
        ),
        timeout=30,
        memory_size=256,
        tags=tags(config_data, lambda_function_name),
        opts=pulumi.ResourceOptions(
            provider=provider,
            depends_on=[lambda_log_group],
            ignore_changes=["code"],
        ),
    )

    allowed_origins = [
        f"https://{site_domain(config_data)}",
        f"https://www.{domain}",
        *config_data.get("additionalAllowedOrigins", []),
    ]

    api_gateway = aws.apigatewayv2.Api(
        f"{prefix}-http-api",
        name=f"{prefix}-http-api",
        protocol_type="HTTP",
        cors_configuration=aws.apigatewayv2.ApiCorsConfigurationArgs(
            allow_origins=allowed_origins,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=[
                "Content-Type",
                "X-Amz-Date",
                "Authorization",
                "X-Api-Key",
                "X-Amz-Security-Token",
            ],
            max_age=300,
        ),
        tags=tags(config_data, f"{prefix}-http-api"),
        opts=pulumi.ResourceOptions(provider=provider),
    )

    integration = aws.apigatewayv2.Integration(
        f"{prefix}-lambda-integration",
        api_id=api_gateway.id,
        integration_type="AWS_PROXY",
        integration_uri=lambda_function.arn,
        payload_format_version="2.0",
        opts=pulumi.ResourceOptions(provider=provider),
    )

    aws.apigatewayv2.Route(
        f"{prefix}-default-route",
        api_id=api_gateway.id,
        route_key="$default",
        target=integration.id.apply(lambda integration_id: f"integrations/{integration_id}"),
        opts=pulumi.ResourceOptions(provider=provider),
    )

    stage = aws.apigatewayv2.Stage(
        f"{prefix}-default-stage",
        api_id=api_gateway.id,
        name="$default",
        auto_deploy=True,
        tags=tags(config_data, f"{prefix}-default-stage"),
        opts=pulumi.ResourceOptions(provider=provider),
    )

    aws.lambda_.Permission(
        f"{prefix}-api-lambda-permission",
        action="lambda:InvokeFunction",
        function=lambda_function.name,
        principal="apigateway.amazonaws.com",
        source_arn=api_gateway.execution_arn.apply(lambda arn: f"{arn}/*/*"),
        opts=pulumi.ResourceOptions(provider=provider),
    )

    api_certificate_validation = create_dns_validated_certificate(
        f"{prefix}-api-certificate",
        api_domain,
        hosted_zone.zone_id,
        config_data,
        provider,
        dns_provider,
    )

    api_domain_name = aws.apigatewayv2.DomainName(
        f"{prefix}-api-domain",
        domain_name=api_domain,
        domain_name_configuration=aws.apigatewayv2.DomainNameDomainNameConfigurationArgs(
            certificate_arn=api_certificate_validation.certificate_arn,
            endpoint_type="REGIONAL",
            security_policy="TLS_1_2",
        ),
        tags=tags(config_data, f"{prefix}-api-domain"),
        opts=pulumi.ResourceOptions(provider=provider, depends_on=[api_certificate_validation]),
    )

    aws.apigatewayv2.ApiMapping(
        f"{prefix}-api-mapping",
        api_id=api_gateway.id,
        domain_name=api_domain_name.id,
        stage=stage.name,
        opts=pulumi.ResourceOptions(provider=provider),
    )

    api_domain_name.domain_name_configuration.apply(
        lambda configuration: aws.route53.Record(
            f"{prefix}-api-record",
            zone_id=hosted_zone.zone_id,
            name=api_domain,
            type="A",
            aliases=[
                aws.route53.RecordAliasArgs(
                    name=configuration.target_domain_name,
                    zone_id=configuration.hosted_zone_id,
                    evaluate_target_health=False,
                )
            ],
            opts=pulumi.ResourceOptions(provider=dns_provider),
        )
    )

    pulumi.export("lambda_function_name", lambda_function.name)
    pulumi.export("api_gateway_url", api_gateway.api_endpoint)
    pulumi.export("api_domain_name", api_domain)
    pulumi.export("contact_api_url", f"https://{api_domain}/contact")

    return {
        "api_gateway": api_gateway,
        "lambda_function": lambda_function,
    }


def setup_frontend(config_data: dict, provider: aws.Provider, dns_provider: aws.Provider) -> dict:
    prefix = config_data["resourcePrefix"]
    domain = config_data["domain"]
    bucket_name = config_data["s3BucketName"]
    hosted_zone = aws.route53.get_zone(
        name=domain,
        opts=pulumi.InvokeOptions(provider=dns_provider),
    )
    frontend_domain = site_domain(config_data)
    frontend_aliases = [frontend_domain, *config_data.get("additionalFrontendAliases", [])]
    protect_imported_frontend = config_data.get("protectImportedFrontend", False)

    frontend_certificate_arn = config_data.get("frontendCertificateArn")
    certificate_dependency = None
    if not frontend_certificate_arn:
        certificate_dependency = create_dns_validated_certificate(
            f"{prefix}-frontend-certificate",
            frontend_domain,
            hosted_zone.zone_id,
            config_data,
            dns_provider,
            dns_provider,
            subject_alternative_names=config_data.get("additionalFrontendAliases", []),
        )
        frontend_certificate_arn = certificate_dependency.certificate_arn

    s3_bucket = aws.s3.BucketV2(
        f"{prefix}-web-bucket",
        bucket=bucket_name,
        force_destroy=True,
        tags=tags(config_data, bucket_name),
        opts=pulumi.ResourceOptions(
            provider=provider,
            protect=protect_imported_frontend,
            ignore_changes=[
                "grants",
                "policy",
                "requestPayer",
                "serverSideEncryptionConfigurations",
                "versionings",
            ],
        ),
    )

    aws.s3.BucketPolicy(
        f"{prefix}-web-bucket-policy",
        bucket=s3_bucket.id,
        policy=json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "PublicReadGetObject",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{bucket_name}/*",
                    }
                ],
            }
        ),
        opts=pulumi.ResourceOptions(
            provider=provider,
            protect=protect_imported_frontend,
        ),
    )

    website_origin_domain = f"{bucket_name}.s3-website-{config_data['frontendRegion']}.amazonaws.com"
    s3_origin_domain = f"{bucket_name}.s3.amazonaws.com"
    s3_origin_id = f"S3-{bucket_name}"
    website_origin_id = website_origin_domain

    distribution_dependencies = [certificate_dependency] if certificate_dependency else []
    cdn = aws.cloudfront.Distribution(
        config_data["cloudfrontDistributionName"],
        enabled=True,
        http_version="http2and3",
        is_ipv6_enabled=True,
        web_acl_id=config_data.get("cloudfrontWebAclId") or None,
        aliases=frontend_aliases,
        default_root_object="index.html",
        origins=[
            aws.cloudfront.DistributionOriginArgs(
                domain_name=website_origin_domain,
                origin_id=website_origin_id,
                custom_origin_config=aws.cloudfront.DistributionOriginCustomOriginConfigArgs(
                    origin_protocol_policy="http-only",
                    http_port=80,
                    https_port=443,
                    origin_ssl_protocols=["TLSv1.2"],
                ),
            ),
            aws.cloudfront.DistributionOriginArgs(
                domain_name=s3_origin_domain,
                origin_id=s3_origin_id,
            )
        ],
        default_cache_behavior=aws.cloudfront.DistributionDefaultCacheBehaviorArgs(
            allowed_methods=["GET", "HEAD"],
            cached_methods=["GET", "HEAD"],
            target_origin_id=s3_origin_id,
            cache_policy_id="4135ea2d-6df8-44a3-9df3-4b5a84be39ad",
            compress=True,
            viewer_protocol_policy="redirect-to-https",
        ),
        custom_error_responses=[
            aws.cloudfront.DistributionCustomErrorResponseArgs(
                error_code=403,
                response_page_path="/index.html",
                response_code=200,
                error_caching_min_ttl=10,
            ),
            aws.cloudfront.DistributionCustomErrorResponseArgs(
                error_code=404,
                response_page_path="/index.html",
                response_code=200,
                error_caching_min_ttl=10,
            ),
        ],
        price_class="PriceClass_100",
        restrictions=aws.cloudfront.DistributionRestrictionsArgs(
            geo_restriction=aws.cloudfront.DistributionRestrictionsGeoRestrictionArgs(
                restriction_type="none"
            )
        ),
        viewer_certificate=aws.cloudfront.DistributionViewerCertificateArgs(
            acm_certificate_arn=frontend_certificate_arn,
            ssl_support_method="sni-only",
            minimum_protocol_version="TLSv1.2_2021",
        ),
        tags=tags(config_data, config_data["cloudfrontDistributionName"]),
        opts=pulumi.ResourceOptions(
            provider=dns_provider,
            depends_on=distribution_dependencies,
            protect=protect_imported_frontend,
            ignore_changes=[
                "defaultCacheBehavior.defaultTtl",
                "defaultCacheBehavior.maxTtl",
                "defaultCacheBehavior.trustedKeyGroups",
                "defaultCacheBehavior.trustedSigners",
                "origins",
                "restrictions.geoRestriction.locations",
            ],
        ),
    )

    cloudfront_alias_target = config_data.get("existingCloudfrontDomainName") or cdn.domain_name
    for idx, alias in enumerate(frontend_aliases):
        aws.route53.Record(
            f"{prefix}-frontend-record-{idx}",
            zone_id=hosted_zone.zone_id,
            name=alias,
            type="A",
            aliases=[
                aws.route53.RecordAliasArgs(
                    name=cloudfront_alias_target,
                    zone_id="Z2FDTNDATAQYW2",
                    evaluate_target_health=False,
                )
            ],
            opts=pulumi.ResourceOptions(
                provider=dns_provider,
                protect=protect_imported_frontend,
            ),
        )

    pulumi.export("bucket_name", s3_bucket.bucket)
    pulumi.export("website_url", s3_bucket.bucket_regional_domain_name)
    pulumi.export("cloudfront_distribution_id", cdn.id)

    return {
        "bucket": s3_bucket,
        "cloudfront_distribution": cdn,
    }


def setup_github_actions_user(
    config_data: dict,
    provider: aws.Provider,
    frontend: dict,
    backend: dict,
) -> None:
    prefix = config_data["resourcePrefix"]
    account_id = config_data["awsAccountId"]
    backend_region = config_data["backendRegion"]
    bucket_name = config_data["s3BucketName"]
    lambda_function_name = config_data["lambdaFunctionName"]
    user_name = config_data["githubActionsUserName"]

    user = aws.iam.User(
        f"{prefix}-github-actions-user",
        name=user_name,
        force_destroy=True,
        tags=tags(config_data, user_name),
        opts=pulumi.ResourceOptions(provider=provider),
    )

    deploy_policy = pulumi.Output.all(
        frontend["cloudfront_distribution"].id,
        backend["lambda_function"].arn,
    ).apply(
        lambda args: json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "DeployAngularBuildToWebsiteBucket",
                        "Effect": "Allow",
                        "Action": [
                            "s3:GetBucketLocation",
                            "s3:ListBucket",
                        ],
                        "Resource": f"arn:aws:s3:::{bucket_name}",
                    },
                    {
                        "Sid": "WriteAngularBuildObjects",
                        "Effect": "Allow",
                        "Action": [
                            "s3:DeleteObject",
                            "s3:GetObject",
                            "s3:PutObject",
                        ],
                        "Resource": f"arn:aws:s3:::{bucket_name}/*",
                    },
                    {
                        "Sid": "InvalidateWebsiteDistribution",
                        "Effect": "Allow",
                        "Action": [
                            "cloudfront:CreateInvalidation",
                            "cloudfront:GetDistribution",
                            "cloudfront:GetInvalidation",
                        ],
                        "Resource": f"arn:aws:cloudfront::{account_id}:distribution/{args[0]}",
                    },
                    {
                        "Sid": "DeployContactLambdaCode",
                        "Effect": "Allow",
                        "Action": [
                            "lambda:GetFunction",
                            "lambda:GetFunctionConfiguration",
                            "lambda:UpdateFunctionCode",
                        ],
                        "Resource": args[1],
                    },
                ],
            }
        )
    )

    user_policy = aws.iam.UserPolicy(
        f"{prefix}-github-actions-policy",
        user=user.name,
        policy=deploy_policy,
        opts=pulumi.ResourceOptions(provider=provider),
    )

    pulumi.export("github_actions_user_name", user.name)
    pulumi.export("github_actions_policy_json", deploy_policy)

    if config_data.get("createGithubActionsAccessKey", False):
        access_key = aws.iam.AccessKey(
            f"{prefix}-github-actions-access-key",
            user=user.name,
            opts=pulumi.ResourceOptions(provider=provider, depends_on=[user_policy]),
        )
        pulumi.export("github_actions_access_key_id", access_key.id)
        pulumi.export(
            "github_actions_secret_access_key",
            pulumi.Output.secret(access_key.secret),
        )
    else:
        pulumi.export(
            "github_actions_access_key_note",
            (
                "createGithubActionsAccessKey is false. Create an access key for "
                f"{user_name} manually, or set the flag true temporarily and read "
                "the secret Pulumi output."
            ),
        )

    pulumi.export(
        "lambda_function_arn",
        f"arn:aws:lambda:{backend_region}:{account_id}:function:{lambda_function_name}",
    )


def main() -> None:
    config_data = get_config()
    require_keys(
        config_data,
        [
            "environment",
            "domain",
            "resourcePrefix",
            "tenant",
            "client",
            "application",
            "repository",
            "awsAccountId",
            "frontendRegion",
            "backendRegion",
            "s3BucketName",
            "lambdaFunctionName",
            "lambdaHandler",
            "lambdaEnvironmentConfig",
            "cloudfrontDistributionName",
            "apiDomainName",
            "sourceEmail",
            "contactRecipients",
            "githubActionsUserName",
        ],
    )

    backend_provider = make_provider(
        "backend-provider",
        config_data["backendRegion"],
        config_data,
    )

    frontend = setup_frontend(config_data, None, None)
    backend = setup_backend(config_data, backend_provider, None)
    setup_github_actions_user(config_data, backend_provider, frontend, backend)


main()
