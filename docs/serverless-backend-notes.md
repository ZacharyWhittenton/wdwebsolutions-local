# Serverless Backend Notes

## Current branch

- Infrastructure is under `infra/`, configured for `wdwebsolutions.com`.
- Runtime contact API code is under `api/` as a FastAPI app adapted to Lambda with Mangum.
- Production contact submissions target `https://api.wdwebsolutions.com/contact`.
- Local Angular development targets `http://localhost:8000/contact`.
- Captcha is intentionally omitted for now.

## FastAPI Lambda backend

FastAPI on Lambda is possible and is a good fit for this project while traffic is low. The usual production shape is:

- FastAPI app for routes and validation.
- Mangum as the AWS Lambda adapter.
- API Gateway HTTP API using a proxy/default route.
- Local development through `uvicorn`.
- Integration tests using FastAPI `TestClient`.

The current backend uses that shape. The deployed Pulumi handler can remain `main.main` because `main` is assigned to the Mangum adapter, and `handler` is also exported for a later cleanup branch if we want the infrastructure config to say `main.handler`.

## Dev environment branch

The Pulumi script includes a `dev` config for the later environment:

- Frontend: `dev.wdwebsolutions.com`
- API: `api.dev.wdwebsolutions.com`
- Lambda: `wdwebsolutions-dev-contact-api`
- Bucket: `dev.wdwebsolutions.com`

The matching GitHub Actions workflow should be added when the dev frontend/backend are ready to deploy.

## Frontend endpoint configuration

The Angular app currently uses compile-time Angular environment files:

- Production: `client/src/environments/environment.ts`
- Local development: `client/src/environments/environment.development.ts`

A later branch can remove compile-time endpoint values by using one of these patterns:

- Serve a small runtime `config.json` from S3 and fetch it before app bootstrap.
- Route `/api/*` through CloudFront to API Gateway and call the API with same-origin relative URLs.
- Write environment values during CI from GitHub variables.

The runtime `config.json` or same-origin `/api/*` options are better for a reusable multi-tenant blueprint.

## GitHub Actions AWS access

The current Pulumi script creates a least-privilege IAM user and policy for deployment. It does not create an access key unless `createGithubActionsAccessKey` is set to `true`.

Creating long-lived IAM user keys and copying them into GitHub secrets works, but GitHub OIDC is preferred because it avoids static AWS credentials entirely. A future infrastructure branch should replace the IAM user with an IAM role trusted by GitHub's OIDC provider and scoped to this repository and branch.

If you do use the generated IAM user, set these GitHub Actions secrets:

- `WDWS_DEPLOY_AWS_ACCESS_KEY_ID`
- `WDWS_DEPLOY_AWS_SECRET_ACCESS_KEY`

After Pulumi deployment, non-secret workflow variables can be synced with:

```bash
cd infra
./scripts/sync-github-actions-config.sh prod
```

Set `SYNC_AWS_SECRETS=true` only if you intentionally created a Pulumi-managed access key and want the script to write those secrets to GitHub.

## Deployment Caveat

The production domain already has existing website infrastructure outside this new Pulumi stack. Before running `pulumi up` for production, decide whether to import the existing S3/CloudFront resources into Pulumi or replace them. Creating a second CloudFront distribution with the same `wdwebsolutions.com` alias will fail until the existing alias is released or imported.

The Route53 hosted zone and domain registration should stay outside this stack. Import only site-specific DNS records, such as the apex `A` alias record and any certificate validation records that belong to resources managed by this stack. See `infra/IMPORT_PROD.md`.
