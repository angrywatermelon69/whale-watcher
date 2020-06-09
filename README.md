## Introduction

This is a Python-based Dash app developed by Quan Digital that meant to track whale activity in the pair XBTUSD on BitMEX's orderbook. This document aims to explain the purpose and functionality of this project. You can contribute to the improvement of this project by calling out issues, requesting new features, and submitting pull requests.

The app is hosted online [here](xbtwatcher.com). 
If you want more info about Quan Digital, you can reach out to us [here](https://www.quan.digital). 

Read the User Guide section to learn more about how to enjoy the features made available in the app. 
![screenshot1](https://github.com/quan-digital/whale-watcher/blob/master/screenshot/screenshot1.png)

## What is the purpose of this app?

In their plataform, BitMEX allow users to use the merket depht chart, however this chart don't show where the volume come from and in how many orders, thus it could be from a large number of individuals who have placed orders or a few whales seeking to manipulate the market with large orders.

![screenshot2](https://github.com/quan-digital/whale-watcher/blob/master/screenshot/screenshot2.png)

This difference is important when we analise the impacts of  how quickly the whales could influence the merket depth. This app allows the user to access that information, by focusing on individual limit orders, emphasizing the largest orders. Enabling the user to spot whales that may be manipulating the present price.

The app use a algorithmic definition to spots a type of whales:
* One large order at a single price-point.
* Example: 250XBT for sale at $9000 via 1 unique order.
* Represented via a bubble in the visualization.
* Tooltip includes order price-point, volume, and number of unique orders
* By default, the algorithm used displays those orders that make up >= 1% of the volume of the order book shown in the +/-5% from present market price.

In addition to the main views which provide a quickly  information about the largest orders, users can zoom in on particular sections of the order book, or to take better advantage of the tooltip capabilities of the Plotly visualization. There are often times when bubbles overlap themselves, when this happens, simply zoom the visualization in on a particular area to separate the two in a more detailed view. An example of the tooltip functionalities for the single whales can be seen via the screenshots below.

![screenshot3](https://github.com/quan-digital/whale-watcher/blob/master/screenshot/screenshot3.png)


## User Guide and Contribution Rules

The present version tracks  only the pair XBTUSD. It is set to update every 5 seconds (to optimize load-time) but this can be changed easily in the code if you want to make the refreshes faster / slower. 
The size of each observation is determined algorithmically using a transformation of the square root of the volume of all orders at that particular price-point calibrated so that the bubbles never become unreasonably large or small and  the color-coding allows for easy identification of whales. 

All of these limitations--i.e. the volume minimum, the order book limitations, etc., are parameterized within the dashAPP.py code and thus can be easily changed if so desired.

Anyone interested with Python 3.6 installed can download the dashAPP.py or clone the repo and run the app locally, just check to be sure you have the few required modules installed. Once you have Python 3.6 installed, open up a Terminal and type:

    pip install -r /path/to/requirements.txt

Once its finished type:

    python dashAPP.py


All are welcome to contribute issues / pull-requests to the codebase. All you have to do is include a detailed description of your contribution and that your code is thoroughly-commented.