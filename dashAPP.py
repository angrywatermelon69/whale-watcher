# Import required libraries
import datetime as dt
import json
import csv
import schedule
import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
from math import log10, floor, isnan
import numpy as np
import logging
from logging.handlers import RotatingFileHandler
from decimal import Decimal
from bitmex_book import BitMEXBook

# Creating webapp
app = dash.Dash(__name__)
server = app.server

# creating variables to facilitate later parameterization
ws = BitMEXBook()
tables = {}
depth_ask = {}
depth_bid = {}
marketPrice = {}
shape_bid = {}
shape_ask = {}
timeStampsGet = {}  
timeStamps = {}  

TBL_PRICE = 'price'
TBL_VOLUME = 'volume'
ticker = 'XBTUSD'
exchange = 'BitMEX'
combined = exchange + ticker
symbol = '$'
base_currency = 'USD'
currency = 'BTC'
SIGNIFICANT = {"USD": 2, "BTC": 5}
DATA_DIR = 'data/'
sig_use = SIGNIFICANT.get(base_currency.upper(), 2)
noDouble = True
clientRefresh = 5

def setup_db(name, extension='.csv', getPath = False):
    """Setup writer that formats data to csv, supports multiple instances with no overlap."""
    formatter = logging.Formatter(fmt='%(asctime)s,%(message)s', datefmt='%d-%m-%y,%H:%M:%S')
    date = dt.datetime.today().strftime('%Y-%m-%d')
    db_path = str(DATA_DIR + name + '/' + name + '_' + date + extension)

    handler = RotatingFileHandler(db_path, backupCount=1)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if (logger.hasHandlers()):
        logger.handlers.clear()
        logger.addHandler(handler)
    else:
        logger.addHandler(handler)
    
    if getPath:
        return logger, db_path
    else:
        return logger

def update_today():
    today = dt.datetime.today().strftime('%Y-%m-%d')
    return 
schedule.every(60).seconds.do(update_today)

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(
        l=30,
        r=30,
        b=20,
        t=40
    ),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor='#F9F9F9',
    legend=dict(font=dict(size=10), orientation='h'),
    title='Dashboard - Running',
)

