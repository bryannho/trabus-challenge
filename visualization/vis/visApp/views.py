from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

import pandas as pd
import numpy as np
import datetime as dt
import psycopg2
import plotly.graph_objects as go
from plotly.offline import plot

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

# Main view
def index(request):
    df = loadData()
    temps_kmlb, rain_kmlb = statsMonthly(df, 'kmlb')
    temps_ksan, rain_ksan = statsMonthly(df, 'ksan')
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    plot_temps = monthlyBar((temps_kmlb, temps_ksan), 'Temperature')
    plot_rain = monthlyBar((rain_kmlb, rain_ksan), 'Rainfall')
    context = {
        'rowData': zip(months, temps_kmlb, temps_ksan, rain_kmlb, rain_ksan),
        'plotTemps': plot_temps,
        'plotRain': plot_rain
    }
    return render(request, 'visApp/index.html', context)

def loadData():
    cur = conn.cursor()
    query = "SELECT * FROM climate"
    df = pd.read_sql_query(query, conn)
    cur.close()
    return df

def statsMonthly(df, station):
    avgTempsByMonth = []
    sumRainfallByMonth = []
    df = df[df['station_id'] == station]
    for i in range(1, 13):
        monthIdx = '0' + str(i) if i < 10 else str(i)
        monthBeg, monthEnd = f'2019-{monthIdx}-01 01:00:00 +0000', f'2019-{monthIdx}-31 23:00:00 +0000'
        dfMonth = df[(df['date'].dt.strftime('%Y-%m-%d') >= monthBeg) & (df['date'].dt.strftime('%Y-%m-%d') <= monthEnd)]
        avgTemp = np.round(dfMonth['temperature'].sum() / len(dfMonth), 2)
        sumRainfall = np.round(dfMonth['precipitation'].sum(), 2)
        avgTempsByMonth.append(avgTemp)
        sumRainfallByMonth.append(sumRainfall)
    return avgTempsByMonth, sumRainfallByMonth

def monthlyBar(monthlies, cat):
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    fig = go.Figure(data=[
        go.Bar(name='Melbourne, FL', x=months, y=monthlies[0]),
        go.Bar(name='San Diego, CA', x=months, y=monthlies[1])
    ])
    title = f'Average Monthly {cat}' if cat != 'Rainfall' else 'Total Monthly Rainfall'
    y_axis = 'Temperature (F)' if cat == 'Temperature' else 'Rainfall (in)'
    fig.update_layout(barmode='group', title=title, xaxis_title='Month', yaxis_title=y_axis)
    plt_div = plot(fig, output_type='div', include_plotlyjs=False)
    return plt_div
