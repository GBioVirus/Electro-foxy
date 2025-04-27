#!/usr/bin/python
# encoding: utf-8\
import discord
from discord.activity import Game
from discord.ext import commands, tasks
import threading
from discord.ext.commands import TextChannelConverter
import asyncio
import random
import time
import json
import requests
import datetime
from discord import Option
from discord.ext.commands import slash_command
import sqlite3
#from background import keep_alive
from datetime import datetime

TOKEN = "token"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='k!', intents=intents)
games = []

db_conn = sqlite3.connect('bot.db')
db_cursor = db_conn.cursor()

# Создание таблицы для хранения данных на уровне сервера
db_cursor.execute('''CREATE TABLE IF NOT EXISTS server_data
                     (server_id TEXT PRIMARY KEY, response_channel_id TEXT, game_channel_id TEXT, host_role_id TEXT, player_role_id TEXT)''')
db_conn.commit()

@bot.slash_command(name='setup')
@commands.has_permissions(administrator=True)
async def setup(ctx):
	await ctx.send("Привет! Давай настроим каналы и роли для приема ответов и игр.")

	def check(message):
		return message.author == ctx.author and message.channel == ctx.channel

# Запрос канала для приема ответов
	await ctx.send("Укажи канал для приема ответов:")
	response1 = await bot.wait_for('message', check=check)
	response_channel_id = response1.channel_mentions[0].id
# Запрос канала для игр
	await ctx.send("Укажи канал для игр:")
	response2 = await bot.wait_for('message', check=check)
	game_channel_id = response2.channel_mentions[0].id

# Запрос роли ведущего
	await ctx.send("Укажи роль для ведущего:")
	response3 = await bot.wait_for('message', check=check)
	host_role_id = response3.role_mentions[0].id

# Запрос роли игроков
	await ctx.send("Укажи роль для игроков:")
	response4 = await bot.wait_for('message', check=check)
	player_role_id = response4.role_mentions[0].id

# Занесение данных в базу данных
	db_cursor.execute('''INSERT OR REPLACE INTO server_data (server_id, response_channel_id, game_channel_id, host_role_id, player_role_id)
	VALUES (?, ?, ?, ?, ?)''', (str(ctx.guild.id), str(response_channel_id), str(game_channel_id), str(host_role_id), str(player_role_id)))
	db_conn.commit()

	await ctx.send("Настройка завершена!")

# Получение данных из базы данных исходя из конкретного сервера
@bot.event
async def on_ready():
	db_cursor.execute("SELECT * FROM server_data")
	server_data = db_cursor.fetchall()
	for row in server_data:
		server_id, response_channel_id, game_channel_id, host_role_id, player_role_id = row
		
		print('Heya i`m {0.user}, give me your paw'.format(bot))
		print("version: 3.3 beta")
		print("created by Mr. Foxy")
		phrases = [
			"Давай повеселимся!",
			"Готов играть?",
			"Угадай слово!",
			"Давай поиграем в Виселицу!",
			"Лисенок лучший",
			"Давай поиграем с Далией",
			"Хахаха",
			"Скраббл или поиск в тени",
			"Создаю кроссворд"
			]
		while True:
			activity = discord.Game(name=random.choice(phrases), type=2)
			await bot.change_presence(status=discord.Status.idle, activity=activity)
			await asyncio.sleep(300)
               
#Ping bot
@bot.slash_command(name='check', description="проверить работу бота")
async def ping(ctx):
	await ctx.respond(f'Эй, я очень занят!\n Мой пинг `{round(bot.latency * 1000)}ms`', ephemeral=True)

