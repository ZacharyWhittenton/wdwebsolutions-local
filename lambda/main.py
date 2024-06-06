import json
import re
import html
from typing import Tuple
from helpers.processQuote import QuoteData, get_quote_body, get_quote_template #, FormData
import urllib3
import os
import boto3
from helpers.validations import email_valid, body_in_event, valid_formType
from helpers.verify_captcha import verify_captcha
from helpers.processContact import ContactData, get_contact_body, get_contact_template

#from botocore.vendored import requests
log = print

def main(event, context):
    try:
        log(event)
        log(context)
        log("1. Checking if body in event")
        # 1. See if body is in event
        # if not body_in_event(event, print_errors=True):
        #     return {'statusCode': 400, 'body': json.dumps('Body not in event')}
        form_data = event
        # We know body is in event
        log("2. Check if captchaToken in formData")
        # 2. Check if captchaToken in formData
        if "captchaToken" not in form_data:
            return {'statusCode': 400, 'body': json.dumps('No Captcha Token provided')}
        log("3. Check if captchaToken is valid")
        # 3. Check if captchaToken is valid
        # if not verify_captcha(form_data['captchaToken'], os.environ['reCAPTCHAKey']):
        #     return {'statusCode': 400, 'body': json.dumps('Captcha verification failed')}
        log("4. Check if formType is valid")
        # 4. Check if formType is in form_data
        if not valid_formType(form_data, print_errors=True):
            log("formtype not valid")
            return {'statusCode': 400, 'body': json.dumps('formType not valid')}
        log("5. Checking formtypes")
        # 6a. Process quote submissions
        if form_data["formType"] == "quote":
            log("6a. Processing quote submissions")
            quoteData = QuoteData(**form_data)
            log("6a. Getting quote template")
            template_body = get_quote_template()
            log("6a. Getting quote body")
            email_body = get_quote_body(quoteData, template_body)
            log("6a. Creating subject")
            subject = f"New quote request received from: {quoteData.emailAddress}"
        # 6b. Process contact submissions
        elif form_data["formType"] == "contact":
            log("6a. Processing contact submissions")
            contactData = ContactData(**form_data)
            log("6a. Getting contact template")
            template_body = get_contact_template()
            log("6a. Getting contact body")
            email_body = get_contact_body(contactData, template_body)
            log("6a. Creating subject")
            subject = f"New contact request received from: {contactData.emailAddress}"
        else:
            raise Exception(f"Valid formtype not detected in formdata. Formdata: {form_data}")
        # 7. Send email
        log("7. Sending email")
        send_email(subject, email_body)
        return {'statusCode': 200, 'body': json.dumps('Your request has succeeded')}
    except Exception as e:
        log(e)
        return {'statusCode': 500, 'body': json.dumps('An error occurred while processing your request')}
    
    
def clean_dictionary(dirty_dict):
    cleaned_dict = {}
    
    # Define a regex pattern to match potentially malicious content or unwanted HTML elements
    script_pattern = re.compile(r'<script.*?>.*?</script>', re.IGNORECASE)
    link_pattern = re.compile(r'<a\s+href=.*?>.*?</a>', re.IGNORECASE)
    image_pattern = re.compile(r'<img\s+[^>]+>', re.IGNORECASE)
    style_pattern = re.compile(r'<style.*?>.*?</style>', re.IGNORECASE)
    html_tags_pattern = re.compile(r'<.*?>')

    # Loop through each key-value pair in the dictionary
    for key, value in dirty_dict.items():
        if isinstance(value, str):
            # Remove scripts, links, images, and styles
            value = re.sub(script_pattern, '', value)
            value = re.sub(link_pattern, '', value)
            value = re.sub(image_pattern, '', value)
            value = re.sub(style_pattern, '', value)
            
            # Remove any remaining HTML tags
            value = re.sub(html_tags_pattern, '', value)
            
            # Decode HTML entities
            value = html.unescape(value)
            
            # Trim whitespaces
            value = value.strip()
            
        # Assign the cleaned value back to the dictionary
        cleaned_dict[key] = value
        
    return cleaned_dict

def send_email(subject, email_body):
    ses_client = boto3.client('ses', region_name='us-east-2')

    source_email = 'no-reply@perlasinsurance.com'
    destination_emails = ['jpatrick@perlasinsurance.com']

    try:
        response = ses_client.send_email(
            Source=source_email,
            Destination={'ToAddresses': destination_emails},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Html': {'Data': email_body}}  # Send as HTML
            }
        )
        print("Email sent! Message ID:", response['MessageId'])
    except Exception as e:
        raise Exception(f"Failed to send email: {e}")


if __name__ == "__main__":
    main()