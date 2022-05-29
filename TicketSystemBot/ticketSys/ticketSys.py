from discord.ext import commands
import discord
from threading import Thread
from json import load, dump
jsonFile = "ticketSys/mainData.json"
class mainData(Thread):
    global dataJson, sendEmbedTicket, jsonChange
    def dataJson():
        mainDataList = []
        dataJson = load(open(jsonFile, "r"))["ticketSys"]
        for i in dataJson:
            mainDataList.append(dataJson[i])
        return mainDataList
    def jsonChange(index, mainIndex, replace):
        mainJsonFile = load(open(jsonFile, "r"))
        mainJsonFile["ticketSys"][index] = int(str(mainIndex).replace(str(mainIndex), str(replace)))
        with open(jsonFile, "w") as jsonDataFile:
            dump(mainJsonFile, jsonDataFile)
    async def sendEmbedTicket(ctx, channel, botName):
        mainEmbed = discord.Embed(title="To Create A New Ticket, Choose Emoji")
        for i in range(len(dataJson()[2])):
            reactionEmoji = discord.utils.get(ctx.guild.emojis, id=dataJson()[4][i])
            mainEmbed.add_field(name=f"{str(reactionEmoji)} {dataJson()[2][i]}", value=str(dataJson()[3][i]), inline=False)
        mainTicketMessage = await channel.send(embed=mainEmbed)
        jsonChange(index="mainTicketMessage", mainIndex=dataJson()[1], replace=mainTicketMessage.id)
        for e in range(len(dataJson()[4])):
            reactionEmoji = discord.utils.get(ctx.guild.emojis, id=dataJson()[4][e])
            await mainTicketMessage.add_reaction(str(reactionEmoji))
                   
class ticketSys(commands.Cog, name="ticketSys"):
    def __init__(self, bot):
        self.bot = bot
    @commands.slash_command(name="initchannel", description="To Initialize The Ticket System To Any Channel")
    async def initchannel(self, ctx, channel: discord.Option(discord.TextChannel, description="Channel To Be Used (If None This Channel Will Be Selected)", required=False, default=None)):
        await ctx.defer()
        if ctx.author.guild_permissions.administrator == True:
            if channel == None:
                channel = ctx.channel
            if int(dataJson()[0]) != int(channel.id):
                jsonChange(index="mainChannel", mainIndex=dataJson()[0], replace=int(channel.id))
                await sendEmbedTicket(ctx, channel, self.bot.user.name)
                await ctx.send_followup(f"{self.bot.user.name} Has Been Intiated To The Channel <#{channel.id}>")
            else:
                await ctx.send_followup(f"{self.bot.user.name} Is Already Running On <#{channel.id}>")
        else:
            await ctx.send_followup(f"You Don't Have Permissions To Initialize The Bot!", delete_after=5.0)
    @commands.slash_command(name="delete_ticket", description="To Delete A Solved Ticket")
    async def delete_ticket(self, ctx):
        if ctx.author.guild_permissions.administrator == True:
            if ctx.channel.category_id == int(dataJson()[6]):
                await ctx.channel.delete()
    @commands.slash_command(name="solved", description="To Mark Ticket As Solved")
    async def solved(self, ctx):
        await ctx.defer()
        for member in ctx.guild.members:
            userJson = load(open("userData.json", "r"))
            userTicket = userJson["userData"]["ticketUser"]
            mainUserTicket = dict(userTicket)
            if ctx.channel.permissions_for(member).view_channel == True:
                try:
                    mainUserTicket.pop(str(ctx.channel.id))
                    userJson["userData"]["ticketUser"] = mainUserTicket
                    with open("userData.json", "w") as mainDataFile:
                        dump(userJson, mainDataFile)
                except: pass
                await ctx.channel.set_permissions(member, view_channel=False)
        await ctx.send_followup(f"Ticket Closed!")
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        allUsers = []
        userJson = load(open("userData.json", "r"))
        userTicket = userJson["userData"]["ticketUser"]
        mainGuild = self.bot.get_guild(payload.guild_id)
        mainChannel = mainGuild.get_channel(payload.channel_id)
        mainMessage = await mainChannel.fetch_message(payload.message_id)
        await mainMessage.remove_reaction(payload.emoji, payload.member)
        if payload.member != self.bot.user:
            for user in userTicket.values():
                allUsers.append(user)
            if payload.user_id not in allUsers:
                if payload.message_id == int(dataJson()[1]):
                    if len(dataJson()[4]) == len(dataJson()[5]):
                        for reaction in range(len(dataJson()[4])):
                            if dataJson()[4][reaction] == int(payload.emoji.id):
                                mainCategory = discord.utils.get(mainGuild.categories, id=int(dataJson()[6]))
                                mainChannel = await mainGuild.create_text_channel(name=f"Ticket-00{str(dataJson()[7])}", category=mainCategory)
                                mainUserTicket = dict(userTicket)
                                mainUserTicket[str(mainChannel.id)] = payload.user_id
                                userJson["userData"]["ticketUser"] = mainUserTicket
                                with open("userData.json", "w") as mainDataFile:
                                    dump(userJson, mainDataFile)
                                await mainChannel.set_permissions(payload.member, view_channel=True)
                                await mainChannel.send(f"<@{payload.member.id}>, Your Ticket Has Been Created Here\nTopic: {dataJson()[5][reaction]}")
                                jsonChange(index="ticketNumber", mainIndex=dataJson()[7], replace=int(dataJson()[7]+1))
                else:
                    print("Something Went Worng\n Please Check The Data Json File.")        
            else: 
                await payload.member.send(f"You Have A Ticket Opened Already In {mainGuild.name} Server.", delete_after=60.0)            
def setup(bot):
    bot.add_cog(ticketSys(bot))
    print("TICKET BOT IN RUNNING!")