@bot.slash_command(name="test")
@commands.has_permissions(manage_messages=True)
async def says(ctx):
	server_id = str(ctx.guild.id)
	db_cursor.execute("SELECT * FROM server_data WHERE server_id=?", (server_id,))
	server_data = db_cursor.fetchone()

	if server_data:
		response_channel_id = server_data[1]
		game_channel_id = server_data[2]
		host_role_id = server_data[3]
		player_role_id = server_data[4]
            
		response = f"Server ID: {server_id}\nResponse Channel ID: {response_channel_id}\nGame Channel ID: {game_channel_id}\nHost Role ID: {host_role_id}\nPlayer Role ID: {player_role_id}"
	else:
		response = "No data found for this server."

	await ctx.respond(response)
#/say command
@bot.slash_command(name="say", description="Make the bot say any phrase")
@commands.has_permissions(manage_messages=True)
async def say(ctx, text: Option(str, description="The phrase to be said"), embed: Option(bool, description="Whether to send the message as an embed") = False, channel: Option(discord.TextChannel, description="The channel to send the message in") = None):
		if channel is None:
		channel = ctx.channel
		async with ctx.channel.typing():
			await asyncio.sleep(2)
			await ctx.respond(f"I said:\n{text}\nIn channel: {channel.mention}", ephemeral=True)
			if embed:
				embed = discord.Embed(description=text, color=0xff0000)
				await channel.send(embed=embed)
			else:
				await channel.send(text)

#bunker codes
#bunker codes
def save_codes():
		with open('codes.json', 'w') as file:
				json.dump(bunker_codes, file)

@bot.command(name = "set_ba")
@commands.has_any_role(1166824236405502035)
async def set_codes(ctx, *codes):
		global bunker_codes
		bunker_codes = {i+1: code for i, code in enumerate(codes)}
		save_codes()
		await ctx.send("Codes is added.")

bunker_codes = {}
last_loaded_date = None

def load_codes():
		global bunker_codes, last_loaded_date
		current_date = datetime.now().date()
		if last_loaded_date != current_date:
				with open('codes.json', 'r') as file:
						bunker_codes = json.load(file)
				last_loaded_date = current_date

def get_bunker_code():
		load_codes()
		current_date = datetime.now().date()
		code = bunker_codes.get(str(current_date.day))
		if not code:
				code = random.choice(list(bunker_codes.values()))
		return code

footer_phrases = [
		"Почухай пузика лисенку",
		"Подари цвяточек",
		"Танцуй крошка",
		"А ты так можешь???",
		"Сдаюсь!"
]

@bot.listen()
async def on_message(message):
		if "альфа код" in message.content.lower() or "бункер код" in message.content.lower():
				code = get_bunker_code()
				footer_text = random.choice(footer_phrases)
				embed = discord.Embed(
						title="Bunker Code",
						description=f"The bunker code for today is: \n# {code}\n", color=0x00ff00)
				embed.set_footer(text=f"If you like it click ♥️\n{footer_text}", icon_url="https://media.discordapp.net/attachments/718777002181787649/1148303687454830713/unnamed.jpg")
				sent_message = await message.channel.send(content=message.author.mention, embed=embed)
				await sent_message.add_reaction('❤️')
		await bot.process_commands(message)

#EA ANSWERS COMMAND
@bot.slash_command(name='ea', description="answer for event on ea channel")
@commands.cooldown(1, 30, commands.BucketType.user)
async def ea(ctx, answer: Option(str, description='your answer for events')):
 	# Retrieve server data from the database based on the server ID
	server_id = str(ctx.guild.id)
	db_cursor.execute("SELECT * FROM server_data WHERE server_id=?", (server_id,))
	server_data = db_cursor.fetchone()

	if server_data:
		response_channel_id = server_data[1]
		game_channel_id = server_data[2]
        
		if ctx.channel.id != int(game_channel_id):
			await ctx.respond(f"Heya {ctx.author.mention}, for /ea command you need to choose <#{game_channel_id}> channel", ephemeral=True)
			return
    
	await ctx.respond(f'Thanks, {ctx.author.name}!❤️\nYour event answer submission is being reviewed by event moderators right now!\n Answer added\nYour answer:\n{answer}', ephemeral=True)
    
	await ctx.send(f"Answer added {ctx.author.mention} 📣")
	achan = int(response_channel_id)
	channea = bot.get_channel(achan)
	words = answer.split(' ')
	avatar = ctx.author.avatar
	embed = discord.Embed(title='**__Event answer__**', color=0xff0000)
	embed.add_field(name=f"**Word Count:** **{len(words)}**", value=f"**User:** {ctx.author.mention}\n**Answer:** {answer}\n\n Maybe this is true", inline=False)
	await channea.send(embed=embed)

