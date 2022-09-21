import dash
from dash import dcc
from dash import html
from dash.dependencies import Output, Input
import plotly.express as px
import pandas as pd
import requests

def get_magic_price():
    magic_url='https://api.coingecko.com/api/v3/coins/ethereum/contract/0xb0c7a3ba49c7a6eaba6cd4a96c55a1391070ac9a/market_chart/?vs_currency=usd&days=max'
    weth_url='https://api.coingecko.com/api/v3/coins/ethereum/contract/0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2/market_chart/?vs_currency=usd&days=max'
    df = pd.DataFrame()

    magic_dict = {
        'magic': {'url': magic_url, 'contract_address': "0xb0c7a3ba49c7a6eaba6cd4a96c55a1391070ac9a", 'name': 'MAGIC'},
        'weth': {'url': weth_url, 'contract_address': "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", 'name': 'WETH'}
    }

    for k in magic_dict:
        # print(magic_dict[k], k)
        url = magic_dict[k]['url']
        contract_address = magic_dict[k]['contract_address']
        name = magic_dict[k]['name']
        
        response = requests.get(url).json()
    #     response=requests.get(magic_url).json()
        for v in response:
            # print(v, response[v])
            
            new_df = pd.DataFrame(response[v])
            new_df['type']=v
            new_df['name']=name
            new_df['contract_address'] = contract_address
            
            df = pd.concat([df, new_df], axis=0)
    df['datetime']=pd.to_datetime(df[0], unit='ms')
    df['date']=pd.to_datetime(df[0], unit='ms').dt.date
    df=df.rename(columns={0: 'timestamp', 1:'price'})

    df=df[['timestamp', 'datetime', 'date', 'price', 'type', 'name', 'contract_address']]

    min_date_magic = (df[df['name']=='MAGIC'])['date'].min()

    df_magic_mask = df['date'] >= min_date_magic
    df_magic_timeline=df.loc[df_magic_mask].sort_values(['name', 'date'])
# msk = pd.to_datetime(df['date']).dt.date >= min_date_magic
# df_magic_timeline = df[msk]

    return df_magic_timeline



app = dash.Dash(__name__, external_stylesheets=["https://cdn.jsdelivr.net/npm/bootswatch@4.5.2/dist/cyborg/bootstrap.min.css"])

#Layout Section: Bootstrap
#-----------------------------------------------------------------------------------------------------------------------
app.layout = html.Div(
    id='root',
    children=[
        html.H1("Skycatcher - Treasure Ecosystem", style={'textAlign':'left'}),
        html.Br(),
        html.H2("Price, Marketcap, and 24hr Trading Volume of Magic Token"),
        html.Div(
            [
            html.Div([
                html.H1('Column 2'),
                html.P("Select Token:"),
                dcc.Dropdown(id='token_select', options=['MAGIC', 'ETH'],value ='MAGIC')], className='one-half columns'),
                
            html.Div([
                html.H1('Column 1'),
                html.P("Select market segment:"),
                dcc.Dropdown(id='magic-chart-dropdown', options=['Price', 'Marketcap','24hr Volume'],value ='Price')], className='one-half columns'),
        ], className="row", style={'width':'50%', 'margin-left': 'auto', 'margin-right':'auto'}),
        
        html.Div([
            
                    dcc.Graph(id = 'magic-token-graph'),
        ])
        ], className='container', style={'width':'75%', 'margin-left': 'auto', 'margin-right':'auto', 'textAlign': 'center'})
            
                

@app.callback(
    Output("magic-token-graph", "figure"), 
    Input("magic-chart-dropdown", "value"),
    Input('token_select', "value"))
def update_line_chart(value, token_select):
    df = get_magic_price()
    value_map = {'Price':'prices', 'Marketcap':'market_caps', '24hr Volume':'total_volumes', 'ETH':'WETH', 'MAGIC':'MAGIC'}
    value_changed = value_map.get(value)
    selected_token = value_map.get(token_select)

    print(value_changed)
    mask = (df['type'] == value_changed) & (df['name'] == selected_token)
    fig = px.line(df[mask],
                  x='date', y='price', color='name')

    fig.update_xaxes(
        rangeslider_visible=False,
        rangeselector=dict(
        buttons=list([
            dict(count=1, label="1m", step="month", stepmode="backward"),
            dict(count=6, label="6m", step="month", stepmode="backward"),
            dict(count=1, label="YTD", step="year", stepmode="todate"),
            dict(count=1, label="1y", step="year", stepmode="backward"),
            dict(step="all")
            ])
        ))
    fig.update_layout(hovermode="x unified")
    fig.update_traces(hovertemplate="<br>Price: $%{y:,.2f} <br>Date: %{x}")
    
    return fig
    
app.run_server(debug=True)