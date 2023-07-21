import os
import pathlib

import dash
from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output, State
import dash_daq as daq
from collections import Counter
import plotly.graph_objs as go
import datetime
from datetime import datetime as dt
from datetime import date
import pandas as pd


app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Remede Dashboard"

server = app.server
app.config["suppress_callback_exceptions"] = True

# Path
APP_PATH = str(pathlib.Path(__file__).parent.resolve())

#### Read data ####
# First Name,Last Name,Certification,Specialty,Work Type,Temp ID,Date/Time Created,Date/Time Modified,First Worked Date,Referral Source,Referred By
temps = pd.read_csv("data/temps23071901_50_00.csv")
# Order ID,Start Date,End Date,Client ID,Order Type,Order Specialty,Client Name,Client Zip,Contact,Temp ID,Client Type
data_types = {
    'Order ID': str,
    'Start Date': str,
    'End Date': str,
    'Client ID': str,
    'Order Type': str,
    'Order Specialty': str,
    'Client Name': str,
    'Client Zip': str,
    'Contact': str,
    'Temp ID': str,
    'Client Type': str,
    'Referral Source': str,
    'Master Client': str
}
orders = pd.read_csv("data/orders23071903_56_57.csv", usecols=range(1,11))
print(orders.head())
# Clients Client ID,Date/Time Created,Status,Client Type,Contract Date,Referral Source,Referred By Name,Master Client
clients = pd.read_csv("data/clients23071904_17_20.csv")

temps['Temp ID'] = temps['Temp ID'].astype(str)
temps['Referral Source'] = temps['Referral Source'].astype(str)
orders['Temp ID'] = orders['Temp ID'].astype(str)
orders['Client ID'] = orders['Client ID'].astype(str)
orders['Client Type'] = orders['Client Type'].astype(str)
orders['Order Type'] =orders['Order Type'].astype(str)
clients['Client ID'] = clients['Client ID'].astype(str)
orders = orders.merge(temps[['Temp ID','Referral Source']], on="Temp ID", how="left")
orders = orders.merge(clients[['Client ID','Master Client']], on="Client ID", how="left")
orders = orders.merge(clients[['Client ID', 'Date/Time Created']], on='Client ID', how='left')

df = pd.DataFrame()
# Extract date only from datetime columns
orders['Start Date'] = pd.to_datetime(orders['Start Date']).dt.date
orders['End Date'] = pd.to_datetime(orders['End Date']).dt.date
orders['Date/Time Created'] = pd.to_datetime(orders["Date/Time Created"], format= '%m/%d/%Y %I:%M %p').dt.date
temps['Date/Time Created'] = pd.to_datetime(temps['Date/Time Created'], format= '%m/%d/%Y %H:%M').dt.date
clients['Date/Time Created'] = pd.to_datetime(clients['Date/Time Created'], format= '%m/%d/%Y %I:%M %p').dt.date

# Compute value counts for each specified column and reset index
start_date_counts = orders['Start Date'].value_counts().reset_index()
end_date_counts = orders['End Date'].value_counts().reset_index()
temps_date_counts = temps['Date/Time Created'].value_counts().reset_index()
clients_date_counts = orders['Date/Time Created'].value_counts().reset_index()

# Rename columns
start_date_counts.columns = ['Dates', 'Start Date Count']
end_date_counts.columns = ['Dates', 'End Date Count']
temps_date_counts.columns = ['Dates', 'Temps Created Date Count']
clients_date_counts.columns = ['Dates', 'Clients Created Date Count']

# Merge all dataframes on 'Dates'
df = pd.merge(start_date_counts, end_date_counts, how='outer', on='Dates')
df = pd.merge(df, temps_date_counts, how='outer', on='Dates')
df = pd.merge(df, clients_date_counts, how='outer', on='Dates')
# Replace NaN values with 0 (if any)
df = df.fillna(0)
# Convert count columns to integers
df[['Start Date Count', 'End Date Count', 'Temps Created Date Count', 'Clients Created Date Count']] = df[['Start Date Count', 'End Date Count', 'Temps Created Date Count', 'Clients Created Date Count']].astype(int)
params = list(df)
suffix_row = "_row"
suffix_button_id = "_button"
suffix_sparkline_graph = "_sparkline_graph"
suffix_count = "_count"
suffix_sd_n = "_sd_number"
suffix_sd_g = "_sd_graph"

