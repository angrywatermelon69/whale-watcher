## Introduction

This is a Python-based Dash app developed by Quan Digital that meant to track passive orders and liquidations in the pair XBTUSD on BitMEX's orderbook. This document aims to explain the purpose and functionality of this project. You can contribute to the improvement of this project by calling out issues, requesting new features, and submitting pull requests.

The app is hosted online [here](http://ec2-34-244-232-144.eu-west-1.compute.amazonaws.com). 

If you want more info about Quan Digital, you can reach out to us [here](https://www.quan.digital). 

Read the User Guide section to learn more about how to enjoy the features made available in the app. 

## What is the purpose of this app?

In their plataform, BitMEX allow users to use the merket depht chart, however this chart jujst show less than 1% of the price from the price levels and don't allow the user to accurately view the volume of price levels.

![screenshot2](https://github.com/quan-digital/whale-watcher/blob/master/screenshot/screenshot2.png)

Thus, this app provides tools for the user access that information, by focusing on limit orders from orderbook, emphasizing the largest price levels. Enabling the user to see in an easy to understand graphic the largest price levels in a bigger range of present price, besides follow in real time updates including turnover , bid/ask prices, volume and liquidations from the orderbook.

![screenshot4](https://github.com/quan-digital/whale-watcher/blob/master/screenshot/screenshot4.jpeg)

The app use a algorithmic definition to spots a price level:
* By default, the algorithm used displays those orders that make up >= 3% of the volume of the order book shown in the +/-5% from present market price.
* Represented via a bubble in the visualization.
* Tooltip includes level price and volume.

And for Liquidations:
* Liquidations above 200,000.00 contracts.
(For now, the liquidations and announcements code are prived because they work integrated with our telegram alert bots...)

In addition to the main views which provide a quickly  information about the largest levels. There are often times when bubbles overlap themselves, when this happens, simply zoom the visualization in on a particular area to separate the two in a more detailed view. 

## User Guide and Contribution Rules

The present version tracks  only the pair XBTUSD. It is set to update every 2 seconds (to optimize load-time) but this can be changed easily in the code if you want to make the refreshes faster / slower. 
The size of each observation is determined algorithmically using a transformation of the square root of the volume of all orders at that particular price-point calibrated so that the bubbles never become unreasonably large or small and  the color-coding allows for easy identification. 

All of these limitations--i.e. the volume minimum, the order book limitations, etc., are parameterized within the dashAPP.py code and thus can be easily changed if so desired.

Anyone interested with Python 3.6 installed can download the dashAPP.py or clone the repo and run the app locally, just check to be sure you have the few required modules installed. Once you have Python 3.6 installed, open up a Terminal and type:

    pip install -r /path/to/requirements.txt

Once its finished type:

    python dashAPP.py

All are welcome to contribute issues / pull-requests to the codebase. All you have to do is include a detailed description of your contribution and that your code is thoroughly-commented.