# Create app layout
app.layout = html.Div(
    [
        dcc.Store(id='aggregate_data'),

        # Header
        html.Div(
            [
                html.Div(
                    [
                        html.H2(
                            'Pyno - Dashboard V0',
                            style={'padding-left':'65px',
                                    'padding-top' : '20px'}

                        ),
                        html.H5(
                            'Running Instance Stats',
                            style={'padding-left':'65px',
                                    'font-size': '1.5rem'}
                        ),
                        html.H5(
                            id = 'timestamp',
                            style={'padding-left':'65px',
                                    'font-size': '1.5rem'}
                        ),
                    ],

                    className='eight columns'
                ),
                html.A(
                    html.Button(
                        "Learn More",
                        id="learnMore"
                    ),
                    href="https://quan.digital",
                    className="two columns"
                )
            ],
            id="header",
            className='row',
        ),

        # Upper page components
        html.Div(
            [
                
                html.Div(
                    [   
                        # First info row
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.P("Symbol"),
                                        html.H6(
                                            id="symbol",
                                            className="info_text"
                                        )
                                    ],
                                    id="",
                                    className="pretty_container"
                                ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.P("State"),
                                        html.H6(
                                            id="state",
                                            className="info_text"
                                        )
                                    ],
                                    id="",
                                    className="pretty_container"
                                ),

                                html.Div(
                                    [
                                        html.P("Previous Close Price"),
                                        html.H6(
                                            id="prevClosePrice",
                                            className="info_text"
                                        )
                                    ],
                                    id="",
                                    className="pretty_container"
                                ),

                                html.Div(
                                    [
                                        html.P("Volume"),
                                        html.H6(
                                            id="volume",
                                            className="info_text"
                                        )
                                    ],
                                    id="",
                                    className="pretty_container"
                                ),

                                html.Div(
                                    [
                                        html.P("Volume 24h"),
                                        html.H6(
                                            id="volume24h",
                                            className="info_text"
                                        )
                                    ],
                                    id="",
                                    className="pretty_container"
                                ),

                                html.Div(
                                    [
                                        html.P("Turn Over"),
                                        html.H6(
                                            id="turnover",
                                            className="info_text"
                                        )
                                    ],
                                    id="",
                                    className="pretty_container"
                                ),

                                html.Div(
                                    [
                                        html.P("Turn Over 24h"),
                                        html.H6(
                                            id="turnover24h",
                                            className="info_text"
                                        )
                                    ],
                                    id="",
                                    className="pretty_container"
                                ),

                            ],
                            id="btcInfo",
                            className="row"
                        ),

                        # Second info row
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.P("High Price"),
                                        html.H6(
                                            id="highPrice",
                                            className="info_text"
                                        )
                                    ],
                                    id="",
                                    className="pretty_container"
                                ),

                                html.Div(
                                    [
                                        html.P("Low Price"),
                                        html.H6(
                                            id="lowPrice",
                                            className="info_text"
                                        )
                                    ],
                                    id="",
                                    className="pretty_container"
                                ),

                                html.Div(
                                    [
                                        html.P("Last Price"), 
                                        html.H6(
                                            id="lastPrice",
                                            className="info_text"
                                        )
                                    ],
                                    id="",
                                    className="pretty_container"
                                ),

                                html.Div(
                                    [
                                        html.P("Bid Price"), 
                                        html.H6(
                                            id="bidPrice",
                                            className="info_text"
                                        )
                                    ],
                                    id="",
                                    className="pretty_container"
                                ),

                                html.Div(
                                    [
                                        html.P("Mid Price"), 
                                        html.H6(
                                            id="midPrice",
                                            className="info_text"
                                        )
                                    ],
                                    id="",
                                    className="pretty_container"
                                ),

                                html.Div(
                                    [
                                        html.P("Ask Price"),
                                        html.H6(
                                            id="askPrice",
                                            className="info_text"
                                        )
                                    ],
                                    id="",
                                    className="pretty_container"
                                ),

                                html.Div(
                                    [
                                        html.P("Open Interest"),
                                        html.H6(
                                            id="openInterest",
                                            className="info_text"
                                        )
                                    ],
                                    id="",
                                    className="pretty_container"
                                ),
                                html.Div(
                                    [
                                        html.P("Open Value"),
                                        html.H6(
                                            id="openValue",
                                            className="info_text"
                                        )
                                    ],
                                    id="",
                                    className="pretty_container"
                                ),
                                html.Div(
                                    [
                                        html.P("Mark Price"),
                                        html.H6(
                                            id="markPrice",
                                            className="info_text"
                                        )
                                    ],
                                    id="",
                                    className="pretty_container"
                                ),

                            ],
                            id="infoContainer",
                            className="row"
                        ),

                        # graph overtime plot
                        html.Div(id='whale_graph', 
                        children =[ 
                            dcc.Graph(id='live-graph-' + exchange + "-" + ticker)
                            ],
                            className="pretty_container"
                        )
                    ]
                )
            ] 
        ),
        html.Div([
            html.Div([
                html.P("Whales spotted today"),
                html.H6(
                    className="info_text",
                    id = "whales_soitted",
                    style={'whiteSpace': 'pre-wrap'}
                                )
                            ],
                            className="pretty_container"
                        ),
                    ],
                    className="pretty_container five columns"
                ),
                # Footer
                html.Div(
                    [
                    html.P(
                    'Designed by canokaue',
                    style={
                            # 'padding-left':'65px',
                            'font-size': '1.5rem',
                            'color': '#b5c6cc',
                            'align': 'left',
                            }
                        ),

                    html.P(
                    'Pyno Dashboard v0.1 - © Quan Digital 2020',
                    style={
                        'padding-left':'165px',
                            'font-size': '1.5rem',
                            'color': '#b5c6cc',
                            'align': 'left',
                            }
                        ),
                    ], 
                    id = 'footer',
                    className="row"
                    ),

                    # Update loop component 
                    dcc.Interval(
                        id='interval-component',
                        interval=clientRefresh*1000,  
                        n_intervals=0
                    )
                ],
                id="mainContainer",
                style={
                    "display": "flex",
                    "flex-direction": "column"
                },
            )
        ]
    )

