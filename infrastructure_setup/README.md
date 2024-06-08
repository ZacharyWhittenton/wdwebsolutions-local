# Installing dependencies with Pulumi

## Install Python packages
- run pip install pulumi
- run pip install pulumi_aws

## Install Pulumi on system
- MacOS: brew install pulumi
- WindowsOS: choco install pulumi
- Restart computer

## Login to aws credentials before running
- install aws CLI if you haven't yet
- restart computer if installing
- run aws configure and add credentials (can be found in AWS console)

## Editing config
- edit variables in the config.json file
- add a new file called ".env" in the same directory as __main__.py
  - this .env will contain the following credential:
  - GITHUB_TOKEN=your_github_token
  - This github token will have your github personal access token

# Running Pulumi:
- run pulumi up
- if this doesn't work, may need to run following command:
- pulumi stack init {{ name }}
  - name example: "wdwebsolutions-prod"
- to read the pulumi outputs
  - run pulumi stack output --show-secrets

# Tearing down resource
- run pulumi destroy
  - this will tear down all resources associated with this pulumi stack
