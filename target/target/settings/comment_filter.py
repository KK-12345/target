import re

arrBad=[
    'kill',
    'bitch',
    'basterd',
    'fuck'
    'abuse'
]

def check_bad_comment(description):
    return any(re.findall(r'|'.join(arrBad), description, re.IGNORECASE))