def fixNan(x, pMin=True):
    if isnan(x):
      if pMin:
         return 99999
      else:
         return 0
    else:
      return x

def calcColor(x):
    response = round(400 / x)
    if response > 255:
        response = 255
    elif response < 30:
        response = 30
    return response

def round_sig(x, sig=3, overwrite=0, minimum=0):
    if (x == 0):
        return 0.0
    elif overwrite > 0:
        return round(x, overwrite)
    else:
        digits = -int(floor(log10(abs(x)))) + (sig - 1)
        if digits <= minimum:
            return round(x, minimum)
        else:
            return round(x, digits)

def calc_data(range=0.05, maxSize=32, minVolumePerc=0.01, ob_points=60):

    order_book = ws.get_current_book()
    ask_tbl = pd.DataFrame(data=order_book['asks'], columns=[
                TBL_PRICE, TBL_VOLUME, 'address'])
    bid_tbl = pd.DataFrame(data=order_book['bids'], columns=[
                TBL_PRICE, TBL_VOLUME, 'address'])

    timeStampsGet[combined] = dt.datetime.now().strftime("%H:%M:%S")

    # prepare Price
    ask_tbl[TBL_PRICE] = pd.to_numeric(ask_tbl[TBL_PRICE])
    bid_tbl[TBL_PRICE] = pd.to_numeric(bid_tbl[TBL_PRICE])

    # data from websocket are not sorted yet
    ask_tbl = ask_tbl.sort_values(by=TBL_PRICE, ascending=True)
    bid_tbl = bid_tbl.sort_values(by=TBL_PRICE, ascending=False)

    # get first on each side
    first_ask = float(ask_tbl.iloc[1, 0])

    # get perc for ask/ bid
    perc_above_first_ask = ((1.0 + range) * first_ask)
    perc_above_first_bid = ((1.0 - range) * first_ask)

    # limits the size of the table so that we only look at orders 5% above and under market price
    ask_tbl = ask_tbl[(ask_tbl[TBL_PRICE] <= perc_above_first_ask)]
    bid_tbl = bid_tbl[(bid_tbl[TBL_PRICE] >= perc_above_first_bid)]

    # changing this position after first filter makes calc faster
    bid_tbl[TBL_VOLUME] = pd.to_numeric(bid_tbl[TBL_VOLUME])
    ask_tbl[TBL_VOLUME] = pd.to_numeric(ask_tbl[TBL_VOLUME]) 

    # prepare everything for depchart
    ob_step = (perc_above_first_ask - first_ask) / ob_points
    ob_ask = pd.DataFrame(columns=[TBL_PRICE, TBL_VOLUME, 'address', 'text'])
    ob_bid = pd.DataFrame(columns=[TBL_PRICE, TBL_VOLUME, 'address', 'text'])

    # Following is creating a new tbl 'ob_bid' which contains the summed volume and adress-count from current price to target price
    i = 1
    last_ask = first_ask
    last_bid = first_ask
    current_ask_volume = 0
    current_bid_volume = 0
    current_ask_adresses = 0
    current_bid_adresses = 0
    while i < ob_points:
        # Get Borders for ask/ bid
        current_ask_border = first_ask + (i * ob_step)
        current_bid_border = first_ask - (i * ob_step)

        # Get Volume
        current_ask_volume += ask_tbl.loc[
            (ask_tbl[TBL_PRICE] >= last_ask) & (ask_tbl[TBL_PRICE] < current_ask_border), TBL_VOLUME].sum()
        current_bid_volume += bid_tbl.loc[
            (bid_tbl[TBL_PRICE] <= last_bid) & (bid_tbl[TBL_PRICE] > current_bid_border), TBL_VOLUME].sum()

        # Get Adresses
        current_ask_adresses += ask_tbl.loc[
            (ask_tbl[TBL_PRICE] >= last_ask) & (ask_tbl[TBL_PRICE] < current_ask_border), 'address'].count()
        current_bid_adresses += bid_tbl.loc[
            (bid_tbl[TBL_PRICE] <= last_bid) & (bid_tbl[TBL_PRICE] > current_bid_border), 'address'].count()

        # Prepare Text
        ask_text = (str(round_sig(current_ask_volume, 3, 0, sig_use)) + currency + " (from " + str(current_ask_adresses) +
                        " orders) up to " + str(round_sig(current_ask_border, 3, 0, sig_use)) + symbol)
        bid_text = (str(round_sig(current_bid_volume, 3, 0, sig_use)) + currency + " (from " + str(current_bid_adresses) +
                        " orders) down to " + str(round_sig(current_bid_border, 3, 0, sig_use)) + symbol)

        # Save Data
        ob_ask.loc[i - 1] = [current_ask_border, current_ask_volume, current_ask_adresses, ask_text]
        ob_bid.loc[i - 1] = [current_bid_border, current_bid_volume, current_bid_adresses, bid_text]
        i += 1
        last_ask = current_ask_border
        last_bid = current_bid_border

    # Get Market Price
    mp = round_sig(ws.get_market_price(),3, 0, sig_use)
    
    bid_tbl = bid_tbl.iloc[::-1]  # flip the bid table so that the merged full_tbl is in logical order

    fulltbl = bid_tbl.append(ask_tbl)  # append the buy and sell side tables to create one cohesive table
    minVolume = fulltbl[TBL_VOLUME].sum() * minVolumePerc  # Calc minimum Volume for filtering
    fulltbl = fulltbl[
        (fulltbl[TBL_VOLUME] >= minVolume)]  # limit our view to only orders greater than or equal to the minVolume size

    fulltbl['sqrt'] = np.sqrt(fulltbl[
                                    TBL_VOLUME])  # takes the square root of the volume (to be used later on for the purpose of sizing the order bubbles)

    final_tbl = fulltbl.groupby([TBL_PRICE])[
        [TBL_VOLUME]].sum()  # transforms the table for a final time to craft the data view we need for analysis

    final_tbl['n_unique_orders'] = fulltbl.groupby(
        TBL_PRICE).address.nunique().astype(int)

    final_tbl = final_tbl[(final_tbl['n_unique_orders'] <= 20.0)]
    final_tbl[TBL_PRICE] = final_tbl.index
    final_tbl[TBL_PRICE] = final_tbl[TBL_PRICE].apply(round_sig, args=(3, 0, sig_use))
    final_tbl[TBL_VOLUME] = final_tbl[TBL_VOLUME].apply(round_sig, args=(1, 2))
    final_tbl['n_unique_orders'] = final_tbl['n_unique_orders'].apply(round_sig, args=(0,))
    final_tbl['sqrt'] = np.sqrt(final_tbl[TBL_VOLUME])
    final_tbl['total_price'] = (((final_tbl['volume'] * final_tbl['price']).round(2)).apply(lambda x: "{:,}".format(x)))

    # Following lines fix double drawing of orders in case it´s a ladder but bigger than 1%
    if noDouble:
        bid_tbl = bid_tbl[(bid_tbl['volume'] < minVolume)]
        ask_tbl = ask_tbl[(ask_tbl['volume'] < minVolume)]

    bid_tbl['total_price'] = bid_tbl['volume'] * bid_tbl['price']
    ask_tbl['total_price'] = ask_tbl['volume'] * ask_tbl['price']

    # Get Dataset for Volume Grouping
    vol_grp_bid = bid_tbl.groupby([TBL_VOLUME]).agg(
        {TBL_PRICE: [np.min, np.max, 'count'], TBL_VOLUME: np.sum, 'total_price': np.sum})
    vol_grp_ask = ask_tbl.groupby([TBL_VOLUME]).agg(
        {TBL_PRICE: [np.min, np.max, 'count'], TBL_VOLUME: np.sum, 'total_price': np.sum})

    # Rename column names for Volume Grouping
    vol_grp_bid.columns = ['min_Price', 'max_Price', 'count', TBL_VOLUME, 'total_price']
    vol_grp_ask.columns = ['min_Price', 'max_Price', 'count', TBL_VOLUME, 'total_price']

    # Filter data by min Volume, more than 1 (intefere with bubble), less than 70 (mostly 1 or 0.5 ETH humans)
    vol_grp_bid = vol_grp_bid[
        ((vol_grp_bid[TBL_VOLUME] >= minVolume) & (vol_grp_bid['count'] >= 2.0) & (vol_grp_bid['count'] < 70.0))]
    vol_grp_ask = vol_grp_ask[
        ((vol_grp_ask[TBL_VOLUME] >= minVolume) & (vol_grp_ask['count'] >= 2.0) & (vol_grp_ask['count'] < 70.0))]

    # Get the size of each order
    vol_grp_bid['unique'] = vol_grp_bid.index.get_level_values(TBL_VOLUME)
    vol_grp_ask['unique'] = vol_grp_ask.index.get_level_values(TBL_VOLUME)

    # Round the size of order
    vol_grp_bid['unique'] = vol_grp_bid['unique'].apply(round_sig, args=(3, 0, sig_use))
    vol_grp_ask['unique'] = vol_grp_ask['unique'].apply(round_sig, args=(3, 0, sig_use))

    # Round the Volume
    vol_grp_bid[TBL_VOLUME] = vol_grp_bid[TBL_VOLUME].apply(round_sig, args=(1, 0, sig_use))
    vol_grp_ask[TBL_VOLUME] = vol_grp_ask[TBL_VOLUME].apply(round_sig, args=(1, 0, sig_use))

    # Round the Min/ Max Price
    vol_grp_bid['min_Price'] = vol_grp_bid['min_Price'].apply(round_sig, args=(3, 0, sig_use))
    vol_grp_ask['min_Price'] = vol_grp_ask['min_Price'].apply(round_sig, args=(3, 0, sig_use))
    vol_grp_bid['max_Price'] = vol_grp_bid['max_Price'].apply(round_sig, args=(3, 0, sig_use))
    vol_grp_ask['max_Price'] = vol_grp_ask['max_Price'].apply(round_sig, args=(3, 0, sig_use))

    # Round and format the Total Price
    vol_grp_bid['total_price'] = (vol_grp_bid['total_price'].round(sig_use).apply(lambda x: "{:,}".format(x)))
    vol_grp_ask['total_price'] = (vol_grp_ask['total_price'].round(sig_use).apply(lambda x: "{:,}".format(x)))

    # Append individual text to each element
    vol_grp_bid['text'] = ("There are " + vol_grp_bid['count'].map(str) + " orders " + vol_grp_bid['unique'].map(
            str) + " " + currency +
                            " each, from " + symbol + vol_grp_bid['min_Price'].map(str) + " to " + symbol +
                            vol_grp_bid['max_Price'].map(str) + " resulting in a total of " + vol_grp_bid[
                                TBL_VOLUME].map(str) + " " + currency + " worth " + symbol + vol_grp_bid[
                                'total_price'].map(str))
    vol_grp_ask['text'] = ("There are " + vol_grp_ask['count'].map(str) + " orders " + vol_grp_ask['unique'].map(
        str) + " " + currency +
                            " each, from " + symbol + vol_grp_ask['min_Price'].map(str) + " to " + symbol +
                            vol_grp_ask['max_Price'].map(str) + " resulting in a total of " + vol_grp_ask[
                                TBL_VOLUME].map(str) + " " + currency + " worth " + symbol + vol_grp_ask[
                                'total_price'].map(str))

    # Save data global
    shape_ask[combined] = vol_grp_ask
    shape_bid[combined] = vol_grp_bid

    cMaxSize = final_tbl['sqrt'].max()  # Fixing Bubble Size

    # nifty way of ensuring the size of the bubbles is proportional and reasonable
    sizeFactor = maxSize / cMaxSize
    final_tbl['sqrt'] = final_tbl['sqrt'] * sizeFactor

    # making the tooltip column for our charts
    final_tbl['text'] = (
                "There is a " + final_tbl[TBL_VOLUME].map(str) + " " + currency + " order for " + symbol + final_tbl[
            TBL_PRICE].map(str) + " being offered by " + final_tbl['n_unique_orders'].map(
            str) + " unique orders worth " + symbol + final_tbl['total_price'].map(str))

    # determine buys / sells relative to last market price; colors price bubbles based on size
    # Buys are green, Sells are Red. Probably WHALES are highlighted by being brighter, detected by unqiue order count.
    final_tbl['colorintensity'] = final_tbl['n_unique_orders'].apply(calcColor)
    final_tbl.loc[(final_tbl[TBL_PRICE] > mp), 'color'] = \
        'rgb(' + final_tbl.loc[(final_tbl[TBL_PRICE] >
                                mp), 'colorintensity'].map(str) + ',0,0)'
    final_tbl.loc[(final_tbl[TBL_PRICE] <= mp), 'color'] = \
        'rgb(0,' + final_tbl.loc[(final_tbl[TBL_PRICE]
                                    <= mp), 'colorintensity'].map(str) + ',0)'

    timeStamps[combined] = timeStampsGet[combined]  # now save timestamp of calc start in timestamp used for title

    tables[combined] = final_tbl  # save table data

    marketPrice[combined] = mp  # save market price

    depth_ask[combined] = ob_ask
    depth_bid[combined] = ob_bid
    
    data = tables[combined]
    ob_ask = depth_ask[combined]
    ob_bid = depth_bid[combined]
    #Get Minimum and Maximum
    ladder_Bid_Min = fixNan(shape_bid[combined]['volume'].min())
    ladder_Bid_Max = fixNan(shape_bid[combined]['volume'].max(), False)
    ladder_Ask_Min = fixNan(shape_ask[combined]['volume'].min())
    ladder_Ask_Max = fixNan(shape_ask[combined]['volume'].max(), False)
    data_min = fixNan(data[TBL_VOLUME].min())
    data_max = fixNan(data[TBL_VOLUME].max(), False)
    ob_bid_max = fixNan(ob_bid[TBL_VOLUME].max(), False)
    ob_ask_max = fixNan(ob_ask[TBL_VOLUME].max(), False)

    x_min = min([ladder_Bid_Min, ladder_Ask_Min, data_min])
    x_max = max([ladder_Bid_Max, ladder_Ask_Max, data_max, ob_ask_max, ob_bid_max])
    max_unique = max([fixNan(shape_bid[combined]['unique'].max(), False),
                        fixNan(shape_ask[combined]['unique'].max(), False)])
    width_factor = 15
    if max_unique > 0: width_factor = 15 / max_unique
    market_price = marketPrice[combined]
    bid_trace = go.Scatter(
        x=[], y=[],
        text=[],
        mode='markers', hoverinfo='text',
        marker=dict(opacity=0, color='rgb(0,255,0)'))
    ask_trace = go.Scatter(
        x=[], y=[],
        text=[],
        mode='markers', hoverinfo='text',
        marker=dict(opacity=0, color='rgb(255,0,0)'))
    shape_arr = [dict(
        # Line Horizontal
        type='line',
        x0=x_min * 0.5, y0=market_price,
        x1=x_max * 1.5, y1=market_price,
        line=dict(color='#F9F9F9', width=2, dash='dash')
    )]
    annot_arr = [dict(
        x=log10((x_max*0.9)), y=market_price, xref='x', yref='y',
        text=str(market_price) + symbol,
        showarrow=True, arrowhead=7, ax=20, ay=0,
        bgcolor='#F9F9F9', font={'color': 'rgb(0,0,0)', 'size':14}
    )]
    # delete these 10 lines below if we want to move to a JS-based coloring system in the future
    shape_arr.append(dict(type='rect',
                            x0=x_min, y0=market_price,
                            x1=x_max, y1=market_price * 1.05,
                            line=dict(color='rgb(255, 0, 0)', width=0.01),
                            fillcolor='rgba(255, 0, 0, 0.06)'))
    shape_arr.append(dict(type='rect',
                            x0=x_min, y0=market_price,
                            x1=x_max, y1=market_price * 0.95,
                            line=dict(color='rgb(0, 255, 0)', width=0.01),
                            fillcolor='rgba(0, 255, 0, 0.06)'))
    for index, row in shape_bid[combined].iterrows():
        cWidth = row['unique'] * width_factor
        vol = row[TBL_VOLUME]
        posY = (row['min_Price'] + row['max_Price']) / 2.0
        if cWidth > 15:
            cWidth = 15
        elif cWidth < 2:
            cWidth = 2
        shape_arr.append(dict(type='line',
                                opacity=0.5,
                                x0=vol, y0=row['min_Price'],
                                x1=vol, y1=row['max_Price'],
                                line=dict(color='rgb(0, 255, 0)', width=cWidth)))
        list(bid_trace['x']).append(vol)
        list(bid_trace['y']).append(row['min_Price'])
        list(bid_trace['text']).append(row['text'])
        list(bid_trace['text']).append(row['text'])
        list(bid_trace['x']).append(vol)
        list(bid_trace['y']).append(posY)
        list(bid_trace['x']).append(vol)
        list(bid_trace['y']).append(row['max_Price'])
        list(bid_trace['text']).append(row['text'])
    for index, row in shape_ask[combined].iterrows():
        cWidth = row['unique'] * width_factor
        vol = row[TBL_VOLUME]
        posY = (row['min_Price'] + row['max_Price']) / 2.0
        if cWidth > 15:
            cWidth = 15
        elif cWidth < 2:
            cWidth = 2
        shape_arr.append(dict(type='line',
                                opacity=0.5,
                                x0=vol, y0=row['min_Price'],
                                x1=vol, y1=row['max_Price'],
                                line=dict(color='rgb(255, 0, 0)', width=cWidth)))
        list(ask_trace['x']).append(vol)
        list(ask_trace['y']).append(row['min_Price'])
        list(ask_trace['text']).append(row['text'])
        list(ask_trace['x']).append(vol)
        list(ask_trace['y']).append(posY)
        list(ask_trace['text']).append(row['text'])
        list(ask_trace['x']).append(vol)
        list(ask_trace['y']).append(row['max_Price'])
        list(ask_trace['text']).append(row['text'])

    result ={ 
        'data': [
            go.Scatter(
                x=data[TBL_VOLUME],
                y=data[TBL_PRICE],
                mode='markers',
                text=data['text'],
                opacity=0.95,
                hoverinfo='text',
                marker={
                    'size': data['sqrt'],
                    'line': {'width': 0.5, 'color': 'white'},
                    'color': data['color']
                    },
                ), 
            ask_trace, bid_trace, go.Scatter(
                x=ob_ask[TBL_VOLUME],
                y=ob_ask[TBL_PRICE],
                mode='lines',
                opacity=0.5,
                hoverinfo='text',
                text=ob_ask['text'],
                line = dict(color = ('rgb(255, 0, 0)'),
                        width = 2)
                ),
            go.Scatter(
                x=ob_bid[TBL_VOLUME],
                y=ob_bid[TBL_PRICE],
                mode='lines',
                opacity=0.5,
                hoverinfo='text',
                text=ob_bid['text'],
                line = dict(color = ('rgb(0, 255, 0)'),
                        width = 2)
                ),
            ],
        'layout': go.Layout(
            # title automatically updates with refreshed market price
            title=("The present market price of {} on {} is: {}{} at {}".format(ticker, exchange, symbol,
                                                                                str(marketPrice[combined]),
                                                                                timeStamps[combined])),
            xaxis=dict(title='Order Size', type='log',range=[log10(x_min*0.95), log10(x_max*1.03)], color = '#F9F9F9'),
            yaxis=dict(title = '{} Price'.format(ticker),range = [market_price*0.94, market_price*1.06], color = '#F9F9F9'),
            font=dict(color = '#F9F9F9', size=14),
            hovermode='closest',
            # now code to ensure the sizing is right
            margin={
                'l':75, 'r':75,
                'b':50, 't':50,
                'pad':4},
            paper_bgcolor='#313541',
            plot_bgcolor='#313541',
            # adding the horizontal reference line at market price
            shapes=shape_arr,
            annotations=annot_arr,
            showlegend=False
            )
        }

    # print whales in a csv file
    csv_logger = setup_db('orders')
   
    with open(DATA_DIR + 'orders/orders' + '_' + dt.datetime.today().strftime('%Y-%m-%d') + '.csv' , 'r') as f:
        readcsv = csv.reader(f, delimiter=',') 
        
        for price,size in zip([str(price) for price in final_tbl[TBL_PRICE]], [str(size) for size in final_tbl[TBL_VOLUME]]):
            if any(price and size in str(row) for row in readcsv):
                pass
            else:
                csv_logger.info("%s,%s" %(price,size))
    return result

