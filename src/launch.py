from absl import app
from absl import logging

import pandas as pd
import sqlite3
import pycountry
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from country_code_converter import CountryCodeConverter
from database_manager import DatabaseManager

DB_PATH = "hackathon.db"
LIMIT = 50
CHART_TYPE_FREE = "top-free"
CHART_TYPE_PAID = "top-paid"

CSV_PATH_DELIVERIES = "/Users/xlu/Downloads/delivery_data.csv"
CSV_PATH_PLACEMENTS = "/Users/xlu/Downloads/placement_data.csv"
CSV_PATH_PUBLISHER = "/Users/xlu/Downloads/publisher_data.csv"   # PublisherURL data
CSV_PATH_ADVERTISER = "/Users/xlu/Downloads/advertiser_data.csv" # AdvertiserURL data

# New CSV for flow data (AdvertizerURL, PublisherURL, count)
CSV_PATH_FLOW = "/Users/xlu/Downloads/flow_data.csv"  # Replace with actual path

db_manager = DatabaseManager(DB_PATH)

def compute_territory_counts(chart_type, apps):
    data = []
    for app_name in apps:
        countries = db_manager.get_countries_for_app(app_name, chart_type=chart_type, limit=LIMIT)
        icon_url = db_manager.get_app_icon(chart_type, app_name)
        data.append({
            "app_name": app_name,
            "territory_count": len(countries),
            "icon_url": icon_url
        })
    df = pd.DataFrame(data)
    return df

def create_choropleth(chart_type, selected_app):
    if not selected_app:
        fig = px.choropleth(None, locations=[], projection='natural earth')
        fig.update_geos(showframe=False, showcoastlines=True)
        return fig

    countries = db_manager.get_countries_for_app(selected_app, chart_type=chart_type, limit=LIMIT)
    if not countries:
        fig = px.choropleth(None, locations=[], projection='natural earth')
        fig.update_geos(showframe=False, showcoastlines=True)
        return fig

    c = CountryCodeConverter(countries).convert()
    iso_alpha = [country['alpha_3'] for country in c if country['alpha_3']]
    hover_name = [country['name'] for country in c if country['alpha_3']]

    if not iso_alpha:
        fig = px.choropleth(None, locations=[], projection='natural earth')
        fig.update_geos(showframe=False, showcoastlines=True)
        return fig

    df = pd.DataFrame({
        'iso_alpha': iso_alpha,
        'hover_name': hover_name,
        'category': ['Hit']*len(iso_alpha)
    })

    fig = px.choropleth(
        df,
        locations='iso_alpha',
        hover_name='hover_name',
        color='category',
        color_discrete_map={'Hit': '#1f77b4'},
        projection='natural earth',
        title=f"Countries with '{selected_app}' in {chart_type.title().replace('-', ' ')} Apps"
    )

    fig.update_layout(margin={"r":0,"t":50,"l":0,"b":0})
    fig.update_geos(showframe=False, showcoastlines=True)
    return fig

def create_static_histogram(df, chart_title):
    dff = df.copy()
    dff = dff.nlargest(20, 'territory_count')
    dff['color'] = 'lightskyblue'
    fig = px.bar(
        dff,
        x='app_name',
        y='territory_count',
        title=chart_title,
        color='color',
        color_discrete_map={'lightskyblue': 'lightskyblue'},
        labels={'app_name': 'App Name', 'territory_count': 'Territories'}
    )
    fig.update_layout(xaxis={'categoryorder':'total descending'}, showlegend=False)
    return fig

all_apps_free = db_manager.fetch_apps_name_from_all_countries(chart_type=CHART_TYPE_FREE, limit=LIMIT)
all_apps_paid = db_manager.fetch_apps_name_from_all_countries(chart_type=CHART_TYPE_PAID, limit=LIMIT)

territory_counts_df_free = compute_territory_counts(CHART_TYPE_FREE, all_apps_free)
territory_counts_df_paid = compute_territory_counts(CHART_TYPE_PAID, all_apps_paid)

histogram_free_fig = create_static_histogram(territory_counts_df_free, "Number of Territories per Free App (Top 20)")
histogram_paid_fig = create_static_histogram(territory_counts_df_paid, "Number of Territories per Paid App (Top 20)")

