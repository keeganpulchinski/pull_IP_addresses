# IP Address Checker for Website
Pulls all of the successful IP address accesses of my website and conglomerates them into a single text file

Normally when CloudFront logs compresses files into an S3 bucket, it is a hassle to open up all of the individual files, download them to my system, open each individual file, and look through all of the information to find things such as hits/misses on resources, 200 status codes or 403 errors. This code allows me to grab all of the successful accesses and inform me of their IP address and their relative location.
