#!/usr/bin/env python3
"""
Dashboard apps main file
"""

from app import (_config, CaseRequest, StateRequest, ChoroplethMap)

import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import uvicorn
from dash import Dash
from dash.dependencies import Input, Output

state_endpoint = StateRequest()
case_endpoit = CaseRequest()
choropleth = ChoroplethMap()

state_responses = state_endpoint.get_district_data(state_code="Tamil Nadu")  # get_state_data().json()['Tamil Nadu']
state_cases = state_endpoint.get_state_confirmed()  # [state_responses[case]['confirmed'] for case in list(state_responses)]

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

figure = choropleth.generate_map(state_responses)

from flask import Flask

server = Flask(__name__)
APP = Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN], server=server)

APP.title = "COVID-19 TN DashBoard"

APP.layout = html.Div([
    dcc.Interval(
        id='interval_component',
        interval=5 * 60 * 1000,
    ),
    dbc.Row(
        dbc.Col(html.Div(html.H2('Coronavirus Tamil Nadu')), width="auto"), align='center', justify='center'),
    dbc.Card([
        dbc.CardHeader(
            dbc.Tabs(
                [
                    dbc.Tab(label="India", tab_id="tab-1"),
                    dbc.Tab(label="Tamil Nadu", tab_id="tab-2"),
                ],
                id="card-tabs",
                card=True,
                active_tab="tab-1",
            )
        ),
        dbc.CardBody(html.Div(id="card-content"))]),
    dbc.Row([
        dbc.Col(html.Div(
            dcc.Graph(
                id='tamilnadu-bar',
                config={
                    'displayModeBar': False
                }
            ))),
        dbc.Col(html.Div(
            dcc.Graph(
                id='tn-heatmap',
                figure=figure,
                config={
                    'displayModeBar': False
                }

            )))]),

    dbc.Row(html.Span([dbc.Badge("Elanthingal Chandrasekaran", color="light", className="mr-1"),
                       dbc.Badge("Linkedin", href="https://in.linkedin.com/in/elanthingal-chandrasekaran-4ba77b28",
                                 pill=True, color="primary",
                                 className="mr-1"),
                       dbc.Badge("Github", href="https://github.com/Elanthingal", pill=True, color="dark")]),
            justify='center')])


@APP.callback(
    Output("card-content", "children"), [Input("card-tabs", "active_tab")])
def update_tab_content(active_tab):
    if active_tab == 'tab-1':
        output = case_endpoit.get_case_data(state_code='TT')
    else:
        output = case_endpoit.get_case_data(state_code='TN')

    return dbc.Row([
        dbc.Col(html.H4(dbc.Badge(f'Confirmed {output["confirmed"]}', color="danger")), width="auto"),
        dbc.Col(html.H4(dbc.Badge(f'Recovered {output["recovered"]}', color="success")), width="auto"),
        dbc.Col(html.H4(dbc.Badge(f'Active {output["active"]}', color="warning")), width="auto"),
        dbc.Col(html.H4(dbc.Badge(f'Deceased {output["deaths"]}', color="dark")), width="auto")], justify='center')


@APP.callback(Output("tamilnadu-bar", "figure"), [Input("interval_component", "n_intervals")])
def update_bar_chart(n_intervals):
    return {
        'data': [
            {'x': list(state_responses), 'y': state_cases, 'type': 'bar'},
        ],
        'layout': {
            'title': 'Tamil Nadu',
            'height': 400,
            'width': '50%',
            'legend': {'x': 1.02},
        }}


@APP.callback(Output("tn-heatmap", "figure"), [Input("interval_component", "n_intervals")])
def update_heat_map(n_intervals):
    return choropleth.generate_map(state_responses)


if __name__ == '__main__':
    APP.run_server(port=os.getenv("PORT"))
