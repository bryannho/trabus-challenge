# trabus-challenge

Name: Bryan Ho \
E-mail: bryan.ho16@gmail.com

Coding challenge for Full Stack Engineer role at Trabus Technologies.

## INSTRUCTIONS:

### Data Ingestor

0. Install dependencies \
>>> pip3 install psychopg2

1. Create an account with ElephantSQL, and create a new database instance. \

2. Navigate to the "Details" tab within your new instance. \

3. In your terminal, navigate to the ingestor/ directory. \
>>> cd ingestor

4. Open ingest.py in your code editor \

5. Fill in "DB_NAME, DB_USER, ... DB_PORT" using the information from your "Details" tab on your ElephantSQL DB. \

6. Run ingest.py \
>>> python3 ingest.py

7. In your ElephantSQL instance, navigate to the "Browser" tab and verify the data using:
`SELECT * FROM climate`

