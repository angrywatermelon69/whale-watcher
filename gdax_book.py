from operator import itemgetter
from bintrees import RBTree
from decimal import Decimal
import pickle

# Coinbase Pypi 
from cbpro.public_client import PublicClient
from cbpro.websocket_client import WebsocketClient


class GDaxBook(WebsocketClient):
    def __init__(self, product_id='BTC-USD'):
        print("Initializing order Book websocket for " + product_id)
        self.product = product_id
        super(GDaxBook, self).__init__(products=[self.product])
        super(GDaxBook, self).start()


        self._asks = RBTree()
        self._bids = RBTree()

        # Initialize exchange data
        self._client = PublicClient()
        self._sequence = -1
        self._current_ticker = None


    # On data receipt
    # __on_message equivalent on ws_bitmex.py
    def on_message(self, message):

        # Coinbase data comes with sequence label
        sequence = message['sequence'] # Sequence status

        # If this is our first entry on sequence
        if self._sequence == -1:

            # Updating RB trees
            self._asks = RBTree()
            self._bids = RBTree()

            # Orderbook bulk data
            res = self._client.get_product_order_book(self.product,level=3) # Gdax oder book data


            # Structured differently from Bitmex - returns separate bids and asks
            for bid in res['bids']:
                self.add({
                    'id': bid[2], 
                    'side': 'buy', 
                    'price': Decimal(bid[0]), 
                    'size': Decimal(bid[1]) 
                })
            for ask in res['asks']:
                self.add({
                    'id': ask[2],
                    'side': 'sell',
                    'price': Decimal(ask[0]),
                    'size': Decimal(ask[1])
                })
            self._sequence = res['sequence']

        if sequence <= self._sequence:
            # ignore older messages (e.g. before order book initialization from getProductOrderBook)
            return
        elif sequence > self._sequence + 1:
            print('Error: messages missing ({} - {}). Re-initializing websocket.'.format(sequence, self._sequence))
            self.close()
            self.start()
            return

        # Order status
        msg_type = message['type'] # Type status
        if msg_type == 'open':
            self.add(message)
        elif msg_type == 'done' and 'price' in message:
            self.remove(message)
        elif msg_type == 'match':
            self.match(message)
            self._current_ticker = message
        elif msg_type == 'change':
            self.change(message)

        self._sequence = sequence

        # bid = self.get_bid()
        # bids = self.get_bids(bid)
        # bid_depth = sum([b['size'] for b in bids])
        # ask = self.get_ask()
        # asks = self.get_asks(ask)
        # ask_depth = sum([a['size'] for a in asks])
        # print('bid: %f @ %f - ask: %f @ %f' % (bid_depth, bid, ask_depth, ask))

    def on_error(self, e):
        # Reset sequence
        self._sequence = -1
        # Reset
        self.close()
        self.start()


    # -----------------------------------------------------------------------------------------------------------------------------------------------------------
    # ---------------------------------------------------Macro functions to manipulate RBTrees-------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------------------------------------------------------
			




    # Add order to out watched orders
    def add(self, order):
        order = {
            'id': order.get('order_id') or order['id'], # Order id data
            'side': order['side'], # Order side data
            'price': Decimal(order['price']), # Order price data
            'size': Decimal(order.get('size') or order['remaining_size']) # Order size data
        }
        if order['side'] == 'buy':
            bids = self.get_bids(order['price'])
            if bids is None:
                bids = [order]
            else:
                bids.append(order)
            self.set_bids(order['price'], bids)
        else:
            asks = self.get_asks(order['price'])
            if asks is None:
                asks = [order]
            else:
                asks.append(order)
            self.set_asks(order['price'], asks)

    # Order is done, remove it from watched orders
    def remove(self, order):
        price = Decimal(order['price'])
        if order['side'] == 'buy':
            bids = self.get_bids(price)
            if bids is not None:
                bids = [o for o in bids if o['id'] != order['order_id']]
                if len(bids) > 0:
                    self.set_bids(price, bids)
                else:
                    self.remove_bids(price)
        else:
            asks = self.get_asks(price)
            if asks is not None:
                asks = [o for o in asks if o['id'] != order['order_id']]
                if len(asks) > 0:
                    self.set_asks(price, asks)
                else:
                    self.remove_asks(price)

    # Associating found order on orderbook with order side, double checking
    def match(self, order):
        size = Decimal(order['size'])
        price = Decimal(order['price'])

        if order['side'] == 'buy':
            bids = self.get_bids(price)
            if not bids:
                return
            assert bids[0]['id'] == order['maker_order_id']
            if bids[0]['size'] == size:
                self.set_bids(price, bids[1:])
            else:
                bids[0]['size'] -= size
                self.set_bids(price, bids)
        else:
            asks = self.get_asks(price)
            if not asks:
                return
            assert asks[0]['id'] == order['maker_order_id']
            if asks[0]['size'] == size:
                self.set_asks(price, asks[1:])
            else:
                asks[0]['size'] -= size
                self.set_asks(price, asks)

    # Updating order price and size
    def change(self, order):
        new_size = Decimal(order['new_size'])
        price = Decimal(order['price'])

        if order['side'] == 'buy':
            bids = self.get_bids(price)
            if bids is None or not any(o['id'] == order['order_id'] for o in bids):
                return
            index = map(itemgetter('id'), bids).index(order['order_id'])
            bids[index]['size'] = new_size
            self.set_bids(price, bids)
        else:
            asks = self.get_asks(price)
            if asks is None or not any(o['id'] == order['order_id'] for o in asks):
                return
            index = map(itemgetter('id'), asks).index(order['order_id'])
            asks[index]['size'] = new_size
            self.set_asks(price, asks)

        tree = self._asks if order['side'] == 'sell' else self._bids
        node = tree.get(price)

        if node is None or not any(o['id'] == order['order_id'] for o in node):
            return


    # -----------------------------------------------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------Functions to get and format data from exchange-------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------------------------------------------------------
	

    # Actual exchange price
    def get_current_ticker(self):
        return self._current_ticker


    # Analyse how ordebook is processed
    def get_current_book(self):
        result = {
            'sequence': self._sequence,
            'asks': [],
            'bids': [],
        }
        for ask in self._asks:
            try:
                # There can be a race condition here, where a price point is removed
                # between these two ops
                this_ask = self._asks[ask]
            except KeyError:
                continue
            for order in this_ask:
                result['asks'].append([order['price'], order['size'], order['id']])
        for bid in self._bids:
            try:
                # There can be a race condition here, where a price point is removed
                # between these two ops
                this_bid = self._bids[bid]
            except KeyError:
                continue

            for order in this_bid:
                result['bids'].append([order['price'], order['size'], order['id']])
        return result




    # -----------------------------------------------------------------------------------------------------------------------------------------------------------
    # ---------------------------------------------------Micro functions to manipulate RBTrees-------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------------------------------------------------------
			

    # Get current minimum ask price from tree
    def get_ask(self):
        return self._asks.min_key()

    # Get mean ask price
    def get_asks(self, price):
        return self._asks.get(price)

    # Remove price form tree
    def remove_asks(self, price):
        self._asks.remove(price)

    # Insert price into tree
    def set_asks(self, price, asks):
        self._asks.insert(price, asks)

    def get_bid(self):
        return self._bids.max_key()

    def get_bids(self, price):
        return self._bids.get(price)

    def remove_bids(self, price):
        self._bids.remove(price)

    def set_bids(self, price, bids):
        self._bids.insert(price, bids)

# Main loop
if __name__ == '__main__':
    import time
    wsClient = WebsocketClient()
    wsClient.start()
    wsClient.products = ["ETH-USD", "ETH-BTC", "BTC-USD", "LTC-USD", "LTC-BTC", "ETH-EUR", "BTC-EUR", "LTC-EUR"]
    order_book = cbpro.OrderBook("ETH-USD")
    order_book.start()
    time.sleep(20)
    order_book.close()