def filter_df(df, sourceList, orderTypeList, start_date, end_date, clientTypeList):
    """
    Filter the dataframe based on provided sourceList, orderTypeList, start_date, end_date, and clientTypeList.
    """
    # If any of the lists are None, replace with a list of all unique values in that column
    if sourceList is None:
        sourceList = df['Referral Source'].unique()
    if orderTypeList is None:
        orderTypeList = df['Client ID'].unique()
    if clientTypeList is None:
        clientTypeList = df['Temp ID'].unique()

    # Convert start_date and end_date to datetime if they're string
    if isinstance(start_date, str):
        start_date = pd.to_datetime(start_date)
    if isinstance(end_date, str):
        end_date = pd.to_datetime(end_date)

    # Filter dataframe
    mask = (
        df['Referral Source'].isin(sourceList) & 
        df['Client ID'].isin(orderTypeList) &
        df['Temp ID'].isin(clientTypeList) &
        (df['Dates'] >= start_date) &
        (df['Dates'] <= end_date)
    )
    return df[mask]

def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-text",
                children=[
                    html.H5("Remede Dashboard"),
                    html.H6("KPI reporting"),
                ],
            ),
            html.Div(
                id="banner-logo",
                children=[
                    html.A(
                        html.Button(children="Remede Consulting"),
                        href="https://remedegroup.com/",
                    ),
                    html.Button(
                        id="learn-more-button", children="LEARN MORE", n_clicks=0
                    ),
                    html.A(
                        html.Img(id="logo", src=app.get_asset_url("Remede_New_Aqua_Logo_Use.jpg")),
                        href="https://remedegroup.com/",
                    ),
                ],
            ),
        ],
    )

def build_tab_1():
    return[
        html.Div(
        id="tab-1-container",
        children=html.P("This is the first tab.")
        )
    ]

