from discord.ext import commands
from globals import *
from decimal import Decimal

class Calculator(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(description="Returns the sum of any number of values.")
    async def add(self, ctx, *nums:Decimal):
        # Checks for at least two arguments
        if len(nums) < 2: 
            raise commands.BadArgument()
        # Adds all elements of the tuple
        summation = sum(nums)
        # Displays the sum without decimals if it's equal to it's integer value
        if summation == summation.to_integral_value(): 
            await ctx.send("{:,}".format(int(summation)))
        # Otherwise displays the sum with decimals
        else:
            await ctx.send("{:,}".format(summation))
    
    @add.error
    async def add_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Enter at least two numbers.")

    @commands.command(description="Returns the difference of any number of values, calculated from left to right.")
    async def subtract(self, ctx, *nums:Decimal):
        # Checks for at least two arguments
        if len(nums) < 2:
            raise commands.BadArgument()
        # Subtracts all elements of the tuple from left to right
        difference = nums[0]
        for x in range(1, len(nums)):
            difference -= nums[x]
        # Displays the difference without decimals if it's equal to it's integer value
        if difference == difference.to_integral_value: 
            await ctx.send("{:,}".format(int(difference)))
        # Otherwise displays the difference with decimals
        else:
            await ctx.send("{:,}".format(difference))
    
    @subtract.error
    async def subtract_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Enter at least two numbers.")

    @commands.command(description="Returns the product of any number of values.")
    async def multiply(self, ctx, *nums:Decimal):
        # Checks for at least two arguments
        if len(nums) < 2:
            raise commands.BadArgument()
        # Multiplies all elements of the tuple
        product = 1
        for x in nums:
            product *= x
        # Displays the product without decimals if it's equal to it's integer value
        if product == product.to_integral_value: 
            await ctx.send("{:,}".format(int(product)))
        # Otherwise displays the product with decimals
        else:
            await ctx.send("{:,}".format(product)) #Sends the answer normally

    @multiply.error
    async def multiply_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Enter at least two numbers.")

    @commands.command(description="Returns the quotient of any number of values, calculated from left to right.")
    async def divide(self, ctx, *nums:Decimal):
        # Checks for at least two arguments
        if len(nums) < 2:
            raise commands.BadArgument()
        # Divides all elements of the tuple from left to right
        quotient = nums[0]
        for x in range(1, len(nums)):
            quotient /= nums[x]
        # Displays the quotient without decimals if it's equal to it's integer value
        if quotient == quotient.to_integral_value: 
            await ctx.send("{:,}".format(int(quotient)))
        # Otherwise displays the quotient with decimals
        else:
            await ctx.send("{:,}".format(quotient))

    @divide.error
    async def divide_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Enter at least two numbers.")