@ea.error
async def ea_error(ctx, error):
	if isinstance(error, commands.CommandOnCooldown):
		em = discord.Embed(title="Slow it down bro!", description=f"Try again in {error.retry_after:.2f}s.", color=0xff0000)
		await ctx.respond(embed=em, ephemeral=True)

@bot.slash_command(name="players", description="Get players in role on events channels")
@commands.has_permissions(manage_messages=True)
async def players(ctx):
# Retrieve server data from the database based on the server ID
	server_id = str(ctx.guild.id)
	db_cursor.execute("SELECT * FROM server_data WHERE server_id=?", (server_id,))
	server_data = db_cursor.fetchone()

	if server_data:
		response_channel_id = server_data[1]
		game_channel_id = server_data[2]
		host_role_id = server_data[3]
		player_role_id = server_data[4]

		role = ctx.guild.get_role(player_role_id)

		if ctx.channel.id == game_channel_id:
			data = "\n".join([f"`{member.id}` {member.name or member.nick}" for member in role.members])
			embed = discord.Embed(title=f"All users in {role}", description=f"Users in role: `{len(role.members)}`\n{data}\n")
			await ctx.respond(embed=embed)
			else:
				await ctx.respond("Change channel EA or SUB", ephemeral=True)
	else:
		await ctx.respond("No server data found.", ephemeral=True)

#add code events
@bot.slash_command(name='add_code', description="Create code")
@commands.has_permissions(manage_messages=True)
async def add(ctx, addcode: Option(str, description="Write code")):
# Retrieve server data from the database based on the server ID
	server_id = str(ctx.guild.id)
	db_cursor.execute("SELECT * FROM server_data WHERE server_id=?", (server_id,))
	server_data = db_cursor.fetchone()
	if server_data:
		code_data = server_data[5]

# Update the code data in the database
		db_cursor.execute("UPDATE server_data SET code_data=? WHERE server_id=?", (addcode, server_id))
		db_connection.commit()
		embed = discord.Embed(title="Code Created", description=f"New code: {addcode}.")
		await ctx.respond(embed=embed, ephemeral=True)
	else:
		await ctx.respond("No server data found.", ephemeral=True)

#ba code 
@bot.slash_command(name="ba", descripton="Try to open eanker ea")
@commands.cooldown(1, 30, commands.BucketType.user)
async def ba(ctx, code: Option(str, description="Write code")):
# Retrieve server data from the database based on the server ID
	server_id = str(ctx.guild.id)
	db_cursor.execute("SELECT * FROM server_data WHERE server_id=?", (server_id,))
	server_data = db_cursor.fetchone()
	if server_data:
		response_channel_id = server_data[1]
		game_channel_id = server_data[2]
		code_data = server_data[5]
		alpha_code = code_data
		if ctx.channel.id != int(game_channel_id):
			await ctx.respond(f"Heya {ctx.author.mention} for /ba command you need to choose <#{game_channel_id}> channel", ephemeral=True)
			return
			if code == alpha_code:
				await ctx.respond(f"Thanks, {ctx.author.mention}! ❤️\nYour code {code} check in terminal\ncode activate or not", ephemeral=True)
				await ctx.send(f"{ctx.author.mention} Your code is added")
				achan = int(response_channel_id)
				channel = bot.get_channel(achan)
				if channel:
					embed = discord.Embed(title="Entered code", description=f"**User:** {ctx.author.mention}\n**User ID:** {ctx.author.id}\n**Code:**\n{code}", color=0x00ff00)
					embed.add_field(name="Loading code...", value="✅ **Code correct**")
					embed.add_field(name="Profile:", value=f"Registration: {create}\nJoin date: {login}", inline=False)
					await channel.send(embed=embed)
			else:
				await ctx.respond(f"Thanks, {ctx.author.mention}! ❤️\nYour code {code} check in terminal\ncode activate or not", ephemeral=True)
				await ctx.send(f"{ctx.author.mention} Your code is added")
				achan = int(responce_channel_id)
				channel = bot.get_channel(achan)
				if channel:
				embed = discord.Embed(title="Entered code", description=f"**User:** {ctx.author.mention}\n**User ID:** {ctx.author.id}\n**Code:**\n{code}", color=0xff0000)
				embed.add_field(name="Loading code...", value="🛑 **Code incorrect**")
				await channel.send(embed=embed)
	else:
		await ctx.respond("No server data found.", ephemeral=True)

