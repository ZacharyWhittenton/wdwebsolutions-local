# wdwebsolutions.com
Repo for the WD Web Solutions Angular Website


## Deploying:
- Deployment is handled via a .yaml file with GitHub Actions
- With every push to "main", the new files are pushed to a private S3 public
- An AWS Cloudfront distribution distributes the files stored in the S3 bucket
  - These files are stored at edge locations for better performance
  - Cloudfront allows for HTTPS encryption when accessing the site
  - Extremely cheap compared to hosting an actual Angular server
  - Cloudfront caches the files from S3 - we need to invalidate this cache on every git push so that the new files will be served to end users
