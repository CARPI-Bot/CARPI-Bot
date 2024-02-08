import math

import discord
from discord.ext import commands

from globals import ERROR_TITLE, send_generic_error

Context = commands.Context

# Handles output for most calculator functions
async def displayAnswer(ctx: Context, answer: float, equation: str):
    # Truncates decimal in output if answer is an integer, otherwise truncate down to four digits
    display_answer = f"{int(answer):,}" if answer == int(answer) else f"{round(answer, 4):,}"
    embedVar = discord.Embed(
        title = display_answer,
        description = equation,
        color = 0x00C500
    )
    await ctx.send(embed=embedVar)

# Error handler for functions that fault if less than two arguments are provided
async def requireTwoArgumentsError(ctx: Context, error: commands.errors):
    if isinstance(error, commands.BadArgument):
        embedVar = discord.Embed(
            title = "Incorrect usage",
            description = "Enter two or more valid numbers, each separated by a space.",
            color = 0xC80000
        )
        await ctx.send(embed=embedVar)
    else:
        await send_generic_error(ctx, error)

class Calculator(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    async def cog_command_error(self, ctx: Context, error: Exception) -> None:
        if not ctx.command.has_error_handler():
            await send_generic_error(ctx, error)
    
    ### ADD ###
    @commands.hybrid_command(
        description = "Calculate the sum of any number of values.",
        aliases = ["sum", "plus", "addition"]
    )
    async def add(self, ctx: Context, nums: commands.Greedy[float]):
        # Checks for at least two arguments
        if len(nums) < 2:
            raise commands.BadArgument
        # Sums all arguments and creates an equation string
        summation, equation = 0, ""
        for i in range(len(nums)):
            summation += nums[i]
            if (nums[i].is_integer()):
                nums[i] = int(nums[i])
            equation += f"{nums[i]} + " if i < len(nums) - 1 else str(nums[i])
        await displayAnswer(ctx, summation, equation)
    
    @add.error
    async def add_error(self, ctx: Context, error):
        await requireTwoArgumentsError(ctx, error)

    ### SUBTRACT ###
    @commands.hybrid_command(
        description="Calculate the difference of any number of values, from left to right.",
        aliases=["sub", "subt", "subtraction", "minus"]
    )
    async def subtract(self, ctx: Context, nums: commands.Greedy[float]):
        if len(nums) < 2:
            raise commands.BadArgument
        # Subtracts all arguments from left to right and creates an equation string
        difference, equation = nums[0], ""
        for i in range(len(nums)):
            if i > 0:
                difference -= nums[i]
            if (nums[i].is_integer()):
                nums[i] = int(nums[i])
            equation += f"{nums[i]} - " if i < len(nums) - 1 else str(nums[i])
        await displayAnswer(ctx, difference, equation)
    
    @subtract.error
    async def subtract_error(self, ctx: Context, error):
        await requireTwoArgumentsError(ctx, error)

    ### MULTIPLY ###
    @commands.hybrid_command(
        description="Calculate the product of any number of values.",
        aliases=["mul", "mult", "times"]
    )
    async def multiply(self, ctx: Context, nums: commands.Greedy[float]):
        if len(nums) < 2:
            raise commands.BadArgument
        # Multiplies all arguments and creates an equation string
        product, equation = 1, ""
        for i in range(len(nums)):
            product *= nums[i]
            if (nums[i].is_integer()):
                nums[i] = int(nums[i])
            equation += f"{nums[i]} × " if i < len(nums) - 1 else str(nums[i])
        await displayAnswer(ctx, product, equation)

    @multiply.error
    async def multiply_error(self, ctx: Context, error):
        await requireTwoArgumentsError(ctx, error)

    ### DIVIDE ###
    @commands.hybrid_command(
        description = "Calculate the quotient of any number of values, from left to right.",
        aliases = ["div", "division"]
    )
    async def divide(self, ctx: Context, nums: commands.Greedy[float]):
        if len(nums) < 2:
            raise commands.BadArgument
        # Divides all arguments from left to right and creates an equation string
        quotient, equation = nums[0], ""
        for i in range(len(nums)):
            if i > 0:
                quotient /= nums[i]
            if (nums[i].is_integer()):
                nums[i] = int(nums[i])
            equation += f"{nums[i]} ÷ " if i < len(nums) - 1 else str(nums[i])
        await displayAnswer(ctx, quotient, equation)

    @divide.error
    async def divide_error(self, ctx: Context, error):
        await requireTwoArgumentsError(ctx, error)
    
    ### POWER ###
    @commands.hybrid_command(
        description="Calculate a power, given any base and any exponent.",
        aliases=["pow", "exp", "exponent"]
    )
    async def power(self, ctx: Context, nums: commands.Greedy[float]):
        if len(nums) < 2:
            raise commands.BadArgument
        # Calculates the powers of all arguments and creates an equation string
        power, equation = nums[0], ""
        for i in range(len(nums)):
            if i > 0:
                power **= nums[i]
            if (nums[i].is_integer()):
                nums[i] = int(nums[i])
            equation += f"{nums[i]} ^ " if i < len(nums) - 1 else str(nums[i])
        await displayAnswer(ctx, power, equation)

    @power.error
    async def power_error(self, ctx: Context, error):
        await requireTwoArgumentsError(ctx, error)
    
    ### MODULUS ###
    @commands.hybrid_command(
        description="Calculate the modulus of any number of values, from left to right.",
        aliases=["mod", "remainder"]
    )
    async def modulus(self, ctx: Context, nums: commands.Greedy[float]):
        if len(nums) < 2:
            raise commands.BadArgument
        # Calculates the modulus of all arguments and creates an equation string
        remainder, equation = nums[0], ""
        for i in range(len(nums)):
            if i > 0:
                remainder %= nums[i]
            if (nums[i].is_integer()):
                nums[i] = int(nums[i])
            equation += f"{nums[i]} % " if i < len(nums) - 1 else str(nums[i])
        await displayAnswer(ctx, remainder, equation)
    
    @modulus.error
    async def modulus_error(self, ctx: Context, error):
        await requireTwoArgumentsError(ctx, error)
    
    ### SQUARE ROOT ###
    @commands.hybrid_command(
        description="Calculate the square root of any number.",
        aliases=["root", "squareroot", "sqroot"]
    )
    async def sqrt(self, ctx: Context, num: float):
        if num.is_integer():
            num = int(num)
        equation = f"√{num}"
        root = math.sqrt(num)
        await displayAnswer(ctx, root, equation)

    @sqrt.error
    async def sqrt_error(self, ctx: Context, error):
        if isinstance(error, commands.BadArgument) or \
           isinstance(error, commands.MissingRequiredArgument):
            embedVar = discord.Embed(
                title = ERROR_TITLE,
                description = "Enter one valid number.",
                color = 0xC80000
            )
            await ctx.send(embed=embedVar)
        else:
            await send_generic_error(ctx, error)

async def setup(bot: commands.Bot):
    await bot.add_cog(Calculator(bot))