@ba.error
async def ba(ctx, error):
	if isinstance(error, commands.CommandOnCooldown):
		em = discord.Embed(title="Slow it down bro!", description=f"Try again in {error.retry_after:.2f}s.", color=0xff0000)
		await ctx.respond(embed=em, ephemeral=True)

#Hangman game
@bot.event
async def on_reaction_add(reaction, user):
	if reaction.emoji == '☠️':
		json = find_json(user.id)
		if json != '':
		games.remove(json)
		print(games)
		await reaction.message.channel.send('Game has been stopped')


@bot.command(name="h")
@commands.has_permissions(manage_messages=True)
async def Hangman(ctx, user1: discord.User, user2: discord.User, chan: discord.TextChannel):
	await hangman_command(ctx, user1, user2, chan)


@bot.command(name="hangman")
@commands.has_permissions(manage_messages=True)
async def hangman(ctx, user1: discord.User, user2: discord.User, chan: discord.TextChannel):
	await hangman_command(ctx, user1, user2, chan)


def generate_embed(text):
	return discord.Embed(color=0xff0000, description=text)


async def hangman_command(ctx, user1, user2, chan):
	if find_json(ctx.author.id):
		await ctx.send('Game with these players already exists')
		return
	word = ' '.join(ctx.message.content.split()[4:])
	msg = await ctx.send(
		embed=generate_embed(f"<@{user1.id}> & <@{user2.id}>\nWord: {word}"))

	j = {
		"player1": user1.id,
		"player2": user2.id,
		"turn": 1,
		"channel": chan,
		"word": word.lower(),
		"letters": [],
		"messages": [msg],
		"id": len(games),
		"author": ctx.author.id
	}
	i = len(games)

	await msg.add_reaction('☠️')
	games.append(j)
	j['messages'].append(await chan.send(
		embed=generate_embed(f"Welcome to Hangman\n<@{user1.id}> vs <@{user2.id}>")
	))


async def parse_message(text, json):
	if text.lower().startswith('>') and len(text) > 1:
		if json['word'] == ' '.join(text[1:].split()):
			await json['channel'].send('✅ Correct')
			for i in ''.join(text[1:].split()):
				if i not in json['letters']:
					json['letters'].append(i)
		else:
			await json['channel'].send('🛑 Incorrect')
			switch_turn(json)
	elif len(text) != 1 or text in json['letters']:
		await json['channel'].send("⚠️ Please repeat, the letter was used")
		return False
	else:
		if text in json['word']:
			await json['channel'].send('✅ Yup')
		else:
			await json['channel'].send('🛑 Nope')
			switch_turn(json)
		json['letters'].append(text)
	await json['channel'].send(
		embed=generate_embed(await generate_hangman_message(json)))
	return True


