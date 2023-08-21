import random
import yfinance as yf
from datetime import date, timedelta
from pandas_datareader import data as pdr
# override yfinance with pandas – seems to be a common step
yf.pdr_override()

# Get stock data from Yahoo Finance – here, asking for about 3 years
today = date.today()
decadeAgo = today - timedelta(days=1095)


data = pdr.get_data_yahoo('NFLX', start=decadeAgo, end=today)

# Other symbols: NFLX – Netflix, TSLA – Tesla, AMZN – Amazon, ZM – Zoom, ETH-USD – Ethereum-Dollar etc.

# Add two columns to this to allow for Buy and Sell signals
# fill with zero
data['Buy'] = 0
data['Sell'] = 0


# Find the signals – uncomment print statements if you want to
# look at the data these pick out in some another way
# e.g. check that the date given is the end of the pattern claimed

for i in range(2, len(data)):

    body = 0.01

    # Three Soldiers
    if (data.Close[i] - data.Open[i]) >= body  \
            and data.Close[i] > data.Close[i-1]  \
            and (data.Close[i-1] - data.Open[i-1]) >= body  \
            and data.Close[i-1] > data.Close[i-2]  \
            and (data.Close[i-2] - data.Open[i-2]) >= body:
        data.at[data.index[i], 'Buy'] = 1
        # print("Buy at ", data.index[i])

    # Three Crows
    if (data.Open[i] - data.Close[i]) >= body  \
            and data.Close[i] < data.Close[i-1] \
            and (data.Open[i-1] - data.Close[i-1]) >= body  \
            and data.Close[i-1] < data.Close[i-2]  \
            and (data.Open[i-2] - data.Close[i-2]) >= body:
        data.at[data.index[i], 'Sell'] = 1
        # print("Sell at ", data.index[i])


def analyse(D, H, T, P):
    try:

        shots_per_signal = D // H  # calculate number of shots per signal
        # print(f"Shots per signal: {shots_per_signal}")

        # Initialize empty lists to store results
        buy_results = []
        sell_results = []

        # Iterate through each row of the data to find signals
        for i in range(H, len(data)):
            if T == 'buy':
                if data.Buy[i] == 1:  # if we’re interested in Buy signals
                    # Calculate the mean and standard deviation of the past H days of closing prices
                    mean = data.Close[i-H:i].pct_change(1).mean()
                    std = data.Close[i-H:i].pct_change(1).std()

                    # Generate D shots of simulated closing prices using mean and std
                    simulated = [random.gauss(mean, std) for x in range(D)]

                    # Sort the simulated prices and calculate the 95th and 99th percentile values
                    simulated.sort(reverse=True)
                    var95 = simulated[int(D*0.95)]
                    var99 = simulated[int(D*0.99)]

                    # Calculate the profit/loss of this signal by comparing the price at the signal with the price P days forward
                    try:
                        future_price = data.iloc[i+P]['Close']
                        profit_loss = future_price - data.iloc[i]['Close']
                    except:
                        # If there is no future price available, skip this signal
                        continue

                    # Store the results in the buy_results list
                    buy_results.append(
                        (var95, var99, profit_loss, data.index[i].strftime('%Y-%m-%d')))
            elif T == 'sell':
                if data.Sell[i] == 1:  # if we’re interested in Sell signals
                    # Calculate the mean and standard deviation of the past H days of closing prices
                    mean = data.Close[i-H:i].pct_change(1).mean()
                    std = data.Close[i-H:i].pct_change(1).std()

                    # Generate D shots of simulated closing prices using mean and std
                    simulated = [random.gauss(mean, std) for x in range(D)]

                    # Sort the simulated prices and calculate the 5th and 1st percentile values (reverse because it's a Sell signal)
                    simulated.sort()
                    var95 = simulated[int(D*0.05)]
                    var99 = simulated[int(D*0.01)]

                    # Calculate the profit/loss of this signal by comparing the price at the signal with the price P days forward
                    try:
                        future_price = data.iloc[i+P]['Close']
                        profit_loss = data.iloc[i]['Close'] - future_price
                    except:
                        # If there is no future price available, skip this signal
                        continue

                    # Store the results in the sell_results list
                    sell_results.append(
                        (var95, var99, profit_loss, data.index[i].strftime('%Y-%m-%d')))

        return {"sell_results": sell_results, "buy_results": buy_results}
    except KeyError as ex:
        return {"error": "Key error: " + str(ex)}
    except Exception as ex:
        return {"error": str(ex)}
