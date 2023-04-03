import psycopg2
import pandas as pd
import numpy as np
import datetime as dt
import math
import plotly.express as px
import plotly.graph_objects as go

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
# 5. Run queries 4-5 [DONE]
# 6. Run query 6 **TO-DO**
# 7. Run query 7 [DONE]
# 8. Plot everything

def statsHumidity(df, station):
    df = df.loc[df['station_id'] == station].copy()
    df['H'] = df.apply(humidityEquation, axis=1)
    return df

def humidityEquation(row):
    t = row['temperature']
    d = row['dewpoint']
    if t == None or t == 0 or pd.isna(t):
        return None
    if d == None or d == 0 or pd.isna(d):
        return None
    #print(math.exp(17.625 * t * d))
    #t = 5 / 9 * (t - 32)
    numerator = np.longdouble(np.longdouble((17.625 * d)) / 243.04 + d)
    denominator = np.longdouble(np.longdouble((17.625 * t)) / 243.04 + t)
    #print(t, d, numerator, denominator)
    humidity = 100 * (numerator / denominator)
    #rh = 100 * ((112 - 0.1 * t + d) / 112 + 0.9 * t) * 8
    #print(t, d, humidity)
    return humidity

def statsMonthly(df, station):
    avgTempsByMonth = []
    sumRainfallByMonth = []
    avgHByMonth = []
    #df = df[df['station_id'] == station]
    for i in range(1, 13):
        monthIdx = '0' + str(i) if i < 10 else str(i)
        monthBeg, monthEnd = f'2019-{monthIdx}-01 01:00:00 +0000', f'2019-{monthIdx}-31 23:00:00 +0000'
        dfMonth = df[(df['date'].dt.strftime('%Y-%m-%d') >= monthBeg) & (df['date'].dt.strftime('%Y-%m-%d') <= monthEnd)]
        #print(len(dfMonth))
        avgTemp = dfMonth['temperature'].sum() / len(dfMonth)
        sumRainfall = dfMonth['precipitation'].sum()
        avgH = dfMonth['H'].sum() / len(dfMonth)
        avgTempsByMonth.append(avgTemp)
        sumRainfallByMonth.append(sumRainfall)
        avgHByMonth.append(avgH)
        print('For month: ', monthIdx, avgTemp, sumRainfall, avgH)
    return avgTempsByMonth, sumRainfallByMonth, avgHByMonth

    

def statsTotal(df, station):
    totalRain = len(df[(df['station_id'] == station) & (df['precipitation'] > 0.0)])
    totalTempHi = len(df[(df['station_id'] == station) & (df['temperature'] > 100)])
    totalTempLo = len(df[(df['station_id'] == station) & (df['temperature'] < 32)])
    totalTempAvg = df.loc[df['station_id'] == station, 'temperature'].mean()
    return (totalRain, totalTempHi, totalTempLo, totalTempAvg)

def plotLine(df, station):
    df = df.iloc[::24, :]
    df.sort_values(by=['date'])
    maxTemp = df['temperature'].max()
    maxTempDay = df[df['temperature'] == maxTemp]['date'].iloc[-1]
    minTemp = df['temperature'].min()
    minTempDay = df[df['temperature'] == minTemp]['date'].iloc[-1]
    maxH = df['H'].max()
    maxHDay = df[df['H'] == maxH]['date'].iloc[-1]
    minH = df['H'].min()
    minHDay = df[df['H'] == minH]['date'].iloc[-1]
    avgTemp = df['temperature'].mean()
    avgH = df['H'].mean()
    fig = go.Figure()
    fig.add_scatter(x=df['date'], y=df['temperature'], mode='lines+markers', name='Temperature')
    fig.add_scatter(x=df['date'], y=df['H'], mode='lines+markers', name='Humidity')
    #fig.add_annotation(x=df.iloc[df['temperature'].idxmax()]['date'], y=df['temperature'].max(), text='max'
    fig.add_annotation(x=maxTempDay, y=maxTemp, text=f'Max: ({maxTemp})')
    fig.add_annotation(x=minTempDay, y=minTemp, text=f'Min: ({minTemp})')
    fig.add_annotation(x=maxHDay, y=maxH, text=f'Max: ({maxH})')
    fig.add_annotation(x=minHDay, y=minH, text=f'Min: ({minH})')
    fig.add_hline(y=avgTemp, line_dash='dot', annotation_text='Avg. Temperature', fillcolor='green')
    fig.add_hline(y=avgH, line_dash='dot', annotation_text='Avg. Humidity', fillcolor='purple')
    if(station == 'kmlb'):
        title = 'Temperature and Humidity in Melbourne, FL'
    else:
        title = 'Temperature and Humidity in San Diego, CA'
    fig.update_layout(title=title, xaxis_title='Date', yaxis_title='Temperature (F) / Humidity (%)')
    fig.show()

def monthlyBar(monthlies, cat):
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    fig = go.Figure(data=[
        go.Bar(name='Melbourne, FL', x=months, y=monthlies[0]),
        go.Bar(name='San Diego, CA', x=months, y=monthlies[1])
    ])
    fig.update_layout(barmode='group', title=f'Average Monthly {cat}', xaxis_title='Month', yaxis_title=cat)
    fig.show()

def plotBar(temps, rain, humidities):
    monthlyBar(temps, 'Temperature')
    monthlyBar(rain, 'Rainfall')
    monthlyBar(humidities, 'Humidity')


def analyze(df, station):
    totalStats = statsTotal(df, station)
    print('Totals for: ', station, totalStats)
    df = statsHumidity(df, station)
    avgTemps, sumRainfall, avgHumidities = statsMonthly(df, station)
    return df, totalStats, avgTemps, sumRainfall, avgHumidities

    
def loadData():
    cur = conn.cursor()
    query = "SELECT * FROM climate"
    df = pd.read_sql_query(query, conn)
    cur.close()
    return df

def main():
    df = loadData()
    df_kmlb, totals_kmlb, temps_kmlb, rainfall_kmlb, humidities_kmlb = analyze(df, 'kmlb')
    df_ksan, totals_ksan, temps_ksan, rainfall_ksan, humidities_ksan = analyze(df, 'ksan')
    totals = (totals_kmlb, totals_ksan)
    temps = (temps_kmlb, temps_ksan)
    rain = (rainfall_kmlb, rainfall_ksan)
    humidities = (humidities_kmlb, humidities_ksan)
    #plotLine(df_kmlb, 'kmlb')
    #plotLine(df_ksan, 'ksan')
    plotBar(temps, rain, humidities)
    

if __name__ == "__main__":
    main()
