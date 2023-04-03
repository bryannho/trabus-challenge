import psycopg2
import pandas as pd
import numpy
import datetime as dt

DB_NAME = "ndvenfvc"
DB_USER = "ndvenfvc"
DB_PASSWORD = "ZNh4pWevN2n9xRvJNxLXaMxc-_sxJ6no"
DB_HOST = "mahmud.db.elephantsql.com"
DB_PORT = "5432"

conn = psycopg2.connect(
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

# Notes:
# 1. Connect to DB via psychopg2 [DONE]
# 2. Run SELECT command and read output into pandas def [DONE]
# 3. Run queries 1-3 using Pandas functions [DONE]
# 4. Figure out parsing date values by month [DONE]
# 5. Run queries 4-6 [DONE]
# 6. Run query 7
# 7. Plot everything

def statsMonthly(df, station):
    avgTempsByMonth = []
    sumRainfallByMonth = []
    df = df[df['station_id'] == station]
    for i in range(1, 13):
        sumTemps = 0
        monthIdx = '0' + str(i) if i < 10 else str(i)
        monthBeg, monthEnd = f'2019-{monthIdx}-01 01:00:00 +0000', f'2019-{monthIdx}-31 23:00:00 +0000'
        dfMonth = df[(df['date'].dt.strftime('%Y-%m-%d') >= monthBeg) & (df['date'].dt.strftime('%Y-%m-%d') <= monthEnd)]
        print(len(dfMonth))
        avgTemp = dfMonth['temperature'].sum() / len(dfMonth)
        sumRainfall = dfMonth['precipitation'].sum()
        avgTempsByMonth.append(avgTemp)
        sumRainfallByMonth.append(sumRainfall)
        print('For month: ', monthIdx, avgTemp, sumRainfall)

    

def statsTotal(df, station):
    totalRain = len(df[(df['station_id'] == station) & (df['precipitation'] > 0.0)])
    totalTempHi = len(df[(df['station_id'] == station) & (df['temperature'] > 100)])
    totalTempLo = len(df[(df['station_id'] == station) & (df['temperature'] < 32)])
    totalTempAvg = df.loc[df['station_id'] == station, 'temperature'].mean()
    return totalRain, totalTempHi, totalTempLo, totalTempAvg



def analyze(df, station):
    totalRain, totalTempHi, totalTempLo, totalTempAvg = statsTotal(df, station)
    print('Totals for: ', station, totalRain, totalTempHi, totalTempLo, totalTempAvg)
    statsMonthly(df, station)

def loadData():
    cur = conn.cursor()
    query = "SELECT * FROM climate"
    df = pd.read_sql_query(query, conn)
    cur.close()
    #print(df.head())
    return df

def main():
    df = loadData()
    analyze(df, 'kmlb')
    #analyze(df, 'ksan')
    
    

if __name__ == "__main__":
    main()
