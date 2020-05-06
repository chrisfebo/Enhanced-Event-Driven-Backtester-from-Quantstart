from execution import SimulatedExecutionHandler
from data import HistoricCSVDataHandler
from strategy import BuyAndHoldStrategy
from portfolio import NaivePortfolio

import datetime

try:
    import Queue as queue
except ImportError:
    import queue

# declare events queue
events = queue.Queue()

# declare start date
start_date = datetime.datetime(2015, 5, 6, 0, 0, 0)

# Declare the components with respective parameters
bars = HistoricCSVDataHandler(events, '/home/chris/github-repos/Enhanced-Event-Driven-Backtester-from-Quantstart/DataHub/', ['AAPL'] )
strategy = BuyAndHoldStrategy(bars, events)
port = NaivePortfolio(bars, events, start_date, 1000000.0)
broker = SimulatedExecutionHandler(events)

while True:
    # Update the bars (specific backtest code, as opposed to live trading)
    if bars.continue_backtest == True:
        bars.update_bars()
    else:
        break

    # Handle the events
    while True:
        try:
            event = events.get(False)
        except Queue.Empty:
            break
        else:
            if event is not None:
                if event.type == 'MARKET':
                    strategy.calculate_signals(event)
                    port.update_timeindex(event)

                elif event.type == 'SIGNAL':
                    port.update_signal(event)

                elif event.type == 'ORDER':
                    broker.execute_order(event)

                elif event.type == 'FILL':
                    port.update_fill(event)

    # 10-Minute heartbeat
    time.sleep(10 * 60)