# ----- Deliveries Data -----
def load_delivery_data(csv_path=CSV_PATH_DELIVERIES):
    df = pd.read_csv(csv_path)
    df = df[df['GeoCode'].notna() & (df['GeoCode'] != "")]
    df['EventHour'] = pd.to_datetime(df['EventHour'], format='%Y-%m-%d %H', errors='coerce')
    grouped = df.groupby(['EventDate', 'EventHour', 'GeoCode'], as_index=False)['Deliveries'].sum()
    return grouped

delivery_data = load_delivery_data()
max_deliveries = delivery_data['Deliveries'].max()
unique_hours_deliveries = sorted(delivery_data['EventHour'].dropna().unique())
delivery_data['alpha_3'] = delivery_data['GeoCode'].apply(lambda x: CountryCodeConverter([x]).convert()[0]['alpha_3'])

def create_delivery_choropleth(current_hour):
    dff = delivery_data[delivery_data['EventHour'] == current_hour].copy()
    dff = dff.dropna(subset=['alpha_3'])
    if dff.empty:
        fig = px.choropleth(None, locations=[], projection='natural earth')
        fig.update_geos(showframe=False, showcoastlines=True)
        return fig, f"No deliveries for hour {current_hour}"

    fig = px.choropleth(
        dff,
        locations='alpha_3',
        color='Deliveries',
        color_continuous_scale='Reds',
        range_color=(0, max_deliveries), 
        projection='natural earth',
        title=f"Deliveries at hour {current_hour.strftime('%Y-%m-%d %H:%M')}"
    )
    fig.update_layout(margin={"r":0,"t":50,"l":0,"b":0})
    fig.update_geos(showframe=False, showcoastlines=True)
    total_deliveries = dff['Deliveries'].sum()
    info = f"Total Deliveries: {total_deliveries:,} at {current_hour.strftime('%Y-%m-%d %H:%M')}"
    return fig, info

# ----- Placement Data -----
def load_placement_data(csv_path=CSV_PATH_PLACEMENTS):
    df = pd.read_csv(csv_path)
    df = df[df['GeoCode'].notna() & (df['GeoCode'] != "")]
    df['EventHour'] = pd.to_datetime(df['EventHour'], format='%Y-%m-%d %H', errors='coerce')
    grouped = df.groupby(['EventDate', 'EventHour', 'GeoCode'], as_index=False)['PlacementCount'].sum()
    return grouped

placement_data = load_placement_data()
placement_data['alpha_3'] = placement_data['GeoCode'].apply(lambda x: CountryCodeConverter([x]).convert()[0]['alpha_3'])
unique_hours_placement = sorted(placement_data['EventHour'].dropna().unique())
max_placement = placement_data['PlacementCount'].max()

def create_placement_choropleth(current_hour):
    dff = placement_data[placement_data['EventHour'] == current_hour].copy()
    dff = dff.dropna(subset=['alpha_3'])
    if dff.empty:
        fig = px.choropleth(None, locations=[], projection='natural earth')
        fig.update_geos(showframe=False, showcoastlines=True)
        return fig, f"No placements for hour {current_hour}"

    fig = px.choropleth(
        dff,
        locations='alpha_3',
        color='PlacementCount',
        color_continuous_scale='Blues',
        range_color=(0, max_placement),
        projection='natural earth',
        title=f"Placements at hour {current_hour.strftime('%Y-%m-%d %H:%M')}"
    )
    fig.update_layout(margin={"r":0,"t":50,"l":0,"b":0})
    fig.update_geos(showframe=False, showcoastlines=True)
    total_placements = dff['PlacementCount'].sum()
    info = f"Total Placements: {total_placements:,} at {current_hour.strftime('%Y-%m-%d %H:%M')}"
    return fig, info

# ----- PublisherURL Data -----
def load_publisher_data(csv_path=CSV_PATH_PUBLISHER):
    df = pd.read_csv(csv_path)
    df = df[df['GeoCode'].notna() & (df['GeoCode'] != "")]
    df['alpha_3'] = df['GeoCode'].apply(lambda x: CountryCodeConverter([x]).convert()[0]['alpha_3'])
    grouped = df.groupby(['EventDate', 'PublisherURL', 'alpha_3'], as_index=False)['Count'].sum()
    return grouped