@bot.event
async def on_message(message):
	if message.author.id == bot.user.id and len(
			message.embeds) == 1 and message.embeds[0].description.startswith(
				'Welcome to Hangman'):
		time.sleep(2)
		game = {}
		for game in games:
			if message in game['messages']:
				break

		await message.channel.send(
			embed=generate_embed(await generate_hangman_message(game)))

		def check(mes):
			return game[
				'player' +
				str(game['turn'])] == mes.author.id and mes.channel == game['channel']

		def json_check(j):
			return j in games

		m = ''
		while json_check(game):
			try:
				m = await bot.wait_for('message', check=check, timeout=30)
				await parse_message(m.content.lower(), game)
			except asyncio.TimeoutError:
				switch_turn(game)
				if json_check(game):
					await game['channel'].send(
						f'Run out of time! Now is turn <@{game["player" + str(game["turn"])]}>'
					)

	elif message.content.startswith('k!'):
		await bot.process_commands(message)


def switch_turn(json):
	if json['turn'] == 1:
		json['turn'] = 2
	else:
		json['turn'] = 1


def find_json(user):
	for i in games:
		if i['author'] == user or i['author'] == user:
			return i
	return ''


async def generate_hangman_message(json):
	global games
	s = f"<@{json['player' + str(json['turn'])]}>\nLetters: {', '.join(json['letters'])}\nTime: 30sec\n\n**"
	count = 0
	for i in json['word']:
		if i in json['letters']:
			s += str(i).upper()
			count += 1
		elif i == ' ':
			s += '\n'
			count += 1
		else:
			s += "⭐"
	if count == len(json['word']):
		s += f"**\n**Word is guessed!**\nWinner: <@{json['player' + str(json['turn'])]}>"
		games.remove(json)
		for i in json['messages']:
			await i.edit(
				embed=generate_embed(i.embeds[0].description + f"\n<@{json['player' + str(json['turn'])]}> won!")
			)
	else:
		s += "**\n\nUse >word if you know the word\n<a:30sec:947273928034893825> <a:10sec:947274015867822080>"
	return s

#Users commands
#Shake duel
@bot.slash_command(name="duel", description="Shake users")
@commands.has_permissions(manage_messages=True)
async def shake(ctx, role: Option(discord.Role, description="Choose role for shake")):
	mmbrs = []
	for rl in role.members:
		mmbrs.append(rl.mention)
		random.shuffle(mmbrs)
		members = "`"
		for i in range(1, len(mmbrs)):
				if i % 2 == 0:
					members = members + mmbrs[i] + "\n\n"
				else:
					members = members + mmbrs[i] + " "
		members = members + mmbrs[0]
		members = members + "`"
		embed = discord.Embed(title="Shake Duel", description=members, color=0x00000)
		await ctx.respond(embed=embed)
#Give roles
@bot.command(name="part")
@commands.has_any_role(1166824236405502035)
async def giverole(ctx, members: commands.Greedy[discord.Member]):
# Retrieve server data from the database based on the server ID
	server_id = str(ctx.guild.id)
	db_cursor.execute("SELECT * FROM server_data WHERE server_id=?", (server_id,))
	server_data = db_cursor.fetchone()
	if server_data:
		eas_channel_id = server_data[1]
		ea1_channel_id = server_data[2]
		embed = discord.Embed(title="Events participant role added", color=0xff0000)
		await ctx.send(embed=embed)
		for m in members:
			role = ctx.guild.get_role(1166824359235702824)
			if ctx.channel.id in [eas_channel_id, ea1_channel_id]:
				await m.add_roles(role)
			else:
				await ctx.send("Command has error", ephemeral=True)
	else:
		await ctx.send("No server data found.", ephemeral=True)

@bot.command(name="unpart")
@commands.has_any_role(1166824236405502035)
async def unrole(ctx, members: commands.Greedy[discord.Member]):
# Retrieve server data from the database based on the server ID
	server_id = str(ctx.guild.id)
	db_cursor.execute("SELECT * FROM server_data WHERE server_id=?", (server_id,))
	server_data = db_cursor.fetchone()
	if server_data:
		eas_channel_id = server_data[1]
		ea1_channel_id = server_data[2]
		embed = discord.Embed(title="Events participant role removed", color=0xff0000)
		await ctx.send(embed=embed)
		for m in members:
			role = ctx.guild.get_role(1166824359235702824)
			if ctx.channel.id in [eas_channel_id, ea1_channel_id]:
				await m.remove_roles(role)
			else:
				await ctx.send("Command has error", ephemeral=True)
	else:
				await ctx.send("No server data found.", ephemeral=True)

