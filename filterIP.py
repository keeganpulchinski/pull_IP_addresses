import boto3
import gzip
import re
import ipinfo
import os
from concurrent.futures import ThreadPoolExecutor

# Initialize AWS S3 client
key_id = os.environ.get('AWS_ACCESS_KEY_ID')
access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
s3 = boto3.client('s3', aws_access_key_id=key_id, aws_secret_access_key=access_key)

# Initialize ipinfo client with your API key
ipinfo_api_key = 'YOUR_IPINFO_API_KEY'
handler = ipinfo.getHandler(api_key=ipinfo_api_key)

# S3 bucket and prefix where your log files are stored
bucket_name = 'logs.keeganpulchinski.net'
prefix = 'logs/'

# Define a regular expression to match both IPv4 and IPv6 addresses
ip_address_pattern = r'\b(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|[0-9a-fA-F:.]+)\b'

# Output file for unique IP addresses with location
output_file = 'ip_addresses.txt'

# Dictionary to store IP addresses and their locations
ip_location_mapping = {}

# List objects in the S3 bucket
objects = s3.list_objects(Bucket=bucket_name, Prefix=prefix)

# Function to extract IP addresses from a log file
def extract_ip_addresses_from_file(file_content):
    return re.findall(ip_address_pattern, file_content)

# Function to get the location based on the IP address
def get_location_from_ip(ip_address):
    try:
        details = handler.getDetails(ip_address)
        return f'{details.city}, {details.region}'
    except ValueError as e:
        # Handle invalid IP addresses or errors
        return 'Unknown'

# Function to process a log file
def process_log_file(obj):
    file_key = obj['Key']
    response = s3.get_object(Bucket=bucket_name, Key=file_key)
    log_content = response['Body'].read()

    # Check if the log file is compressed (e.g., in gzip format) and decompress it if necessary
    if file_key.endswith('.gz'):
        log_content = gzip.decompress(log_content)

    # Extract IP addresses from the log file
    ip_addresses = extract_ip_addresses_from_file(log_content.decode('utf-8'))

    for ip in ip_addresses:
        location = get_location_from_ip(ip)
        if location != 'Unknown':
            ip_location_mapping[ip] = location

# Use ThreadPoolExecutor to parallelize the processing of log files
with ThreadPoolExecutor() as executor:
    executor.map(process_log_file, objects.get('Contents', []))

# Check if the dictionary is not empty before calculating the maximum IP address length
if ip_location_mapping:
    max_ip_length = max(len(ip) for ip in ip_location_mapping.keys())
else:
    max_ip_length = 0

# Write unique IP addresses with locations to the output file
with open(output_file, 'w', encoding='utf-8') as output:
    for ip, location in ip_location_mapping.items():
        padded_ip = ip.ljust(max_ip_length)  # Pad the IP address to make all the same width
        output.write(f'{padded_ip} ---------- {location}\n')

print(f'IP addresses with location extracted and saved to {output_file}')
