# trabus-challenge

Name: Bryan Ho \
E-mail: bryan.ho16@gmail.com

Coding challenge for Full Stack Engineer role at Trabus Technologies.

## INSTRUCTIONS:

### Data Ingestor

0. Install dependencies \
    `pip3 install pandas` \
    `pip3 install numpy` \
    `pip3 install psychopg2` \
    `pip3 install plotly==5.14.0` \
    `pip3 install django` \
    `pip3 install django-bootstrap-v5` \

1. Create an account with ElephantSQL, and create a new database instance.

2. Navigate to the "Details" tab within your new instance.

3. From the root directory trabus-challenge, navigate to the ingestor/ directory. \
    `cd ingestor`

4. Open ingest.py in your code editor

5. Fill in "DB_NAME, DB_USER, ... DB_PORT" using the information from your "Details" tab on your ElephantSQL DB.

6. Run ingest.py \
    `python3 ingest.py`

7. In your ElephantSQL instance, navigate to the "Browser" tab and verify the data using: \
    `SELECT * FROM climate`


### Data Analysis

1. From the root directory trabus-challenge, navigate to analysis/ \
    `cd analysis`

2. Open analysis.py in your code editor

3. Fill in "DB_NAME, DB_USER, ... DB_PORT" using the information from your "Details" tab on your ElephantSQL DB.

4. Run analysis.py \
    `python3 analysis.py`


### Data Visualization

1. From the root directory trabus-challenge, navigate to visualization/visApp

2. Open views.py in your code editor

3. Fill in "DB_NAME, DB_USER, ... DB_PORT" using the information from your "Details" tab on your ElephantSQL DB.

4. cd to the root directory trabus-challenge, navigate to visualization/vis
    `cd visualization/vis`

5. Start the Django server
    `python3 manage.py runserver`

6. In your web browser, navigate to `http://localhost:8000/visApp`

