# commands.py

from discord.ext import commands
from bot.trading_logic import AlphaVantageTradingLogic

ALPHA_VANTAGE_API_KEY = 'ZAJZK9GPV6QOTI3N'

alpha_vantage_logic = AlphaVantageTradingLogic(ALPHA_VANTAGE_API_KEY)

class StockCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready():
        print("Bot is online")

    @commands.command(name='stock')
    async def check_stock_price(self, ctx, *symbols):
        if not symbols:
            await ctx.send("Please provide at least one stock symbol.")
            return

        prices = {}
        for symbol in symbols:
            price = alpha_vantage_logic.get_stock_price(symbol)
            prices[symbol] = price

        response = "\n".join([f"{symbol}: ${price}" if price is not None else f"Could not fetch data for {symbol}" for symbol, price in prices.items()])
        
        # Send the response to the Discord channel
        await ctx.send(response)

async def setup(bot):
    await bot.add_cog(StockCommands(bot))
