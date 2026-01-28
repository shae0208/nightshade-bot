import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import sqlite3
from keep_alive import keep_alive

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

profanities = ['nigger', 'nigg3r', 'n1gg3r', 'n1gger', 'spic', 'sp1c', 'chink', 'ch1nk', 'gook',
               'g00k', 'wetback', 'beaner', 'kike', 'gringo', 'honky', 'faggot', 'f@ggot', 'f@gg0t',
               'fagg0t', 'cocksucker', 'c0cksucker', 'c0cksuck3r', 'cocksuck3r', 'dyke', 'cunt']

def create_user_table():
    connection = sqlite3.connect(f'{BASE_DIR}\\user_warnings_db')
    cursor = connection.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS 'users_per_guild' (
            'user_id' INTEGER,
            'warning_count' INTEGER,
            'guild_id' INTEGER,
            PRIMARY KEY('user_id','guild_id')
        )
    """)
    
    connection.commit()
    connection.close()

create_user_table()

def increase_and_get_warnings(user_id: int, guild_id: int):
    connection = sqlite3.connect(f'{BASE_DIR}\\user_warnings_db')
    cursor = connection.cursor()
    
    cursor.execute("""
        SELECT warning_count
        FROM users_per_guild
        WHERE (user_id = ?) AND (guild_id = ?);
    """, (user_id, guild_id))
    
    result = cursor.fetchone()
    
    if result == None:
        cursor.execute("""
            INSERT INTO users_per_guild (user_id, warning_count, guild_id)
            VALUES (?, 1, ?);
        """, (user_id, guild_id))
        
        connection.commit()
        connection.close()
        
        return 1
    
    cursor.execute("""
        UPDATE users_per_guild
        SET warning_count = ?
        WHERE (user_id = ?) AND (guild_id = ?);
    """, (result[0] + 1, user_id, guild_id))
    
    connection.commit()
    connection.close()
    
    return result[0] + 1

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

keep_alive()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix = '!', intents = intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user} is now online")

@bot.event
async def on_message(message):
    if message.author.id == bot.user.id:
        return
    else:
        for profanity in profanities:
            if profanity.lower() in message.content.lower():
                num_warnings = increase_and_get_warnings(message.author.id, message.guild.id)
                
                if num_warnings >= 3:
                    await message.author.ban(reason = "Exceeded 3 strikes for using hate speech.")
                    await message.channel.send(f"{message.author.mention} has been banned for repeated hate speech infractions.")
                else:
                    await message.channel.send(f"{message.author.mention} This is warning #{num_warnings} for use of hate speech. If you reach 3 warnings, you will be banned.")
                    await message.delete()
                    
                break
            
    await bot.process_commands(message)
                
bot.run(TOKEN)