import dash
import pandas as pd
import pickle
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

with open("../sanremo_df.pkl", "rb") as f:
    df = pickle.load(f)

app = dash.Dash()

# Get a list of column names for the dropdown menu
column_options = df.columns
column_dtypes = df.dtypes
numeric_columns = [col for col in column_options if column_dtypes[col] != 'object']

app.layout = html.Div([
    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='Scatter Plot', value='tab-1'),
        dcc.Tab(label='Average Evolution', value='tab-2'),
    ]),
    html.Div(id='tabs-content')
])

@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H1('Scatter Plot'),
            html.Div([
                html.Label('X-axis variable'),
                dcc.Dropdown(
                    id='x-variable',
                    options=[{'label': col, 'value': col} for col in numeric_columns],
                    value='acousticness'
                )
            ], style={'width': '48%', 'display': 'inline-block'}),
            html.Div([
                html.Label('Y-axis variable'),
                dcc.Dropdown(
                    id='y-variable',
                    options=[{'label': col, 'value': col} for col in numeric_columns],
                    value='danceability'
                )
            ], style={'width': '48%', 'display': 'inline-block'}),
            html.Div([
                html.Label('Year'),
                dcc.Dropdown(
                    id='year',
                    options=[
                        {'label': 'All', 'value': 'all'}
                    ]+[
                        {'label': col, 'value': col} for col in df['year'].unique()
                    ],
                    value='all'
                )
            ], style={'width': '48%', 'display': 'inline-block'}),
            dcc.Graph(id='scatter-plot')
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.Label('Variable'),
            dcc.Dropdown(
                id='average-variable',
                options=[{'label': col, 'value': col} for col in df.select_dtypes(include=['float64','int64']).columns],
                value='danceability'
            ),
            dcc.Graph(id='average-evolution')
        ], style={'width': '48%', 'display': 'inline-block'})    

@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('x-variable', 'value'),
     Input('y-variable', 'value'),
     Input('year', 'value')])
def update_figure(x_variable, y_variable, year):
    if x_variable is None or y_variable is None:
        return {'data': [], 'layout': {}}
    else:
        if year != 'all':
            filtered_df = df[df['year'] == year]
        else:
            filtered_df = df
        return {
            'data': [{
                'x': filtered_df[x_variable],
                'y': filtered_df[y_variable],
                'mode': 'markers',
                'text': filtered_df['song'],
                'hoverinfo': 'text',
                'marker': {
                    'color': filtered_df['winner'],
                    'colorscale': 'Viridis',
                    'showscale': True
                }
            }],
            'layout': {
                'xaxis': {'title': x_variable},
                'yaxis': {'title': y_variable}
            }
        }

@app.callback(
    Output('average-evolution', 'figure'),
    [Input('average-variable', 'value')])
def update_average_figure(variable):
    if variable is None:
        return {'data': [], 'layout': {}}
    else:
        average_df = df.groupby("year")[variable].mean().reset_index()
        return {
            'data': [{
                'x': average_df["year"],
                'y': average_df[variable],
                'mode': 'lines',
            }],
            'layout': {
                'xaxis': {'title': "Year"},
                'yaxis': {'title': variable}
            }
        }

if __name__ == '__main__':
    app.run_server(debug=True)

