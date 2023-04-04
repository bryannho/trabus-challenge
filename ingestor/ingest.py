import sys
import os
import psycopg2

DB_NAME = "********"
DB_USER = "********"
DB_PASSWORD = "********************************"
DB_HOST = "******.db.elephantsql.com"
DB_PORT = "5432"


conn = psycopg2.connect(
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

def createDB():
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS climate (station_id VARCHAR(4), date TIMESTAMP, temperature float, dewpoint float, wind_speed float, precipitation float)");
    cur.execute("INSERT INTO climate VALUES('kmlb', '2019-01-01 01:00:00', 69.0, 67.0, 0.0, 0.0)")
    conn.commit()
    cur.close()

# Connect to DB and insert batch of rows into DB
def insertRowsToDB(values):
    cur = conn.cursor()
    cur.executemany("INSERT INTO climate VALUES(%s, %s, %s, %s, %s, %s)", values)
    conn.commit()
    cur.close()

# Open CSV file, parse values, and insert to DB
def ingestFile(fileName, stationId):
    with open(fileName) as f:
        allValues = []
        for line in f.readlines()[1:]:
            vals = line.strip().split(',')
            for i in range(len(vals)):
                if vals[i] == '':
                    vals[i] = None
            vals.insert(0, stationId)
            allValues.append(vals)
            print('Added: ', vals)
        insertRowsToDB(allValues)

def main():
    # Create DB
    createDB()
    # Read Melbourne, FL climate data and insert into DB
    ingestFile('data/kmlb_hrly_vals_2019.csv', 'kmlb')
    # Read San Diego, CA climate data and insert into DB
    ingestFile('data/ksan_hrly_vals_2019.csv', 'ksan')
    # Close DB connection
    conn.close()

if __name__ == "__main__":
    main()