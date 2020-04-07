import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
from bitmex_book import BitMEXBook
from math import log10, floor, isnan

a = BitMEXBook()


# begin building the dash itself
app = dash.Dash()
#app.scripts.append_script({"external_url": 'https://cdn.rawgit.com/pmaji/crypto-whale-watching-app/master/main.js'})

app.layout = html.Div(id='main_container', children=[
    html.Div(
        html.H2('DASH WHALE WATCHER TEST')
        ),
    dcc.Graph(
        id='DASH WHALE WATCHER TEST',
        figure={
            'data': [
                go.Scatter(
                    x=[log10(x) for x in a.get_all_sizes()],
                    y=a.get_all_prices(),
                    mode='markers',
                    text= 'All data',
                    opacity=0.95,
                    hoverinfo='text',
                    marker={
                        'size': 10,
                        'line': {'width': 0.5, 'color': 'white'},
                        'color': 'black'
                            }),            
                go.Scatter(
                    x=[log10(x) for x in a.get_ask_sizes()][::-1], 
                    y=a.get_ask_prices(),
                    mode='lines',
                    opacity=0.5,
                    hoverinfo='text',
                    text='ASKS',
                    line = dict(color = ('rgb(255, 0, 0)'),
                            width = 2)
                        ),
                go.Scatter(
                x=[log10(x) for x in a.get_bid_sizes()],
                y=a.get_bid_prices(),
                mode='lines',
                opacity=0.5,
                hoverinfo='text',
                text='BIDS',
                line = dict(color = ('rgb(0, 255, 0)'),
                        width = 2)
                    )
                ],
            'layout' :
                go.Layout(
                    # title automatically updates with refreshed market price
                    title=("The present market price of {} on {} is: {}{}".format('XBTUSD', 'BitMEX', '$', a.get_last_price())),
                    xaxis=dict(title='Order Size', type='log',range=[log10(a.get_smallest_size())*0.95, log10(a.get_largest_size())*1.03]),
                    yaxis={'title': '{} Price'.format('XBTUSD'),'range':[a.get_last_price()*0.94, a.get_last_price()*1.06]},
                    hovermode='closest',
                    # now code to ensure the sizing is right
                    margin={
                        'l':75, 'r':75,
                        'b':50, 't':50,
                        'pad':4
                        },
                    paper_bgcolor='#F5F5F5',
                    plot_bgcolor='#F5F5F5',
                    # adding the horizontal reference line at market price
                    shapes=[dict(
                        # Line Horizontal
                        type='line',
                        x0=log10(a.get_smallest_size()) * 0.5, y0=a.get_last_price(),
                        x1=log10(a.get_largest_size()) * 1.5, y1=a.get_last_price(),
                        line=dict(color='rgb(0, 0, 0)', width=2, dash='dash')
                    )],
                    annotations=[dict(
                        x=log10((a.get_largest_size()*0.9)), y=a.get_last_price(), xref='x', yref='y',
                        text=str(a.get_last_price()) + '$',
                        showarrow=True, arrowhead=7, ax=20, ay=0,
                        bgcolor='rgb(0,0,255)', font={'color': '#ffffff'}
                    )],
                    showlegend=False
                    
                    )
                }
            )
        ]
    )


if __name__ == '__main__':
    app.run_server()