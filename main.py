import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AdamOptimizer:
    def __init__(self, learning_rate=0.01, beta1=0.9, beta2=0.999, epsilon=1e-8):
        self.learning_rate = learning_rate
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon = epsilon
        self.m = 0
        self.v = 0
        self.t = 0

    def update(self, gradient):
        self.t += 1
        self.m = self.beta1 * self.m + (1 - self.beta1) * gradient
        self.v = self.beta2 * self.v + (1 - self.beta2) * (gradient ** 2)
        m_hat = self.m / (1 - self.beta1 ** self.t)
        v_hat = self.v / (1 - self.beta2 ** self.t)
        update = self.learning_rate * m_hat / (np.sqrt(v_hat) + self.epsilon)
        return update

def calculate_gradient(prices, window=5):
    gradients = np.zeros(len(prices))
    for i in range(window, len(prices)):
        slope, _, _, _, _ = linregress(range(window), prices[i-window:i])
        gradients[i] = slope
    return gradients

def predict_next_price(prices, gradients, optimizer, volatility, last_n=10):
    recent_gradients = gradients[-last_n:]
    update = optimizer.update(np.mean(recent_gradients))
    noise = np.random.normal(0, volatility)
    return prices[-1] + update + noise

def calculate_volatility(prices, window=20):
    returns = np.log(prices[1:] / prices[:-1])
    return np.std(returns) * np.sqrt(252)  # Annualized volatility

def predict_prices(ticker, start_date, end_date, prediction_days=30):
    data = yf.download(ticker, start=start_date, end=end_date)
    close_prices = data['Close'].values
    
    gradients = calculate_gradient(close_prices)
    optimizer = AdamOptimizer()
    volatility = calculate_volatility(close_prices)
    
    predictions = []
    for _ in range(prediction_days):
        next_price = predict_next_price(close_prices, gradients, optimizer, volatility)
        predictions.append(next_price)
        close_prices = np.append(close_prices, next_price)
        gradients = calculate_gradient(close_prices)
    
    return data['Close'], predictions

def plot_results(actual_prices, predictions):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(actual_prices.index, actual_prices, label='Actual Prices')
    future_dates = pd.date_range(start=actual_prices.index[-1], periods=len(predictions)+1, freq='D')[1:]
    ax.plot(future_dates, predictions, label='Predicted Prices')
    ax.set_title('Stock Price Prediction using Adam Optimizer')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.legend()
    return fig

class StockPredictionApp:
    def __init__(self, master):
        self.master = master
        master.title("Stock Price Prediction")
        
        self.ticker_label = ttk.Label(master, text="Ticker:")
        self.ticker_label.grid(row=0, column=0, padx=5, pady=5)
        self.ticker_entry = ttk.Entry(master)
        self.ticker_entry.grid(row=0, column=1, padx=5, pady=5)
        
        self.start_date_label = ttk.Label(master, text="Start Date:")
        self.start_date_label.grid(row=1, column=0, padx=5, pady=5)
        self.start_date_entry = ttk.Entry(master)
        self.start_date_entry.grid(row=1, column=1, padx=5, pady=5)
        
        self.end_date_label = ttk.Label(master, text="End Date:")
        self.end_date_label.grid(row=2, column=0, padx=5, pady=5)
        self.end_date_entry = ttk.Entry(master)
        self.end_date_entry.grid(row=2, column=1, padx=5, pady=5)
        
        self.predict_button = ttk.Button(master, text="Predict", command=self.predict)
        self.predict_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        
        self.canvas = None
    
    def predict(self):
        ticker = self.ticker_entry.get()
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()
        
        actual_prices, predictions = predict_prices(ticker, start_date, end_date)
        fig = plot_results(actual_prices, predictions)
        
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        
        self.canvas = FigureCanvasTkAgg(fig, master=self.master)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=4, column=0, columnspan=2, padx=5, pady=5)

root = tk.Tk()
app = StockPredictionApp(root)
root.mainloop()