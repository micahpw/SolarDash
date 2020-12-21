#High Level Class for representing data

#Class is responsible for loading data and generating graphics

#Each class encapsulates the logic and knowledge behind a particular dataset
#%%
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
        pwr = pd.read_csv('./data/Plant_1_Generation_Data.csv')
        wtr = pd.read_csv('./data/Plant_1_Weather_Sensor_Data.csv')

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
    def plotScatter(self):        



        fig= px.scatter(self.Total, x='DC_POWER_mean', y='LOSS_PERC_mean', color='SOURCE_KEY_', opacity=0.8, custom_data=['SOURCE_KEY_'])
#fig= px.scatter(x=daily['IRRADIATION'], y=daily['DAILY_YIELD'], color='MODULE_TEMPERATURE',  opacity=0.5)
#
        return fig    
    
    #Plot Bars
    def plotBars(self, SOURCE_KEY):

        inverter = self.Daily.loc[SOURCE_KEY].reset_index()
        inverter['SOURCE_KEY']=SOURCE_KEY #TODO avoid recreating column

        xvals = inverter.index
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
        fig.update_layout(
        title_text="Double Y Axis Example"
        )

    # Set x-axis title
        fig.update_xaxes(title_text="xaxis title")

    # Set y-axes titles
        fig.update_yaxes(title_text="<b>primary</b> yaxis title", secondary_y=False)
        fig.update_yaxes(title_text="<b>secondary</b> yaxis title", secondary_y=True)

        fig.update_layout(barmode='group')
        #fig = px.bar(x=inverter.index.values, y=inverter[('DAILY_YIELD','sum')])
        return fig


    def plotIntervals(self, key, date):
        
        start = datetime.strptime(date,'%Y-%m-%dT%H:%M:%S')
        end = start + timedelta(days=1)

        
        
        inverter_raw = self.Intervals.loc[key].loc[start:end]
        
            
        
        
        
        fig = go.Figure()
        fig = make_subplots(specs=[[{"secondary_y": True}]])
      
        
        fig.add_trace(go.Scatter(x=inverter_raw.index, y=inverter_raw['DC_POWER'],
                    mode='lines',
                    name='DC'),
                    secondary_y=False)
        fig.add_trace(go.Scatter(x=inverter_raw.index, y=inverter_raw['AC_POWER'],
                    mode='lines',
                    name='AC'),
                    secondary_y=False)

        fig.add_trace(go.Scatter(x=inverter_raw.index, y=inverter_raw['MODULE_TEMPERATURE'],
                    mode='lines',
                    name='MODULE_TEMPERATURE'),
                    secondary_y=True)
        return fig
    
#%%
#g = SolarFarm()


#key = '4UPUqMRk7TRMgml'

#
#g.Daily.loc[key][('LOSS_PERC','max')].hist(bins=25)



#%%
#fig = g.plotBars(key)#(key, '05-20-2020','05-24-2020')

#fig.show()




# %%