def build_tabs():
    return html.Div(
        id="tabs",
        className="tabs",
        children=[
            dcc.Tabs(
                id="app-tabs",
                value="tab2",
                className="custom-tabs",
                children=[
                    dcc.Tab(
                        id="Reporting-Tab",
                        label="KPI Reporting",
                        value="tab1",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    dcc.Tab(
                        id="Second-tab",
                        label="Second Tab Test",
                        value="tab2",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                ],
            )
        ],
    )

def build_segment_panel():
    return [
        html.Div(
            id="set-specs-intro-container",
            children=html.P(
                "Used to set segmentation for the rest of the dashboard"
            ),
        ),
        html.Div(
            id="settings-menu",
            children=[
                html.Div(
                    id="referral-select-menu",
                    children=[
                        html.Label(id="referral-select-title",children="Referral Metrics"),
                        html.Br(),
                        dcc.Dropdown(
                            id = "sourceList",
                            options=[{"label": i, "value": i} for i in temps['Referral Source'].unique()],
                            multi = True,
                            placeholder="Select a source(s)",
                        ),  
                    ],  
                ),
                html.Div(
                    id="order-select-menu",
                    children=[
                        html.Label(id="order-select-title",children="Order Metrics"),
                        html.Br(),
                        dcc.Dropdown(
                            id="orderTypeList",
                            options=[{'label': i, "value": i} for i in orders['Order Type'].unique()],
                            multi = True,
                            placeholder="Select an order type(s)",
                        ),  
                    ],  
                ),
                html.Div(
                    id="type-select-menu",
                    children=[
                        html.Label(id="type-select-title",children="Type Metrics"),
                        html.Br(),
                        dcc.Dropdown(
                            id="clientTypeList",
                            options=[{'label': i, "value": i} for i in orders['Client Type'].unique()],
                            multi = True,
                            placeholder="Select a client type(s)"
                        ),  
                    ],
                ),
                html.Div(
                    id="date-select-menu",
                    children=[
                        html.Label(id="date-select-title",children="date Metrics"),
                        html.Br(),
                        dcc.DatePickerRange(
                            id='date-range',
                            min_date_allowed=date(2015,1,1),
                            max_date_allowed=date(2900,1,1),
                            start_date=datetime.datetime.now() - datetime.timedelta(days=7),
                            end_date=datetime.datetime.now()
                        ),  
                    ],
                ),
            ],
        ),
    ],

def generate_piechart():
    return dcc.Graph(
        id="piechart",
        figure={
            "data": [
                {
                    "labels": [],
                    "values": [],
                    "type": "pie",
                    "marker": {"line": {"color": "white", "width": 1}},
                    "hoverinfo": "label",
                    "textinfo": "label",
                }
            ],
            "layout": {
                "margin": dict(l=20, r=20, t=20, b=20),
                "showlegend": True,
                "paper_bgcolor": "rgba(0,0,0,0)",
                "plot_bgcolor": "rgba(0,0,0,0)",
                "font": {"color": "white"},
                "autosize": True,
            },
        },
    )

@app.callback(
    Output('piechart', 'figure'),
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date')])
def update_piechart(start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # filter orders by date range
    filtered_orders = orders[(orders['Start Date'] >= start_date) &
                             (orders['Start Date'] <= end_date)]
    
    # count starts by specialty
    starts_by_specialty = filtered_orders['Order Specialty'].value_counts()

    return {
        "data": [
            {
                "labels": starts_by_specialty.index,
                "values": starts_by_specialty.values,
                "type": "pie",
                "marker": {"line": {"color": "white", "width": 1}},
                "hoverinfo": "label",
                "textinfo": "label+percent",
            }
        ],
        "layout": {
            "margin": dict(l=20, r=20, t=20, b=20),
            "showlegend": True,
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "font": {"color": "white"},
            "autosize": True,
        },
    }

def build_quick_stats_panel():
    return html.Div(
        id="quick-stats",
        className="row",
        children=[
            html.Div(
                id="card-1",
                children=[
                    html.P("Total Starts"),
                    daq.LEDDisplay(
                        id="starts-led",
                        color="#92e0d3",
                        backgroundColor="#1e2130",
                        size=50,
                    ),
                ],
            ),
            html.Div(
                id="card-2",
                children=[
                    html.P("Percent of VMS Dependent Placements"),
                    daq.Gauge(
                        id="progress-guage",
                        max=100,
                        min=0,
                        showCurrentValue=True,
                    ),
                ],
            ),
        ],
    )

@app.callback(
    [Output('starts-led', 'value'), Output('progress-guage', 'value')],
    [
        Input('date-range', 'start_date'),
        Input('date-range', 'end_date'),
    ]
)
def update_quick_stats(start_date, end_date):
    if start_date is None or end_date is None:
        return dash.no_update, dash.no_update

    df = filter_df(orders, start_date, end_date)

    # you would replace the below calculations with your actual calculations
    total_starts = len(df)
    percent_vms = df['Master Client'].mean() * 100  # replace with your actual calculation

    return total_starts, percent_vms
     
def generate_modal():
    return html.Div(
        id="markdown",
        className="modal",
        children=(
            html.Div(
                id="markdown-container",
                className="markdown-container",
                children=[
                    html.Div(
                        className="close-container",
                        children=html.Button(
                            "Close",
                            id="markdown_close",
                            n_clicks=0,
                            className="closeButton",
                        ),
                    ),
                    html.Div(
                        className="markdown-Text",
                        children=dcc.Markdown(
                            children=(
                                """
                        ###### Dashboard Usage
                        This is a dashboard for monitoring Remede Consulting KPI's

                        ###### What does this app shows

                        Use the segmentation control tab to dive into segmented data under the KPI tab

                        To update data replace existing csv files with more recent updates.
                        Export active temps with these fields: First Name,Last Name,Certification,Specialty,Work Type,Temp ID,Date/Time Created,Date/Time Modified,First Worked Date,Referral Source,Referred By
                        Export filled orders with these fields: Order ID,Start Date,End Date,Client ID,Order Type,Order Specialty,Client Name,Client Zip,Contact,Temp ID,Client Type
                        Export active clients with these fields: Clients Client ID,Date/Time Created,Status,Client Type,Contract Date,Referral Source,Referred By Name,Master Client

                        ###### Source Code

                        You can find the source code of this app on our [Github repository](Fill with Github Link).

                    """
                            )
                        ),
                    ),
                ],
            )
        ),
    )

@app.callback(
    Output("markdown", "style"),
    [Input("learn-more-button", "n_clicks"), Input("markdown_close", "n_clicks")],
)
def update_click_output(button_click, close_click):
    ctx = dash.callback_context

    if ctx.triggered:
        prop_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if prop_id == "learn-more-button":
            return {"display": "block"}

    return {"display": "none"}

def build_top_panel(_=None):
    return html.Div(
        id="top-section-container",
        className="row",
        children=[
            html.Div(
                id="metric-summary-session",
                className="row",
                children=[
                    generate_section_banner("Metric Summary"),
                    html.Div(
                        id="metric-div",
                        children=[
                            generate_metric_list_header(),
                            html.Div(
                                id="metric-rows",
                                children=[
                                    generate_metric_row_helper(1),
                                    generate_metric_row_helper(2),
                                    generate_metric_row_helper(3),
                                    generate_metric_row_helper(4),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(
                id="vms-piechart-outer",
                className="four columns",
                children=[
                    generate_section_banner("% Placements with VMS Associateion"),
                    generate_piechart(),
                ],
            ),
        ],
    )

def generate_metric_row_helper(index):
    item=params[index]

    div_id = item + suffix_row
    button_id = item +suffix_button_id
    sparkline_graph_id = item + suffix_sparkline_graph
    count_id = suffix_count
    sd_percentage_id = item + suffix_sd_n
    sd_graph_id = item +suffix_sd_g

    return generate_metric_row(
        div_id,
        None,
        {
            "id": item,
            "className": "metric-row-button-text",
            "children": html.Button(
                id=button_id,
                className="metric-row-button",
                children=item,
                title="click to Deep dive into chart",
                n_clicks=0,
            ),
        },
        {"id": count_id, "children": "0"},
        {
            "id": item + "_sparkline",
            "children": dcc.Graph(
                id= sparkline_graph_id,
                style={"width": "100%", "height": "95%"},
                config={
                    "staticPlot": False,
                    "editable": False,
                    "displayModeBar": False,
                },
            ),
        },
        {"id": sd_percentage_id, "children": "0.00%"},
        {
            "id": sd_graph_id + "container",
            "children": daq.GraduatedBar(
                id=sd_graph_id,
                color={
                    "ranges": {
                        "#92e0d3": [0,3],
                        "#f4d44d": [3,7],
                        "#f45060": [7,15],
                    }
                },
                showCurrentValue=False,
                max=15,
                value=0
            ),
        },
    )


def generate_metric_list_header():
    return generate_metric_row(
        "metric_header",
        {"height": "3rem","margin": "1rem0", "textAlign": "center"},
        {"id": "m_header_1", "children": html.Div("Parameter")},
        {"id": "m_header_2", "children": html.Div("Count")},
        {"id": "m_header_3", "children": html.Div("Sparkline")},
        {"id": "m_header_4", "children": html.Div("1SD")},
        {"id": "m_header_5", "children": html.Div("2SD")},
    )

def generate_metric_row(id,style,col1,col2,col3,col4,col5):
    if style is None:
        style = {"height": "8rem", "width": "100%"}
    return html.Div(
        id=id,
        className="row-metric-row",
        style=style,
        children=[
            html.Div(
                id=col1["id"],
                className="one column",
                style={"margin-right":"2.5rem","minwidth":"50px"},
                children=col1["children"],
            ),
                        html.Div(
                id=col2["id"],
                style={"textAlign": "center"},
                className="one column",
                children=col2["children"],
            ),
            html.Div(
                id=col3["id"],
                style={"height": "100%"},
                className="four columns",
                children=col3["children"],
            ),
            html.Div(
                id=col4["id"],
                style={},
                className="one column",
                children=col4["children"],
            ),
            html.Div(
                id=col5["id"],
                style={"height": "100%", "margin-top": "5rem"},
                className="three columns",
                children=col5["children"],
            ),
        ],
    )

def create_callback(index):
    def callback(sourceList, orderTypeList, start_date, end_date, clientTypeList):
        item = params[index]
        sparkline_graph_id = item + suffix_sparkline_graph

        # Convert start_date and end_date from string to datetime
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        # Filter the dataframe
        filtered_df = filter_df(orders, sourceList, orderTypeList, start_date, end_date, clientTypeList)

        # Group by date and count the orders
        grouped_df = filtered_df.groupby('Dates').size().reset_index(name='counts')

        # Generate the plot data
        trace = go.Scatter(
            x=grouped_df['Dates'],
            y=grouped_df['counts'],
            mode='lines+markers',
            name='Order count',
            line=dict(color='#f4d44d'),
        )

        # Return the figure
        return {
            'data': [trace],
            'layout': {
                "uirevision": True,
                "margin": dict(l=0, r=0, t=4, b=4, pad=0),
                "xaxis": dict(
                    showline=False,
                    showgrid=False,
                    zeroline=False,
                    showticklabels=False,
                ),
                "yaxis": dict(
                    showline=False,
                    showgrid=False,
                    zeroline=False,
                    showticklabels=False,
                ),
                "paper_bgcolor": "rgba(0,0,0,0)",
                "plot_bgcolor": "rgba(0,0,0,0)",
            }
        }
    return callback

for index in range(len(params)):
    item = params[index]
    sparkline_graph_id = item + suffix_sparkline_graph
    app.callback(
        Output(sparkline_graph_id, 'figure'),
        [
            Input('sourceList', 'value'),
            Input('orderTypeList', 'value'),
            Input('date-range', 'start_date'),
            Input('date-range', 'end_date'),
            Input('clientTypeList', 'value')
        ]
    )(create_callback(index))

def generate_section_banner(title):
    return html.Div(className="section-banner", children=title)

def build_chart_panel():
    return html.Div(
        id="control-chart-container",
        className="twelve columns",
        children=[
            generate_section_banner("Dive Down Chart"),
            dcc.Graph(
                id="dive-down-chart",
                figure=go.Figure(
                    {
                        "data":[
                            {
                                "x":[],
                                "y":[],
                                "mode": "lines+markers",
                                "name": params[1],
                            }
                        ],
                        "layout": {
                            "paper_bgcolor": "rgba(0,0,0,0)",
                            "plot_bgcolor": "rgba(0,0,0,0)",
                            "xaxis": dict(
                                showline=False, showgrid=False, zeroline=False
                            ),
                            "yaxis": dict(
                                showgrid=False, showline=False,zeroline=False
                            ),
                            "autosize":True
                        },
                    }
                ),
            ),
        ],
    )

def generate_graph(data,col):
    stats_df=filter_df(data)
    col_data = data["Count"]

@app.callback(
        output=Output("dive-down-chart", "figure"),
        inputs=[
            Input(params[1] + suffix_button_id, "n_clicks"),
            Input(params[2] + suffix_button_id, "n_clicks"),
            Input(params[3] + suffix_button_id, "n_clicks"),
            Input(params[4] + suffix_button_id, "n_clicks"),
        ],
)
def update_control_chart(n1,n2,n3,n4,data,cur_fig):
    ctx = dash.callback_context

    if not ctx.triggered:
        return generate_graph(data,params[1])
    if ctx.triggered:
        splitted = ctx.triggered[0]["prop_id"].split(".")
        prop_id = splitted[0]
        prop_type = splitted[1]

        if prop_type == "n_clicks":
            curr_id = cur_fig["data"][0]["name"]
            prop_id = prop_id[:-4]
            if curr_id == prop_id:
                return generate_graph(data,curr_id)
            else:
                return generate_graph(data,prop_id)
        if prop_type == "n_intervals" and cur_fig is not None:
            curr_id = cur_fig["data"][0]["name"]
            return generate_graph(data, curr_id)
        
@app.callback(
    [Output("app-content", "children")],
    [Input("app-tabs", "value")],
)
def render_tab_content(tab_switch):
    if tab_switch == "tab1":
        return [build_tab_1()],
    return (
        html.Div(
            id="status-container",
            children=[
                build_quick_stats_panel(),
                html.Div(
                    id="graphs-container",
                    children=[build_top_panel(),build_chart_panel(),build_segment_panel()],
                ),
            ],
        ),
    )

app.layout = html.Div(
    id="big-app-container",
    children=[
        build_banner(),
        html.Div(
            id="app-container",
            children=[
                build_tabs(),
                # Main app
                html.Div(id="app-content")
            ],
        ),
        generate_modal(),
    ],
)




if __name__ == "__main__":
       app.run_server(debug=True, port=8050)