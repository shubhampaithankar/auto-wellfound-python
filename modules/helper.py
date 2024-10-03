import re

def get_proper_string(value: str) -> str: 
    return '\n'.join([' '.join(line.split()) for line in value.splitlines()]).strip().lower()
