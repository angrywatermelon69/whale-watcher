## Introduction

This is a Python-based Dash app developed by Quan Digital that meant to track whale activity in the pair XBTUSD on BitMEX's orderbook. This document aims to explain the purpose and functionality of this project. You can contribute to the improvement of this project by calling out issues, requesting new features, and submitting pull requests.

The app is hosted online [here](http://www.xbtwatcher.com). 
If you want more info about Quan Digital, you can reach out to us [here](https://www.quan.digital). 

## User Guide

The present version tracks  only the pair XBTUSD. It is set to update every 5 seconds (to optimize load-time) but this can be changed easily in the code if you want to make the refreshes faster / slower. 
The size of each observation is determined algorithmically using a transformation of the square root of the volume of all orders at that particular price-point calibrated so that the bubbles never become unreasonably large or small and  the color-coding allows for easy identification of whales. 

The app use a algorithmic definition to spots a type of Price Levels:
* One large order at a single price-point.
* Example: 250XBT for sale at $9000 via 1 unique order.
* Represented via a bubble in the visualization.
* Tooltip includes order price-point, volume, and number of unique orders
* By default, the algorithm used displays those orders that make up >= 1% of the volume of the order book shown in the +/-5% from present market price.

All of these limitations--i.e. the volume minimum, the order book limitations, etc., are parameterized within the app.py code and thus can be easily changed if so desired.

In addition to the main views which provide a quickly  information about the largest orders, users can zoom in on particular sections of the order book, or to take better advantage of the tooltip capabilities of the Plotly visualization. There are often times when bubbles overlap themselves, when this happens, simply zoom the visualization in on a particular area to separate the two in a more detailed view. An example of the tooltip functionalities for the single whales can be seen via the screenshots below.

Anyone interested with Python 3.6 installed can download the app.py or clone the repo and run the app locally, just check to be sure you have the few required modules installed. Once you have Python 3.6 installed, open up a Terminal and type:

    pip3 install -r /path/to/requirements.txt

Once its finished type:

    python3 app.py

All are welcome to contribute issues / pull-requests to the codebase. All you have to do is include a detailed description of your contribution and that your code is thoroughly-commented.