@bot.slash_command(name="mc", description="Give or remove MC Role")
@commands.has_any_role("Admins", "Global Moderators", "Regional Moderators", "Events MC")
async def mcrole(ctx, member: discord.Member = None):
# Retrieve server data from the database based on the server ID
	server_id = str(ctx.guild.id)
	db_cursor.execute("SELECT * FROM server_data WHERE server_id=?", (server_id,))
	server_data = db_cursor.fetchone()
	if server_data:
		mc_role_id = server_data[3]
		rolemc = ctx.guild.get_role(mc_role_id)
		if not member:
			member = ctx.author
			if rolemc in member.roles:
				await member.remove_roles(rolemc)
				await ctx.respond(f"Goodbye {member.mention}!", ephemeral=True)
			else:
				await member.add_roles(rolemc)
				await ctx.respond(f"Yay, you're an MC now {member.mention}!", ephemeral=True)
	else:
		await ctx.respond("No server data found.", ephemeral=True)

#Scrabble game command
#/scrabble
@bot.slash_command(name="scrabble", description="scrabble game")
@commands.has_permissions(manage_messages=True)
async def scrabble(ctx, phrase: Option(str, description="2 or 3 words"),
	scrnum: Option(int, description="number scrabblel"),
	channel: Option(discord.TextChannel, description="choose channel"),
	language: discord.Option(str, choices=["rus", "eng"], descriprion="choose language")):
	await ctx.respond(f"**Scrabble:** {phrase} №**{scrnum}**")

	final_phrase = phrase
	def check(m):
		return m.content.lower() == final_phrase.lower(
		) and m.channel.id == channel.id

	phrase = randomize_letters(phrase).split()
	ballsforquest = 0
	wordscount = len(phrase)
	if (wordscount == 2):
		bl_circle = random.randint(1, len(phrase[0]))
		rd_circle = random.randint(1, len(phrase[1]))
		bl_circle = bl_circle - 1
		rd_circle = rd_circle - 1
		phrase[0] = phrase[0][:bl_circle] + "🔵" + phrase[0][bl_circle + 1:]
		phrase[1] = phrase[1][:rd_circle] + "🔴" + phrase[1][rd_circle + 1:]
		ballsforquest = 1
		wrdballsforquest = "балл"
		if language == "rus":
			lastPhrase = "🔵 - 🔴 пропуски букв, для соответствующих слов"
		elif language == "eng":
			lastPhrase = "**🔵 & 🔴 are blanks for the respective words**"
	elif (wordscount == 3):
		bl_circle = random.randint(1, len(phrase[0]))
		rd_circle = random.randint(1, len(phrase[1]))
		grn_circle = random.randint(1, len(phrase[2]))
		bl_circle = bl_circle - 1
		rd_circle = rd_circle - 1
		grn_circle = grn_circle - 1
		phrase[0] = phrase[0][:bl_circle] + "🔵" + phrase[0][bl_circle + 1:]
		phrase[1] = phrase[1][:rd_circle] + "🔴" + phrase[1][rd_circle + 1:]
		phrase[2] = phrase[2][:rd_circle] + "🟢" + phrase[2][rd_circle + 1:]
		ballsforquest = 2
		wrdballsforquest = "балла"
		if language == "rus":
			lastPhrase = "🔵 - 🔴 - 🟢 пропуски букв, для соответствующих слов"
		elif language == "eng":
			lastPhrase = "**🔵 & 🔴 & 🟢 are blanks for the respective words**"
	phrase = " / ".join(phrase)
	phrase = phrase.upper()

	if language == "rus":
		await channel.send(
			f"__Скрэббл номер {scrnum}__\n{phrase}\n**{wordscount} слова**\n**{ballsforquest} {wrdballsforquest}**\n{lastPhrase}"
		)
	elif language == "eng":
		await channel.send(
			f"**Scrabble - Round {scrnum}**\n**{phrase}**\n**Words: {wordscount}\nPoints: {ballsforquest}**\n{lastPhrase}"
		)

	guess = await bot.wait_for("message", check=check, timeout=100000)
	gcu = guess.content
	if final_phrase.lower() == gcu.lower():
		athor = guess.author
		if wordscount == 2:
			if language == "rus":
				await channel.send(
					f"Правильный ответ: **{final_phrase.upper()}**\n{athor.mention}, +1 балл"
				)
			elif language == "eng":
				await channel.send(
					f"__Correct answer:__ **{final_phrase.upper()}**\n**+1 point for {athor.mention}**"
				)
		elif wordscount == 3:
			if language == "rus":
				await channel.send(
					f"Правильный ответ: **{final_phrase.upper()}**\n{athor.mention}, +2 балла"
				)
			elif language == "eng":
				await channel.send(
					f"__Correct answer:__ **{final_phrase.upper()}**\n**+2 points for {athor.mention}**"
				)

