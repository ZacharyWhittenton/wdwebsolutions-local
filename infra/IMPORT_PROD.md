# Production Import Plan

This stack should manage the website and API resources, but it should not manage the actual domain registration or the Route53 hosted zone for `wdwebsolutions.com`.

The Pulumi program intentionally uses `aws.route53.get_zone(...)` as a data source. That means `pulumi destroy` cannot delete the hosted zone or abandon the domain. It can only delete Route53 records that are declared in this stack.

## Import Existing Production Resources

Import the resources that already power the production website, then let Pulumi create the new backend/API resources.

Known existing values:

- S3 bucket: `wdwebsolutions.com`
- CloudFront distribution: `E5R6IPQNGNHV1`
- Frontend DNS name: `wdwebsolutions.com`

Known hosted zone:

- Route53 hosted zone ID: `Z0788729IO99YJ1U6MA4`

Values to look up before import:

- ACM certificate ARN used by the current CloudFront distribution
- Current S3 bucket policy

## Do Not Import

Do not import these:

- Route53 hosted zone for `wdwebsolutions.com`
- Domain registration for `wdwebsolutions.com`
- Any parent DNS resources not specific to this site

## DNS Records This Stack May Manage

These are site-specific and are acceptable to import or create:

- Apex `A` alias record for `wdwebsolutions.com` pointing at CloudFront
- `www.wdwebsolutions.com` `A` alias record pointing at CloudFront
- API `A` alias record for `api.wdwebsolutions.com` pointing at API Gateway
- DNS validation records for ACM certificates created by this stack

If the stack is destroyed later, those records may be deleted, but the hosted zone and domain remain.

## Initial Import Commands

Run these from `infra/` after selecting or creating the `prod` stack:

```bash
pulumi stack select prod || pulumi stack init prod

pulumi import aws:s3/bucketV2:BucketV2 \
  wdwebsolutions-prod-web-bucket \
  wdwebsolutions.com

pulumi import aws:cloudfront/distribution:Distribution \
  wdwebsolutions-prod-web \
  E5R6IPQNGNHV1
```

The Route53 apex record import ID has this format:

```text
HOSTED_ZONE_ID_RECORD_NAME_RECORD_TYPE
```

For the apex record it will look like:

```bash
pulumi import aws:route53/record:Record \
  wdwebsolutions-prod-frontend-record-0 \
  Z0788729IO99YJ1U6MA4_wdwebsolutions.com_A

pulumi import aws:route53/record:Record \
  wdwebsolutions-prod-frontend-record-1 \
  Z0788729IO99YJ1U6MA4_www.wdwebsolutions.com_A
```

## Preview Before Applying

After each import, run:

```bash
pulumi preview
```

The goal is no unexpected replacements. If preview wants to replace the CloudFront distribution, certificate, or bucket, update the Pulumi resource arguments to match the live AWS settings before applying.

## Recommended Path

1. Import the existing S3 bucket.
2. Import or align the bucket website configuration, policy, and public access block.
3. Import the existing CloudFront distribution.
4. Import the apex Route53 `A` alias record.
5. Create a new stack-specific ACM certificate instead of importing the existing wildcard certificate, unless you confirm that wildcard certificate is not shared by anything else.
6. Let Pulumi create the new Lambda, API Gateway, `api.wdwebsolutions.com` record, and deployment IAM user.

## Imported On 2026-04-27

The `prod` stack currently imports and protects:

- `aws:s3/bucketV2:BucketV2` `wdwebsolutions-prod-web-bucket` -> `wdwebsolutions.com`
- `aws:s3/bucketPolicy:BucketPolicy` `wdwebsolutions-prod-web-bucket-policy` -> `wdwebsolutions.com`
- `aws:cloudfront/distribution:Distribution` `wdwebsolutions-prod-web` -> `E5R6IPQNGNHV1`
- `aws:route53/record:Record` `wdwebsolutions-prod-frontend-record-0` -> `Z0788729IO99YJ1U6MA4_wdwebsolutions.com_A`
- `aws:route53/record:Record` `wdwebsolutions-prod-frontend-record-1` -> `Z0788729IO99YJ1U6MA4_www.wdwebsolutions.com_A`

The hosted zone and domain registration are still unmanaged data sources.

The existing wildcard ACM certificate and CloudFront WAF web ACL are referenced by ARN but not imported. This avoids letting this site stack destroy broader resources that may be reusable elsewhere.
