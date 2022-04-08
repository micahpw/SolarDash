#High Level Class for representing data

#Class is responsible for loading data and generating graphics

#Each class encapsulates the logic and knowledge behind a particular dataset

import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots
from datetime import datetime
from datetime import timedelta
import plotly.express as px

class SolarFarm():


    def __init__(self):
        self.Intervals, self.Daily, self.Total = self.loadData()        

        super().__init__()


    def loadData(self):
        pwr = pd.read_csv('./data/Plant_2_Generation_Data.csv')
        wtr = pd.read_csv('./data/Plant_2_Weather_Sensor_Data.csv')

        wtr['DATE_TIME'] = pd.to_datetime(wtr['DATE_TIME'])
        pwr['DATE_TIME'] = pd.to_datetime(pwr['DATE_TIME'])

        df = pd.merge(pwr, wtr[['DATE_TIME','PLANT_ID','AMBIENT_TEMPERATURE','MODULE_TEMPERATURE','IRRADIATION']], on=['DATE_TIME','PLANT_ID'])
        df['LOSS'] = df['DC_POWER'] - df['AC_POWER']
        df['LOSS_PERC'] = 100*df['LOSS']/df['DC_POWER']

        daily = df.groupby('SOURCE_KEY').resample('D', on='DATE_TIME').agg({'DAILY_YIELD':'sum','IRRADIATION':'sum', 'AC_POWER':'max','DC_POWER':'max', 'MODULE_TEMPERATURE':['mean','max'], 'LOSS':['max','sum'], 'LOSS_PERC':['max','median','mean']})

        total = df.groupby('SOURCE_KEY').agg({'LOSS_PERC':['mean','median','max'],'MODULE_TEMPERATURE':['mean','max'],'DC_POWER':['mean','max'], 'IRRADIATION':['mean','max']}).reset_index()

        total.columns = ['_'.join(col).strip() for col in total.columns.values]

        df.set_index(['SOURCE_KEY','DATE_TIME'], inplace=True)
        return df, daily, total
                
    
    #Plot Daily Bars based on inverter
    def plotScatter(self, xcol, ycol):        

        fig= px.scatter(self.Total, 
            x=xcol, 
            y=ycol, 
            color='SOURCE_KEY_', 
            opacity=0.8, custom_data=['SOURCE_KEY_'])

        fig.update_layout(
                title=go.layout.Title(text="Aggregate Inverter Stats: {x} vs {y}".format(x=xcol, y=ycol), font=dict(
                family="Times New Roman",
                size=22,
                color="#030303"
        )))

        return fig    
    
    #Plot Bars
    def plotBars(self, SOURCE_KEY):

        inverter = self.Daily.loc[SOURCE_KEY].reset_index()
        inverter['SOURCE_KEY']=SOURCE_KEY #TODO avoid recreating column

        xvals = inverter['DATE_TIME']
        y1 = inverter[('DAILY_YIELD','sum')]
        y2 = inverter[('IRRADIATION','sum')]
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(
        go.Bar(x=xvals, y=y1, name="DAILY_YIELD", customdata=inverter[['SOURCE_KEY','DATE_TIME']]),
        secondary_y=False,
        )

        fig.add_trace(
        go.Scatter(x=xvals, y=y2, name="IRRADIANCE",mode='lines+markers', customdata=inverter[['SOURCE_KEY','DATE_TIME']]),
        secondary_y=True,
        )

        # Add figure title
        fig.update_layout(title=go.layout.Title(text="Daily Yield and Irradiance over Time", font=dict(
                family="Times New Roman",
                size=22,
                color="#030303"
            )))

        # Set x-axis title
        fig.update_xaxes(title_text="Date")

        # Set y-axes titles
        fig.update_yaxes(title_text="<b>Power (kW)</b>", secondary_y=False)
        fig.update_yaxes(title_text="<b>Irradiance</b>", secondary_y=True)

        fig.update_layout(barmode='group')
        return fig


    def plotHist(self,key, column):

        inverter_raw = self.Intervals.loc[key]
        x = inverter_raw[column].values
        
        fig = go.Figure(data=[go.Histogram(x=x, opacity=0.8)])

        #Update Layout
        fig.update_layout(title=go.layout.Title(text="Inverter Distribution: {}".format(column), font=dict(
                family="Times New Roman",
                size=22,
                color="#030303",                
            )))

        fig.update_xaxes(title_text="{}".format(column))

        # Set y-axes titles
        fig.update_yaxes(title_text="<b>Count</b>")        

        return fig

    #Plot the interval data for that particular inverter and date.
    def plotIntervals(self, key, date):
        
        #Parse the input date and get data
        start = datetime.strptime(date,'%Y-%m-%dT%H:%M:%S')
        end = start + timedelta(days=1)
        inverter_raw = self.Intervals.loc[key].loc[start:end]
                            
        
        #Create figure and plot DC, AC and Irradiance values.
        fig = go.Figure()
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.update_layout(title=go.layout.Title(text="Raw Power Output vs Irradiance", font=dict(
                family="Times New Roman",
                size=22,
                color="#030303",                
        )))
        
        fig.add_trace(go.Scatter(x=inverter_raw.index, y=inverter_raw['DC_POWER'],
                    mode='lines',
                    name='DC',                                     
                    ),
                    secondary_y=False)
        fig.add_trace(go.Scatter(x=inverter_raw.index, y=inverter_raw['AC_POWER'],
                    fill='tozeroy',
                    mode='lines',
                    name='AC',                    
                    ),
                    secondary_y=False)

        fig.add_trace(go.Scatter(x=inverter_raw.index, y=inverter_raw['IRRADIATION'],
                    mode='lines',
                    name='IRRADIATION',
                    ),
                    secondary_y=True)
        return fig
    