#Scrabble game command
#/question
@bot.slash_command(name="question", description="question scrabble")
@commands.has_permissions(manage_messages=True)
async def question(ctx, question: Option(str, description="write question"),
	answer: Option(str, description="two words"),
	channel: Option(discord.TextChannel, description="choose channel"),
	language: discord.Option(str, choices=["rus", "eng"], descriprion="choose language")):

	def check(m):
		return m.content.lower() == answer.lower() and m.channel.id == channel.id

	await ctx.respond(f"**Question:** {question}\n**Answer:** {answer}")
	wordscount = len(answer.split())
	if len(answer.split()) == 3:
		endword = ""
		for i in range(0, len(answer.split()[0])):
			endword = endword + "🟡"
		endword = endword + " / "
		for i in range(0, len(answer.split()[1])):
			endword = endword + "🟡"
		endword = endword + " / "
		for i in range(0, len(answer.split()[2])):
			endword = endword + "🟡"
		ballsforquest = 2
		wrdballsforquest = "балла"
	elif len(answer.split()) == 2:
		endword = ""
		for i in range(0, len(answer.split()[0])):
			endword = endword + "🟡"
		endword = endword + " / "
		for i in range(0, len(answer.split()[1])):
			endword = endword + "🟡"
		ballsforquest = 1
		wrdballsforquest = "балл"
	if language == "rus":
		await channel.send(
			f"__Скрэббл вопрос__\n**Вопрос: **{question}\n{endword}\n**{wordscount} слова**\n**{ballsforquest} {wrdballsforquest}**\n🟡 - замена каждой буквы в словах"
		)
	elif language == "eng":
		await channel.send(
			f"**__Plus question__** {question}\n**Scrabble:** {endword}\n**Pts. for trivia : {ballsforquest}**\n**To unlock the letters, someone must answer correctly to the trivia question!**"
		)
	guess = await bot.wait_for("message", check=check, timeout=100000)
	gcu = guess.content
	if answer.lower() == gcu.lower():
		athor = guess.author
		if len(answer.split()) == 2:
			if language == "rus":
				await channel.send(
					f"Правильный ответ: **{answer.upper()}**\n{athor.mention}, +1 балл")
			elif language == "eng":
				await channel.send(
					f"__Correct answer:__ **{answer.upper()}\n+1 point for {athor.mention}**"
				)
		elif len(answer.split()) == 3:
			if language == "rus":
				await channel.send(
					f"Правильный ответ: **{answer.upper()}**\n{athor.mention}, +2 балла")
			elif language == "eng":
				await channel.send(
					f"__Correct answer:__ **{answer.upper()}\n+2 points for {athor.mention}**"
				)

bot.run(TOKEN)
