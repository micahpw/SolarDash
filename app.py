import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import model

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)



SolarFarm = model.SolarFarm()


available_indicators = SolarFarm.Total.columns.values

app.layout = html.Div([
    html.Div([

        html.Div([
            dcc.Dropdown(
                id='crossfilter-xaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='Fertility rate, total (births per woman)'
            ),
            dcc.RadioItems(
                id='crossfilter-xaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ],
        style={'width': '49%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='crossfilter-yaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='Life expectancy at birth, total (years)'
            ),
            dcc.RadioItems(
                id='crossfilter-yaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'})
    ], style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(250, 250, 250)',
        'padding': '10px 5px'
    }),

    html.Div([
        dcc.Graph(
            id='OverallPerformance',
            hoverData={'points': [{'customdata': 'Japan'}]}
        )
    ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}),
    html.Div([
        dcc.Graph(id='InverterDaily'),
        dcc.Graph(id='InverterRaw'),
    ], style={'display': 'inline-block', 'width': '49%'}),


])



##Callbacks
#Scatter Plot for each inverter
#Daily Bars for production, Irradiance
#Interval plot for bar hover


@app.callback(
    dash.dependencies.Output('OverallPerformance', 'figure'),
    [dash.dependencies.Input('crossfilter-xaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-yaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-xaxis-type', 'value'),
     dash.dependencies.Input('crossfilter-yaxis-type', 'value')])
def update_graph(xaxis_column_name, yaxis_column_name,
                 xaxis_type, yaxis_type,
                 ):
    
    fig = SolarFarm.plotScatter()

    return fig


@app.callback(
    dash.dependencies.Output('InverterDaily', 'figure'),
    [dash.dependencies.Input('OverallPerformance', 'hoverData'),
     dash.dependencies.Input('crossfilter-xaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-xaxis-type', 'value')])
def update_y_timeseries(hoverData, xaxis_column_name, axis_type):
    #key = '4UPUqMRk7TRMgml'
    key = hoverData['points'][0]['customdata'][0]        
    fig = SolarFarm.plotBars(key)    
    return fig


@app.callback(
    dash.dependencies.Output('InverterRaw', 'figure'),
    [dash.dependencies.Input('InverterDaily', 'hoverData'),
     dash.dependencies.Input('crossfilter-yaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-yaxis-type', 'value')])
def update_x_timeseries(hoverData, yaxis_column_name, axis_type):
    
    
    #key = '4UPUqMRk7TRMgml'
    key = hoverData['points'][0]['customdata'][0]      
    date = hoverData['points'][0]['customdata'][1]      

    

    fig = SolarFarm.plotIntervals(key, date)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)