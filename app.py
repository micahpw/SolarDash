import dash
from dash import dcc
from dash import html
import model
import numpy as np

app = dash.Dash(__name__)

SolarFarm = model.SolarFarm()

available_indicators = SolarFarm.Total.columns.values

hist_columns = SolarFarm.Intervals.columns.values

app.layout = html.Div(id='parent', children=[

    html.Div(className='GridWrapper', children=[
        
        
        html.Div(id='Banner', children=[
            html.H1('Welcome to Interactive Plotting with Dash',id='BannerText', title='Welcome to Interactive Plotting with Dash')
        ]),

        #High Level Scatter with Drop-down choices
        html.Div(className='TopLeft', children=[
            
            #Column Configuration  
            html.Div(children=[
            dcc.Dropdown(
                id='TLscatterX',
                #className='scatterX',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value=available_indicators[np.where(available_indicators=='DC_POWER_mean')[0][0]],
                
            ),
            dcc.Dropdown(
                id='TLscatterY',
                #className='scatterY',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value=available_indicators[np.where(available_indicators=='LOSS_PERC_mean')[0][0]],
                
            )], style={'display':'flex'}),
                        
            dcc.Graph(
            id='OverallPerformance',
            hoverData={'points': [{'customdata': SolarFarm.Total.index[0]}]})
        ]),


        ## Histogram of particular key/Inverter

        html.Div(className='TopRight', children=[

            dcc.Dropdown(
                id='InverterX',
                #className='scatterX',
                options=[{'label': i, 'value': i} for i in hist_columns],
                value=hist_columns[np.where(hist_columns=='LOSS_PERC')[0][0]]
                ),
            dcc.Graph(id='InverterHist', hoverData={'points': [{'customdata': SolarFarm.Total.index[0]}]})
        ] ),


    html.Div(className='BottomLeft', children=[
        dcc.Graph(id='InverterDaily')
        ]),
    html.Div(className='BottomRight', children=[
        dcc.Graph(id='InverterRaw'),
    ])


    ])
])



##Callbacks
#Scatter Plot for each inverter
#Daily Bars for production, Irradiance
#Interval plot for bar hover


@app.callback(
    dash.dependencies.Output('OverallPerformance', 'figure'),
    [dash.dependencies.Input('TLscatterX', 'value'),     
     dash.dependencies.Input('TLscatterY', 'value')])
def update_graph(xcol, ycol):
    
    fig = SolarFarm.plotScatter(xcol, ycol)

    return fig


@app.callback(
    dash.dependencies.Output('InverterDaily', 'figure'),
    [dash.dependencies.Input('OverallPerformance', 'hoverData')])
def updateBarGraph(hoverData):
    #key = '4UPUqMRk7TRMgml'
    key = hoverData['points'][0]['customdata'][0]        
    fig = SolarFarm.plotBars(key)    
    return fig


@app.callback(
    dash.dependencies.Output('InverterHist', 'figure'),
    [dash.dependencies.Input('OverallPerformance', 'hoverData'),     
    dash.dependencies.Input('InverterX', 'value')])
def updateHist(hoverData, xcol):
    #key = '4UPUqMRk7TRMgml'
    key = hoverData['points'][0]['customdata'][0]        
    fig = SolarFarm.plotHist(key, xcol)    
    return fig


@app.callback(
    dash.dependencies.Output('InverterRaw', 'figure'),
    [dash.dependencies.Input('InverterDaily', 'hoverData')])
def updateIntervals(hoverData):        
    #key = '4UPUqMRk7TRMgml'
    key = hoverData['points'][0]['customdata'][0]      
    date = hoverData['points'][0]['customdata'][1]          

    fig = SolarFarm.plotIntervals(key, date)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)