def load_orders():
    try:
        with open(DATA_DIR + 'orders/orders' + '_' + dt.datetime.today().strftime('%Y-%m-%d') + '.csv' , 'r') as f:
            readcsv = csv.reader(f, delimiter=',')
            orders = [row for row in  readcsv]
    except:
        orders = {}
    return orders

# Cyclic overtime graph update
@app.callback(Output('whale_graph', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_Site_data(n):
    cData = calc_data()
    children = [dcc.Graph(
        id='live-graph-' + exchange + "-" + ticker,
        figure=cData)]  
    return children

# Cyclic upper data update function
@app.callback([Output('timestamp', 'children'),
               Output('whales_soitted', 'children'),
               Output('symbol', 'children'),
               Output('state', 'children'),
               Output('prevClosePrice', 'children'),
               Output('volume', 'children'),
               Output('volume24h', 'children'),
               Output('turnover', 'children'),
               Output('turnover24h', 'children'),
               Output('highPrice', 'children'),
               Output('lowPrice', 'children'),
               Output('lastPrice', 'children'),
               Output('bidPrice', 'children'),
               Output('midPrice', 'children'),
               Output('askPrice', 'children'),
               Output('openInterest', 'children'),
               Output('openValue', 'children'),
               Output('markPrice', 'children')],
              [Input('interval-component', 'n_intervals')])

def update_metrics(n):
    # Update today
    schedule.run_pending()

    statusData = ws.get_frontend_data()
    orderList = [
        ('There was a ' + order[3] + ' XBT order for ' + order[2] + ' USD at ' + order[1] + '\n') for order in load_orders()
        ]
    return [
        str('Last updated: ' + dt.datetime.today().strftime('%Y-%m-%d')),
        orderList,
        statusData['symbol'],
        statusData['state'],
        statusData['prevClosePrice'],
        statusData['volume'],
        statusData['volume24h'],
        statusData['turnover'],
        statusData['turnover24h'],
        statusData['highPrice'],
        statusData['lowPrice'], 
        statusData['lastPrice'],
        statusData['bidPrice'],
        statusData['midPrice'],
        statusData['askPrice'],
        statusData['openInterest'],
        statusData['openValue'],
        statusData['markPrice']
    ]

# Main
if __name__ == '__main__':
    app.server.run(host= '0.0.0.0', debug=True, threaded= True)

