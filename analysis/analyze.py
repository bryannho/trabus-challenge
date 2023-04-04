import psycopg2
import pandas as pd
import numpy as np
import datetime as dt
import math
import plotly.express as px
import plotly.graph_objects as go

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

# Calculate humidity by applying given equation over all rows
def statsHumidity(df, station):
    df = df.loc[df['station_id'] == station].copy()
    df['H'] = df.apply(humidityEquation, axis=1)
    return df

# Humidity equation
def humidityEquation(row):
    t = row['temperature']
    d = row['dewpoint']
    if t == None or t == 0 or pd.isna(t):
        return None
    if d == None or d == 0 or pd.isna(d):
        return None
    t = 5 / 9 * (t + 459.67)
    d = 5 / 9 * (d + 459.67)
    e = 0.611 * np.exp(5423 * (1/273 - 1/d))
    es = 0.611 * np.exp(5423 * (1/273 - 1/t))
    humidity = 100 * (e / es)
    return humidity

# Calculate monthly avg. temps, rainfall, avg. humidity
def statsMonthly(df, station):
    avgTempsByMonth = []
    sumRainfallByMonth = []
    avgHByMonth = []
    for i in range(1, 13):
        monthIdx = '0' + str(i) if i < 10 else str(i)
        monthBeg, monthEnd = f'2019-{monthIdx}-01 01:00:00 +0000', f'2019-{monthIdx}-31 23:00:00 +0000'
        dfMonth = df[(df['date'].dt.strftime('%Y-%m-%d') >= monthBeg) & (df['date'].dt.strftime('%Y-%m-%d') <= monthEnd)]
        avgTemp = dfMonth['temperature'].sum() / len(dfMonth)
        sumRainfall = dfMonth['precipitation'].sum()
        avgH = dfMonth['H'].sum() / len(dfMonth)
        avgTempsByMonth.append(avgTemp)
        sumRainfallByMonth.append(sumRainfall)
        avgHByMonth.append(avgH)
    return avgTempsByMonth, sumRainfallByMonth, avgHByMonth

# Calculate total rainfall, days above 100F, days below 32F, and average temp
def statsTotal(df, station):
    totalRain = len(df[(df['station_id'] == station) & (df['precipitation'] > 0.0)])
    totalTempHi = len(df[(df['station_id'] == station) & (df['temperature'] > 100)])
    totalTempLo = len(df[(df['station_id'] == station) & (df['temperature'] < 32)])
    totalTempAvg = df.loc[df['station_id'] == station, 'temperature'].mean().round(2)
    return (totalRain, totalTempHi, totalTempLo, totalTempAvg)

# Take only the temperature values at 12:00 each day
def reduceDaily(row):
    if(row['date'].strftime("%H:%M:%S") != "12:00:00"):
        return None
    return 1

# Reduce df to one row for each day
def getDaily(df):
    df['chosen'] = df.apply(reduceDaily, axis=1)
    df = df[df['chosen'].notna()]
    df = df.round(2)
    df = df.sort_values(by=['date'])
    return df

