import re
from typing import Dict

def body_in_event(event: Dict, print_errors=False) -> bool:
    """
    Receives a json object via AWS API Gateway passing the request
    to AWS Lambda and returns whether the dictionary event has a 'body' key in it.
    It will handle errors.
    """
    try:
        # Check if 'body' key exists in the event dictionary
        # Check if event is a dictionary
        if not isinstance(event, dict):
            return False

        return 'body' in event
    except Exception as e:
        # Log the exception if needed, for debugging purposes
        print(f"Error occurred: {e}")

        # Return False if there's an error (can be modified based on how you want to handle errors)
        return False

def valid_formType(body: Dict, print_errors=False) -> bool:
    """
    Receives a body json object and returns whether the key "formType" is in the dictionary keys.
    If it is in the dictionary, it will make sure that the value of formType is either 'contact' or 'quote'.
    """
    try:
        # Check if 'formType' is in the body and its value is either 'contact' or 'quote'
        if 'formType' in body and body['formType'] in ['contact', 'quote']:
            return True
        else:
            # Optionally print error messages
            if print_errors:
                if 'formType' not in body:
                    print("Error: 'formType' key is missing.")
                else:
                    print("Error: 'formType' value is invalid. Must be either 'contact' or 'quote'.")
            return False
    except Exception as e:
        # Optionally print exception error messages
        if print_errors:
            print(f"Error occurred: {e}")
        return False



def email_valid(email):
    # Simple regex for validating an email
    pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    if re.match(pattern, email):
        return True
    else:
        return False
    

def body_lengths_valid(data_dict):
    for key, value in data_dict.items():
        # Check if key is a string and its length
        if not isinstance(key, str) or len(str(key)) >= 50:
            return False

        # Check if value is a string and its length
        if isinstance(value, str):
            if len(value) >= 200:
                return False
        # Check if value is a list, its length, and the length of its items
        elif isinstance(value, list):
            if len(value) > 5 or not all(isinstance(item, str) and len(item) < 50 for item in value):
                return False
        # If value is neither a string nor a list
        else:
            return False

    return True
