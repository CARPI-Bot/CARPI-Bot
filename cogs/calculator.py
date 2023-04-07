import discord
from discord.ext import commands
from globals import *
from decimal import Decimal
import math

# Handles output for most calculator functions
async def displayAnswer(ctx:commands.Context, answer:Decimal, equation:str, color:int=0x00C500):
    # Displays the answer without decimals if it's equal to it's integer value
    if answer == answer.to_integral_value(): 
        display_answer = "{:,}".format(int(answer))
    # Otherwise displays the answer with decimals
    else:
        display_answer = "{:,}".format(answer)
    # Creates and sends a response embed
    embedVar = discord.Embed(title=display_answer,
                                description=equation,
                                color=color)
    await ctx.send(embed=embedVar)

# Error handler for functions that only fault if less than two arguments are provided
async def requireTwoArgumentsError(ctx:commands.Context, error:commands.errors, color:int=0xC80000):
    # If less than two arguments are passed in
    if isinstance(error, commands.BadArgument):
        embedVar = discord.Embed(title=ERROR_TITLE,
                                 description="Enter at least two numbers, each separated by a space.",
                                 color=color)
        await ctx.send(embed=embedVar)
    # Sends the default error defined in globals.py
    else:
        await sendDefaultError(ctx)

class Calculator(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    ### ADD ###
    @commands.hybrid_command(description="Calculate the sum of any number of values.",
                             aliases=["sum", "plus"])
    async def add(self, ctx, nums:commands.Greedy[Decimal]):
        # Checks for at least two arguments
        if len(nums) < 2: 
            raise commands.BadArgument
        # Sums all arguments and creates an equation string
        summation, equation = 0, ""
        for i in range(len(nums)):
            summation += nums[i]
            if (i < len(nums) - 1):
                equation += f"{nums[i]} + "
            else:
                equation += str(nums[i])
        # Outputs the answer
        await displayAnswer(ctx, summation, equation)
    
    @add.error
    async def add_error(self, ctx, error):
        await requireTwoArgumentsError(ctx, error)

    ### SUBTRACT ###
    @commands.hybrid_command(description="Calculate the difference of any number of values, from left to right.",
                             aliases=["sub", "subt", "minus"])
    async def subtract(self, ctx, nums:commands.Greedy[Decimal]):
        # Checks for at least two arguments
        if len(nums) < 2:
            raise commands.BadArgument
        # Subtracts all arguments from left to right and creates an equation string
        difference, equation = nums[0], f"{nums[0]} - "
        for i in range(1, len(nums)):
            difference -= nums[i]
            if (i < len(nums) - 1):
                equation += f"{nums[i]} - "
            else:
                equation += str(nums[i])
        # Outputs the answer
        await displayAnswer(ctx, difference, equation)
    
    @subtract.error
    async def subtract_error(self, ctx, error):
        await requireTwoArgumentsError(ctx, error)

    ### MULTIPLY ###
    @commands.hybrid_command(description="Calculate the product of any number of values.",
                             aliases=["mul", "mult", "times"])
    async def multiply(self, ctx, nums:commands.Greedy[Decimal]):
        # Checks for at least two arguments
        if len(nums) < 2:
            raise commands.BadArgument
        # Multiplies all arguments and creates an equation string
        product, equation = 1, ""
        for i in range(len(nums)):
            product *= nums[i]
            if (i < len(nums) - 1):
                equation += f"{nums[i]} × "
            else:
                equation += str(nums[i])
        # Outputs the answer
        await displayAnswer(ctx, product, equation)

    @multiply.error
    async def multiply_error(self, ctx, error):
        await requireTwoArgumentsError(ctx, error)

    ### DIVIDE ###
    @commands.hybrid_command(description="Calculate the quotient of any number of values, from left to right.",
                             aliases=["div"])
    async def divide(self, ctx, nums:commands.Greedy[Decimal]):
        # Checks for at least two arguments
        if len(nums) < 2:
            raise commands.BadArgument
        # Divides all arguments from left to right and creates an equation string
        quotient, equation = nums[0], f"{nums[0]} ÷ "
        for i in range(1, len(nums)):
            quotient /= nums[i]
            if (i < len(nums) - 1):
                equation += f"{nums[i]} ÷ "
            else:
                equation += str(nums[i])
        # Outputs the answer
        await displayAnswer(ctx, quotient, equation)

    @divide.error
    async def divide_error(self, ctx, error):
        await requireTwoArgumentsError(ctx, error)
    
    ### POWER ###
    @commands.hybrid_command(description="Returns the exponential result of any number to the power of any number.",
                             aliases=["exp", "exponent"])
    async def power(self, ctx, nums:commands.Greedy[Decimal]):
        # Checks for at least two arguments
        if len(nums) < 2:
            raise commands.BadArgument
        # Calculates the powers of all arguments and creates an equation string
        power, equation = nums[0], f"{nums[0]} ^ "
        for i in range(1, len(nums)):
            power **= nums[i]
            if (i < len(nums) - 1):
                equation += f"{nums[i]} ^ "
            else:
                equation += str(nums[i])
        # Outputs the answer
        await displayAnswer(ctx, power, equation)

    @power.error
    async def power_error(self, ctx, error):
        await requireTwoArgumentsError(ctx, error)
    
    ### MODULUS ###
    @commands.hybrid_command(description="Calculate the remainder of any number of values, from left to right.",
                             aliases=["mod", "remainder"])
    async def modulus(self, ctx, nums:commands.Greedy[Decimal]):
        # Checks for at least two inputs
        if len(nums) < 2:
            raise commands.BadArgument
        # Calculates the modulus of all arguments and creates an equation string
        remainder, equation = nums[0], f"{nums[0]} % "
        for i in range(1, len(nums)):
            remainder %= nums[i]
            if (i < len(nums) - 1):
                equation += f"{nums[i]} % "
            else:
                equation += str(nums[i])
        # Outputs the answer
        await displayAnswer(ctx, remainder, equation)
    
    @modulus.error
    async def modulus_error(self, ctx, error):
        await requireTwoArgumentsError(ctx, error)
    
    ### SQUARE ROOT ###
    @commands.hybrid_command(description="Calculate the square root of any number or group of numbers.",
                             aliases=["rad", "radical", "root", "squareroot", "square_root"])
    async def sqrt(self, ctx, nums:commands.Greedy[Decimal]):
        # Checks for at least one argument
        if len(nums) == 0:
            raise commands.BadArgument
        # Calculates the root of each argument and creates output strings
        roots, display_roots, inputs = [], "", "Input(s): "
        for i in range(len(nums)):
            roots.append(Decimal(math.sqrt(nums[i])))
            if (i < len(nums) - 1):
                inputs += f"{nums[i]}, "
            else:
                inputs += str(nums[i])
        # Creates the answer string and determines how each number should be formatted
        format_template = "{:,}, "
        for i in range(len(roots)):
            if (i == len(nums) - 1):
                format_template = "{:,}"
            if roots[i] == roots[i].to_integral_value():
                display_roots += format_template.format(int(roots[i]))
            else:
                display_roots += format_template.format(roots[i])
        # Creates and sends a response embed
        embedVar = discord.Embed(title=display_roots,
                                    description=inputs,
                                    color=0x00C500)
        await ctx.send(embed=embedVar)

    @sqrt.error
    async def sqrt_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            embedVar = discord.Embed(title=ERROR_TITLE,
                                    description="Enter at least one number, each separated by a space.",
                                    color=0xC80000)
            await ctx.send(embed=embedVar)
        else:
            await sendDefaultError(ctx)
    
    ### INVERSE ###
    @commands.hybrid_command(description= "Calculates the inverse of any number or a group of numbers.",
                             aliases=["1/"])
    async def inverse(self, ctx, nums:commands.Greedy[Decimal]):
        # Checks for at least one argument
        if len(nums) == 0:
            raise commands.BadArgument 
        # Calculates the inverse of each argument and creates output strings
        inverses, display_inverses, inputs = [], "", "Input(s): "
        for i in range(len(nums)):
            inverses.append(Decimal(1 / nums[i]))
            if (i < len(nums) - 1):
                inputs += f"{nums[i]}, "
            else:
                inputs += str(nums[i])
        # Creates the answer string and determines how each number should be formatted
        format_template = "{:,}, "
        for i in range(len(inverses)):
            if (i == len(nums) - 1):
                format_template = "{:,}"
            if inverses[i] == inverses[i].to_integral_value():
                display_inverses += format_template.format(int(inverses[i]))
            else:
                display_inverses += format_template.format(inverses[i])
        # Creates and sends a response embed
        embedVar = discord.Embed(title=display_inverses,
                                    description=inputs,
                                    color=0x00C500)
        await ctx.send(embed=embedVar)
    
    @inverse.error
    async def inverse_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            embedVar = discord.Embed(title=ERROR_TITLE,
                                    description="Enter at least one number, each separated by a space.",
                                    color=0xC80000)
            await ctx.send(embed=embedVar)
        else:
            await sendDefaultError(ctx)

async def setup(bot):
    await bot.add_cog(Calculator(bot))