publisher_data = load_publisher_data()
unique_urls = publisher_data['PublisherURL'].unique()

def create_publisher_choropleth(publisher_url):
    dff = publisher_data[publisher_data['PublisherURL'] == publisher_url].copy()
    dff = dff.dropna(subset=['alpha_3'])
    if dff.empty:
        fig = px.choropleth(None, locations=[], projection='natural earth')
        fig.update_geos(showframe=False, showcoastlines=True)
        return fig, f"No data for {publisher_url}"

    fig = px.choropleth(
        dff,
        locations='alpha_3',
        color='Count',
        color_continuous_scale='Greens',
        projection='natural earth',
        title=f"Counts for URL: {publisher_url}"
    )
    fig.update_layout(margin={"r":0,"t":50,"l":0,"b":0})
    fig.update_geos(showframe=False, showcoastlines=True)
    total_count = dff['Count'].sum()
    info = f"Total Count: {total_count:,} for {publisher_url}"
    return fig, info

# ----- AdvertiserURL Data -----
def load_advertiser_data(csv_path=CSV_PATH_ADVERTISER):
    df = pd.read_csv(csv_path)
    df = df[df['GeoCode'].notna() & (df['GeoCode'] != "")]
    df['alpha_3'] = df['GeoCode'].apply(lambda x: CountryCodeConverter([x]).convert()[0]['alpha_3'])
    grouped = df.groupby(['EventDate', 'AdvertiserURL', 'alpha_3'], as_index=False)['Count'].sum()
    return grouped

advertiser_data = load_advertiser_data()
unique_advertiser_urls = advertiser_data['AdvertiserURL'].unique()

def create_advertiser_choropleth(advertiser_url):
    dff = advertiser_data[advertiser_data['AdvertiserURL'] == advertiser_url].copy()
    dff = dff.dropna(subset=['alpha_3'])
    if dff.empty:
        fig = px.choropleth(None, locations=[], projection='natural earth')
        fig.update_geos(showframe=False, showcoastlines=True)
        return fig, f"No data for {advertiser_url}"

    fig = px.choropleth(
        dff,
        locations='alpha_3',
        color='Count',
        color_continuous_scale='Purples',  
        projection='natural earth',
        title=f"Counts for Advertiser URL: {advertiser_url}"
    )
    fig.update_layout(margin={"r":0,"t":50,"l":0,"b":0})
    fig.update_geos(showframe=False, showcoastlines=True)
    total_count = dff['Count'].sum()
    info = f"Total Count: {total_count:,} for {advertiser_url}"
    return fig, info

# ----- Flow Data (AdvertizerURL, PublisherURL, count) for Sankey -----
def load_flow_data(csv_path=CSV_PATH_FLOW):
    df = pd.read_csv(csv_path)
    # df:
    # AdvertizerURL, PublisherURL, count
    # Some rows have missing AdvertizerURL or PublisherURL? Filter them out:
    df = df.dropna(subset=["PublisherURL", "count"])  # Keep only rows with PublisherURL and count
    # If AdvertizerURL can be empty, treat them as a separate category or skip?
    # Let's assume we keep rows only where PublisherURL is not empty. If AdvertizerURL is empty, treat as unknown:
    # For simplicity, let's fill empty AdvertizerURL with "Unknown Advertiser"
    df['AdvertizerURL'] = df['AdvertizerURL'].fillna("Unknown Advertiser")
    return df

flow_data = load_flow_data(CSV_PATH_FLOW)

# Create node lists
advertisers = flow_data['AdvertizerURL'].unique().tolist()
publishers = flow_data['PublisherURL'].unique().tolist()

# Create a map from advertiser/publisher to node index
# Let's put all advertisers first, then publishers
advertiser_nodes = advertisers
publisher_nodes = publishers
nodes = advertiser_nodes + publisher_nodes

node_indices = {node: i for i, node in enumerate(nodes)}

source_indices = [node_indices[adv] for adv in flow_data['AdvertizerURL']]
target_indices = [node_indices[pub] for pub in flow_data['PublisherURL']]
values = flow_data['count'].tolist()