# Plot the temp and humidity as a line graph, marking min/max values as annotations and averages as horizontal lines
def plotLine(df, station):
    # Reduce df to daily values
    df = getDaily(df)
    # Find max/min temp/humidity
    maxTemp = df['temperature'].max()
    maxTempDay = df[df['temperature'] == maxTemp]['date'].iloc[-1]
    minTemp = df['temperature'].min()
    minTempDay = df[df['temperature'] == minTemp]['date'].iloc[-1]
    maxH = df['H'].max()
    maxHDay = df[df['H'] == maxH]['date'].iloc[-1]
    minH = df['H'].min()
    minHDay = df[df['H'] == minH]['date'].iloc[-1]
    # Find avg. temp/humidity
    avgTemp = df['temperature'].mean().round(2)
    avgH = df['H'].mean().round(2)
    # Create line plot
    fig = go.Figure()
    fig.add_scatter(x=df['date'], y=df['temperature'], mode='lines', name='Temperature')
    fig.add_scatter(x=df['date'], y=df['H'], mode='lines', name='Humidity')
    fig.add_annotation(x=maxTempDay, y=maxTemp, text=f'Max Temp: ({maxTemp})', ax=20, ay=-30, bordercolor="#000000", borderwidth=2, borderpad=4, bgcolor="#ffffff")
    fig.add_annotation(x=minTempDay, y=minTemp, text=f'Min Temp: ({minTemp})', ax=20, ay=-30, bordercolor="#000000", borderwidth=2, borderpad=4, bgcolor="#ffffff")
    fig.add_annotation(x=maxHDay, y=maxH, text=f'Max H: ({maxH})', ax=20, ay=-30, bordercolor="#000000", borderwidth=2, borderpad=4, bgcolor="#ffffff")
    fig.add_annotation(x=minHDay, y=minH, text=f'Min H: ({minH})', ax=20, ay=-30, bordercolor="#000000", borderwidth=2, borderpad=4, bgcolor="#ffffff")
    fig.add_hline(y=avgTemp, line_dash='dot', annotation_text=f'Avg. Temperature: {avgTemp}', annotation_font_size=14, line_width=3, line_color='blue')
    fig.add_hline(y=avgH, line_dash='dot', annotation_text=f'Avg. Humidity: {avgH}', annotation_font_size=14, line_width=3, line_color='red')
    if(station == 'kmlb'):
        title = 'Temperature and Humidity in Melbourne, FL'
    else:
        title = 'Temperature and Humidity in San Diego, CA'
    fig.update_layout(title=title, xaxis_title='Date', yaxis_title='Temperature (F) / Humidity (%)')
    fig.show()

# Create bar chart comparing monthly temp/rainfall/humidity between kmlb and ksan
def monthlyBar(monthlies, cat):
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    fig = go.Figure(data=[
        go.Bar(name='Melbourne, FL', x=months, y=monthlies[0]),
        go.Bar(name='San Diego, CA', x=months, y=monthlies[1])
    ])
    title = f'Average Monthly {cat}' if cat != 'Rainfall' else 'Total Monthly Rainfall'
    if(cat == 'Temperature'):
        y_title = 'Temperature (F)'
    elif(cat == 'Rainfall'):
        y_title = 'Rainfall (in)'
    else:
        y_title = 'Humidity (%)'
    fig.update_layout(barmode='group', title=title, xaxis_title='Month', yaxis_title=y_title)
    fig.show()

# Create 3 bar charts comparing monthly temp/rainfall/humidity between kmlb and ksan
def plotBar(temps, rain, humidities):
    monthlyBar(temps, 'Temperature')
    monthlyBar(rain, 'Rainfall')
    monthlyBar(humidities, 'Humidity')

# Conduct total stat analysis, humidity calculation, and monthly stat analysis for a weather station
def analyze(df, station):
    totalStats = statsTotal(df, station)
    print('Total Rainfall, Days above 100F, Days Below 32F, Avg. Temp for station ', station, ': ', totalStats)
    df = statsHumidity(df, station)
    avgTemps, sumRainfall, avgHumidities = statsMonthly(df, station)
    return df, avgTemps, sumRainfall, avgHumidities

# Load data from ElephantSQL database
def loadData():
    cur = conn.cursor()
    query = "SELECT * FROM climate"
    df = pd.read_sql_query(query, conn)
    cur.close()
    return df

def main():
    df = loadData()
    df_kmlb, temps_kmlb, rainfall_kmlb, humidities_kmlb = analyze(df, 'kmlb')
    df_ksan, temps_ksan, rainfall_ksan, humidities_ksan = analyze(df, 'ksan')
    temps = (temps_kmlb, temps_ksan)
    rain = (rainfall_kmlb, rainfall_ksan)
    humidities = (humidities_kmlb, humidities_ksan)
    plotLine(df_kmlb, 'kmlb')
    plotLine(df_ksan, 'ksan')
    plotBar(temps, rain, humidities)
    

if __name__ == "__main__":
    main()
