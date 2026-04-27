#!/usr/bin/env bash
set -euo pipefail

STACK="${1:-prod}"
REPO="${GITHUB_REPOSITORY:-WD-Web-Solutions/wdwebsolutions.com}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${INFRA_DIR}"

bucket_name="$(pulumi stack output bucket_name --stack "${STACK}")"
distribution_id="$(pulumi stack output cloudfront_distribution_id --stack "${STACK}")"
lambda_function_name="$(pulumi stack output lambda_function_name --stack "${STACK}")"
contact_api_url="$(pulumi stack output contact_api_url --stack "${STACK}")"

gh variable set PROD_S3_BUCKET --repo "${REPO}" --body "${bucket_name}"
gh variable set PROD_CLOUDFRONT_DISTRIBUTION_ID --repo "${REPO}" --body "${distribution_id}"
gh variable set PROD_LAMBDA_FUNCTION_NAME --repo "${REPO}" --body "${lambda_function_name}"
gh variable set PROD_CONTACT_API_URL --repo "${REPO}" --body "${contact_api_url}"

if [[ "${SYNC_AWS_SECRETS:-false}" == "true" ]]; then
  pulumi stack output github_actions_access_key_id --stack "${STACK}" \
    | gh secret set WDWS_DEPLOY_AWS_ACCESS_KEY_ID --repo "${REPO}"
  pulumi stack output github_actions_secret_access_key --show-secrets --stack "${STACK}" \
    | gh secret set WDWS_DEPLOY_AWS_SECRET_ACCESS_KEY --repo "${REPO}"
fi

echo "Synced GitHub Actions variables for ${REPO} from Pulumi stack ${STACK}."