sankey_fig = go.Figure(data=[go.Sankey(
    arrangement="snap",
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=nodes,
        color="blue"
    ),
    link=dict(
        source=source_indices,
        target=target_indices,
        value=values
    )
)])
sankey_fig.update_layout(title_text="Advertiser to Publisher Flows", font_size=10)

dash_app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])

dash_app.layout = dbc.Container(
    fluid=True,
    children=[
        html.H1("Top-50 Apps by Territory (Free vs Paid)", className="mt-3 mb-3 text-center"),
        dcc.Interval(id='interval-component', interval=2000, n_intervals=0),

        dbc.Row([
            dbc.Col([
                html.H3("Top-Free Apps"),
                html.Div(id='app-info-free', className="mt-3"),
                html.Img(id='app-icon-free', style={'height': '100px', 'margin-top': '10px'}),
                dcc.Loading(
                    id="loading-map-free",
                    children=[dcc.Graph(id='world-map-free')],
                    type="default"
                ),
                dcc.Graph(figure=histogram_free_fig, id='histogram-free')
            ], width=6),

            dbc.Col([
                html.H3("Top-Paid Apps"),
                html.Div(id='app-info-paid', className="mt-3"),
                html.Img(id='app-icon-paid', style={'height': '100px', 'margin-top': '10px'}),
                dcc.Loading(
                    id="loading-map-paid",
                    children=[dcc.Graph(id='world-map-paid')],
                    type="default"
                ),
                dcc.Graph(figure=histogram_paid_fig, id='histogram-paid')
            ], width=6)
        ], className="mt-4"),

        html.Hr(),

        html.H1("Worldwide Ad Deliveries and Placements Over Time", className="mt-3 mb-3 text-center"),
        dbc.Row([
            dbc.Col([
                html.H3("Deliveries"),
                dcc.Interval(id='delivery-interval', interval=2000, n_intervals=0),
                dcc.Loading(
                    id="loading-delivery-map",
                    children=[dcc.Graph(id='delivery-map')],
                    type="default"
                ),
                html.Div(id='delivery-info', className="mt-3 text-center")
            ], width=6),
            dbc.Col([
                html.H3("Placements"),
                dcc.Interval(id='placement-interval', interval=2000, n_intervals=0),
                dcc.Loading(
                    id="loading-placement-map",
                    children=[dcc.Graph(id='placement-map')],
                    type="default"
                ),
                html.Div(id='placement-info', className="mt-3 text-center")
            ], width=6),
        ], className="mt-4"),

        html.Hr(),

        html.H1("Counts by PublisherURL and AdvertiserURL", className="mt-3 mb-3 text-center"),
        dbc.Row([
            dbc.Col([
                html.H3("PublisherURL"),
                dcc.Interval(id='url-interval', interval=2000, n_intervals=0),
                dcc.Loading(
                    id="loading-url-map",
                    children=[dcc.Graph(id='url-map')],
                    type="default"
                ),
                html.Div(id='url-info', className="mt-3 text-center")
            ], width=6),
            dbc.Col([
                html.H3("AdvertiserURL"),
                dcc.Interval(id='advertiser-interval', interval=2000, n_intervals=0),
                dcc.Loading(
                    id="loading-advertiser-map",
                    children=[dcc.Graph(id='advertiser-map')],
                    type="default"
                ),
                html.Div(id='advertiser-info', className="mt-3 text-center")
            ], width=6),
        ], className="mt-4"),

        html.Hr(),

        # New Sankey diagram for directional flow
        html.H1("Advertiser to Publisher Flows", className="mt-3 mb-3 text-center"),
        dcc.Graph(figure=sankey_fig, id='flow-sankey')
    ]
)

