from discord.ext import commands
from globals import *
from decimal import Decimal

class Calculator(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(description='Returns the sum of any number of float values.')
    async def add(self, ctx, *nums:Decimal):
        #Require at least two arguments
        if len(nums) < 2: 
            raise commands.BadArgument()
        summation = sum(nums) #Adds all elements of the tuple together
        #If the sum is equal to it's integer value (no decimals)
        if summation == summation.to_integral_value(): 
            await ctx.send('{:,}'.format(int(summation))) #Sends the answer without decimals
        else:
            await ctx.send('{:,}'.format(summation)) #Sends the answer normally
    
    @add.error
    async def add_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('Enter at least two valid numbers.')

    @commands.command(description='Returns the difference of any number of float values, calculated from left to right.')
    async def subtract(self, ctx, *nums:Decimal):
        if len(nums) < 2:
            raise commands.BadArgument()
        difference = nums[0]
        for x in range(1, len(nums)):
            difference -= nums[x] #Subtracts all elements of the tuple from left to right
        #If the difference is equal to it's integer value (no decimals)
        if difference == difference.to_integral_value: 
            await ctx.send('{:,}'.format(int(difference))) #Sends the answer without decimals
        else:
            await ctx.send('{:,}'.format(difference)) #Sends the answer normally
    
    @subtract.error
    async def subtract_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('Enter at least two valid numbers.')

    @commands.command(description='Returns the product of any number of float values.')
    async def multiply(self, ctx, *nums:Decimal):
        if len(nums) < 2:
            raise commands.BadArgument()
        product = 1
        for x in nums:
            product *= x #Multiplies all elements of the tuple together
        #If the product is equal to it's integer value (no decimals)
        if product == product.to_integral_value: 
            await ctx.send('{:,}'.format(int(product))) #Sends the answer without decimals
        else:
            await ctx.send('{:,}'.format(product)) #Sends the answer normally

    @multiply.error
    async def multiply_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('Enter at least two valid numbers.')

    @commands.command(description='Returns the quotient of any number of float values, calculated from left to right.')
    async def divide(self, ctx, *nums:Decimal):
        if len(nums) < 2:
            raise commands.BadArgument()
        quotient = nums[0]
        for x in range(1, len(nums)):
            quotient /= nums[x] #Divides all elements of the tuple from left to right
        #If the quotient is equal to it's integer value (no decimals)
        if quotient == quotient.to_integral_value: 
            await ctx.send('{:,}'.format(int(quotient))) #Sends the answer without decimals
        else:
            await ctx.send('{:,}'.format(quotient)) #Sends the answer normally

    @divide.error
    async def divide_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('Enter at least two valid numbers.')