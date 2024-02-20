import discord
from discord.ext import commands
from bot.trading_logic import AlphaVantageTradingLogic
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import os

load_dotenv()

ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
POLYGON_API_KEY = os.getenv('POLYGON_IO_API_KEY')
alpha_vantage_logic = AlphaVantageTradingLogic(ALPHA_VANTAGE_API_KEY, POLYGON_API_KEY)

class StockCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.watchlist = {}
    @commands.Cog.listener()
    async def on_ready():
        print("Bot is online")

    @commands.command(name='stock')
    async def check_stock_price(self, ctx, *symbols):
        if not symbols:
            await ctx.send("Please provide at least one stock ticker.")
            return

        prices = {}
        for symbol in symbols:
            price = alpha_vantage_logic.get_stock_price(symbol)
            prices[symbol] = price

        response = "\n".join([f"{symbol}: ${price}" if price is not None else f"Could not fetch data for {symbol}" for symbol, price in prices.items()])
        
        await ctx.send(response)
    @commands.command(name='addtowatchlist')
    async def add_to_watchlist(self, ctx, *symbols):
        if not symbols:
            await ctx.send("Please provide at least one stock ticker.")
            return
        added_tickers  = []
        for symbol in symbols:
            price = alpha_vantage_logic.get_stock_price(symbol)
            if price is not None:
                self.watchlist[symbol] = price
                added_tickers.append(symbol)
            else:
                await ctx.send(f"Invalid ticker: {symbol}.")
        
        if added_tickers:
            symbols_message = "\n".join([f"Added to watchlist: {symbol}" for symbol in added_tickers])
            await ctx.send(symbols_message)
            added_tickers = []
        else:
            await ctx.send("No valid symbols were added.")
            
    @commands.command(name='watchlist')
    async def display_watchlist(self,ctx):
        if not self.watchlist:
            await ctx.send("Watchlist is empty")
        
        response = "\n".join([f"{symbol}: ${price}" if price is not None else f"Errorin the list" for symbol, price in self.watchlist.items()])
        await ctx.send(response)
        
    @commands.command(name='deletewatchlist')
    async def delete_watchlist(self, ctx):
        print("Deleting watchlist...")
        self.watchlist.clear()
        print("Watchlist deleted.")
        await ctx.send("Watchlist has been deleted")
        
    
    @commands.command(name='gethist')
    async def run_gethistorical_prices(self, ctx, symbol):
        try:
            hist_data = alpha_vantage_logic.get_historical_polygon(symbol)
            if hist_data is not None:
                # Convert the DataFrame to a string for sending in Discord
                # hist_data_str = hist_data.to_string(index=False)
                await ctx.send(f"Historical data: Success for {symbol}.")
            else:
                await ctx.send(f"Failed to get historical data for {symbol}. ")
        
        except Exception as e:
            await ctx.send(f"error: {str(e)}")
            
    @commands.command(name='plot')
    async def run_plot(self, ctx, symbol):
        try:
            alpha_vantage_logic.train_price_prediction_model(symbol)
            alpha_vantage_logic.plot_for_stock(symbol)
            plot_path = os.path.abspath(f"{symbol}_plot.png")
            
            with open(f"{symbol}_plot.png", 'rb') as plot_file:
                await ctx.send(f"Plot for {symbol}" , file = discord.File(plot_file))
        except Exception as e:
            await ctx.send(f"Error {str(e)}")

    @commands.command(name='recommend')
    async def run_predict_price(self, ctx, symbol):
        try:
            alpha_vantage_logic.train_price_prediction_model(symbol)
            
            reccomendation = alpha_vantage_logic.decision_for_stock(symbol)
            
            if reccomendation:
                print(reccomendation)
                await ctx.send(f"Recommendation for {symbol}: {reccomendation}")
            else:
                await ctx.send(f"Failed to make a recommendation for {symbol}")
        except Exception as e:
            await ctx.send(f"Error: {str(e)}")

async def setup(bot):
    await bot.add_cog(StockCommands(bot))