@dash_app.callback(
    Output('world-map-free', 'figure'),
    Output('app-info-free', 'children'),
    Output('app-icon-free', 'src'),
    Output('world-map-paid', 'figure'),
    Output('app-info-paid', 'children'),
    Output('app-icon-paid', 'src'),
    Input('interval-component', 'n_intervals'),
    prevent_initial_call=False
)
def update_maps_and_icons(n):
    current_app_free = all_apps_free[n % len(all_apps_free)] if all_apps_free else None
    current_app_paid = all_apps_paid[n % len(all_apps_paid)] if all_apps_paid else None

    # Free apps
    if current_app_free:
        countries_free = db_manager.get_countries_for_app(current_app_free, chart_type=CHART_TYPE_FREE, limit=LIMIT)
        fig_free = create_choropleth(CHART_TYPE_FREE, current_app_free)
        info_free = f"'{current_app_free}' appears in the top-50 free apps for {len(countries_free)} territories."
        icon_free = territory_counts_df_free.loc[territory_counts_df_free['app_name'] == current_app_free, 'icon_url']
        icon_free = icon_free.iloc[0] if not icon_free.empty else ''
    else:
        fig_free = px.choropleth(None, locations=[], projection='natural earth')
        fig_free.update_geos(showframe=False, showcoastlines=True)
        info_free = "No free apps available."
        icon_free = ''

    # Paid apps
    if current_app_paid:
        countries_paid = db_manager.get_countries_for_app(current_app_paid, chart_type=CHART_TYPE_PAID, limit=LIMIT)
        fig_paid = create_choropleth(CHART_TYPE_PAID, current_app_paid)
        info_paid = f"'{current_app_paid}' appears in the top-50 paid apps for {len(countries_paid)} territories."
        icon_paid = territory_counts_df_paid.loc[territory_counts_df_paid['app_name'] == current_app_paid, 'icon_url']
        icon_paid = icon_paid.iloc[0] if not icon_paid.empty else ''
    else:
        fig_paid = px.choropleth(None, locations=[], projection='natural earth')
        fig_paid.update_geos(showframe=False, showcoastlines=True)
        info_paid = "No paid apps available."
        icon_paid = ''

    return (fig_free, info_free, icon_free,
            fig_paid, info_paid, icon_paid)

@dash_app.callback(
    Output('delivery-map', 'figure'),
    Output('delivery-info', 'children'),
    Input('delivery-interval', 'n_intervals'),
    prevent_initial_call=False
)
def update_delivery_map(n):
    if not unique_hours_deliveries:
        fig = px.choropleth(None, locations=[], projection='natural earth')
        fig.update_geos(showframe=False, showcoastlines=True)
        return fig, "No delivery data available."

    current_hour = unique_hours_deliveries[n % len(unique_hours_deliveries)]
    fig, info = create_delivery_choropleth(current_hour)
    return fig, info

@dash_app.callback(
    Output('placement-map', 'figure'),
    Output('placement-info', 'children'),
    Input('placement-interval', 'n_intervals'),
    prevent_initial_call=False
)
def update_placement_map(n):
    if not unique_hours_placement:
        fig = px.choropleth(None, locations=[], projection='natural earth')
        fig.update_geos(showframe=False, showcoastlines=True)
        return fig, "No placement data available."

    current_hour = unique_hours_placement[n % len(unique_hours_placement)]
    fig, info = create_placement_choropleth(current_hour)
    return fig, info

@dash_app.callback(
    Output('url-map', 'figure'),
    Output('url-info', 'children'),
    Input('url-interval', 'n_intervals'),
    prevent_initial_call=False
)
def update_url_map(n):
    if len(unique_urls) == 0:
        fig = px.choropleth(None, locations=[], projection='natural earth')
        fig.update_geos(showframe=False, showcoastlines=True)
        return fig, "No URL data available."

    current_url = unique_urls[n % len(unique_urls)]
    fig, info = create_publisher_choropleth(current_url)
    return fig, info

@dash_app.callback(
    Output('advertiser-map', 'figure'),
    Output('advertiser-info', 'children'),
    Input('advertiser-interval', 'n_intervals'),
    prevent_initial_call=False
)
def update_advertiser_map(n):
    if len(unique_advertiser_urls) == 0:
        fig = px.choropleth(None, locations=[], projection='natural earth')
        fig.update_geos(showframe=False, showcoastlines=True)
        return fig, "No AdvertiserURL data available."

    current_advertiser_url = unique_advertiser_urls[n % len(unique_advertiser_urls)]
    fig, info = create_advertiser_choropleth(current_advertiser_url)
    return fig, info

def main(argv):
    dash_app.run_server(debug=True)

if __name__ == '__main__':
    app.run(main)
