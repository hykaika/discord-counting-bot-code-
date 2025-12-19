import discord
import re
from discord.ext import commands


TOKEN = DEIN-BOT-Token'


COUNTING_CHANNEL_ID = CHANNEL-ID

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

class GameState:
    def __init__(self):
        self.current_number = 0
        self.last_user = None
        self.game_active = True
        self.used_expressions = set()

game_state = GameState()

def is_safe_expression(expr):
    """Prüft, ob der Ausdruck sicher ist (nur Zahlen und Grundrechenarten)"""
   
    if not re.match(r'^[\d\s\+\-\*\/\(\)]+$', expr):
        return False
    
 
    if re.search(r'[\+\-\*\/]{2,}', expr):
        return False
    
    
    if '()' in expr:
        return False
    
    return True

def calculate_expression(expr):
    """Berechnet einen mathematischen Ausdruck sicher"""
    try:
        
        if not is_safe_expression(expr):
            return None
        
     
        expr = expr.replace(' ', '').replace('x', '*').replace('×', '*')
        
        
        result = eval(expr, {"__builtins__": {}}, {})
        
        
        if result in (float('inf'), float('-inf'), float('nan')):
            return None
        
        
        if isinstance(result, (int, float)):
            if float(result).is_integer():
                return int(result)
            return None  
        return None
    except:
        return None

@bot.event
async def on_ready():
    print(f'✅ Bot ist online als {bot.user}')
    print(f'📊 Counting Channel ID: {COUNTING_CHANNEL_ID}')
    print('──────────────────────────────')

@bot.event
async def on_message(message):
    
    if message.author == bot.user:
        return
    
    
    if message.channel.id != COUNTING_CHANNEL_ID:
        return await bot.process_commands(message)
    
    content = message.content.strip()
    
    
    if content.startswith('!'):
        return await bot.process_commands(message)
    
   
    if not game_state.game_active:
        return
    
    
    if message.author.id == game_state.last_user:
        await message.add_reaction('🚫')
        error_msg = await message.channel.send(
            f'❌ {message.author.mention} darf nicht zweimal hintereinander schreiben!\n'
            f'**Spiel wird zurückgesetzt! Starte mit 1.**'
        )
        game_state.current_number = 0
        game_state.last_user = None
        game_state.used_expressions.clear()
        return
    
   
    if content.isdigit():
        user_number = int(content)
    else:
        
        user_number = calculate_expression(content)
        if user_number is None:
            await message.add_reaction('❌')
            await message.channel.send(
                f'❌ Ungültige Eingabe von {message.author.mention}!\n'
                f'**Nur Zahlen und + - * / erlaubt. Keine Dezimalzahlen!**\n'
                f'Spiel wird zurückgesetzt. Starte mit 1.'
            )
            game_state.current_number = 0
            game_state.last_user = None
            game_state.used_expressions.clear()
            return
    
    
    expected_number = game_state.current_number + 1
    
   
    if user_number == expected_number:
      
        await message.add_reaction('✅')
        game_state.current_number = user_number
        game_state.last_user = message.author.id
        
       
        next_number = user_number + 1
        embed = discord.Embed(
            title="✅ Korrekt!",
            description=f"{message.author.mention} hat **{user_number}** geschrieben.",
            color=discord.Color.green()
        )
        embed.add_field(name="Nächste Zahl", value=f"**{next_number}**", inline=True)
        embed.add_field(name="Letzte Zahl", value=game_state.current_number, inline=True)
        embed.set_footer(text=f"Spieler: {message.author.name}")
        
        await message.channel.send(embed=embed, delete_after=15)
    else:
        
        await message.add_reaction('❌')
        embed = discord.Embed(
            title="❌ Fehler!",
            description=f"{message.author.mention} hat **{user_number}** geschrieben.",
            color=discord.Color.red()
        )
        embed.add_field(name="Erwartet wurde", value=f"**{expected_number}**", inline=True)
        embed.add_field(name="Spiel wird zurückgesetzt", value="Starte mit 1", inline=True)
        embed.set_footer(text="Der nächste Spieler beginnt mit 1")
        
        await message.channel.send(embed=embed)
        game_state.current_number = 0
        game_state.last_user = None
        game_state.used_expressions.clear()

@bot.command(name='start')
@commands.has_permissions(administrator=True)
async def start_game(ctx):
    """Startet das Spiel"""
    if ctx.channel.id != COUNTING_CHANNEL_ID:
        return
    
    game_state.game_active = True
    game_state.current_number = 0
    game_state.last_user = None
    game_state.used_expressions.clear()
    
    embed = discord.Embed(
        title="🎮 Spiel gestartet!",
        description="Das Counting-Spiel wurde gestartet.",
        color=discord.Color.green()
    )
    embed.add_field(name="Regeln", value="1. Beginne mit **1**\n2. Immer +1 zählen\n3. Kein Spieler darf zweimal hintereinander\n4. Mathe-Ausdrücke erlaubt (+ - * /)", inline=False)
    embed.add_field(name="Startzahl", value="**1**", inline=True)
    embed.set_footer(text=f"Admin: {ctx.author.name}")
    
    await ctx.send(embed=embed)

@bot.command(name='stop')
@commands.has_permissions(administrator=True)
async def stop_game(ctx):
    """Stoppt das Spiel"""
    if ctx.channel.id != COUNTING_CHANNEL_ID:
        return
    
    game_state.game_active = False
    embed = discord.Embed(
        title="⏹️ Spiel gestoppt",
        description="Das Counting-Spiel wurde pausiert.",
        color=discord.Color.orange()
    )
    embed.add_field(name="Letzte Zahl", value=game_state.current_number, inline=True)
    embed.set_footer(text=f"Admin: {ctx.author.name}")
    
    await ctx.send(embed=embed)

@bot.command(name='status')
async def game_status(ctx):
    """Zeigt den aktuellen Spielstatus"""
    if ctx.channel.id != COUNTING_CHANNEL_ID:
        return
    
    embed = discord.Embed(
        title="📊 Spielstatus",
        color=discord.Color.blue()
    )
    
    if game_state.game_active:
        status_text = "✅ Laufend"
        next_player = f"**{game_state.current_number + 1}**"
    else:
        status_text = "⏸️ Pausiert"
        next_player = "Spiel ist pausiert"
    
    embed.add_field(name="Status", value=status_text, inline=True)
    embed.add_field(name="Aktuelle Zahl", value=game_state.current_number, inline=True)
    embed.add_field(name="Nächste Zahl", value=next_player, inline=True)
    
    if game_state.last_user:
        user = await bot.fetch_user(game_state.last_user)
        embed.add_field(name="Letzter Spieler", value=user.mention, inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='reset')
@commands.has_permissions(administrator=True)
async def reset_game(ctx):
    """Setzt das Spiel zurück"""
    if ctx.channel.id != COUNTING_CHANNEL_ID:
        return
    
    game_state.current_number = 0
    game_state.last_user = None
    game_state.used_expressions.clear()
    
    embed = discord.Embed(
        title="🔄 Spiel zurückgesetzt",
        description="Das Spiel wurde auf 0 zurückgesetzt.",
        color=discord.Color.green()
    )
    embed.add_field(name="Startzahl", value="**1**", inline=True)
    embed.set_footer(text=f"Admin: {ctx.author.name}")
    
    await ctx.send(embed=embed)

@bot.command(name='set')
@commands.has_permissions(administrator=True)
async def set_number(ctx, number: int):
    """Setzt die aktuelle Zahl (Admin)"""
    if ctx.channel.id != COUNTING_CHANNEL_ID:
        return
    
    if number < 0:
        await ctx.send("❌ Zahl muss positiv sein!")
        return
    
    game_state.current_number = number
    game_state.last_user = None
    game_state.used_expressions.clear()
    
    embed = discord.Embed(
        title="📝 Zahl gesetzt",
        description=f"Aktuelle Zahl wurde auf **{number}** gesetzt.",
        color=discord.Color.green()
    )
    embed.add_field(name="Nächste Zahl", value=f"**{number + 1}**", inline=True)
    embed.set_footer(text=f"Admin: {ctx.author.name}")
    
    await ctx.send(embed=embed)

@bot.command(name='rules')
async def show_rules(ctx):
    """Zeigt die Spielregeln"""
    embed = discord.Embed(
        title="📚 Spielregeln - Counting Game",
        color=discord.Color.purple()
    )
    
    rules = """
    1️⃣ **Beginne mit der Zahl 1**
    2️⃣ **Jeder Spieler erhöht um 1** (1 → 2 → 3 → ...)
    3️⃣ **Mathematische Ausdrücke erlaubt**: + - * / (z.B. "2+2" für 4)
    4️⃣ **Keine Dezimalzahlen** - nur ganze Zahlen!
    5️⃣ **Kein Spieler darf zweimal hintereinander**
    6️⃣ **Bei Fehler startet das Spiel wieder bei 1**
    7️⃣ **Nächste Zahl immer: Aktuelle Zahl + 1**
    """
    
    embed.add_field(name="Regeln", value=rules, inline=False)
    embed.add_field(name="Beispiele", value="• `5` → korrekt nach 4\n• `3*2` → korrekt nach 5\n• `10/2` → korrekt nach 4", inline=False)
    embed.set_footer(text="Viel Spaß beim Spielen!")
    
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Du hast keine Berechtigung für diesen Befehl!")
    elif isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Ungültige Argumente! Bitte überprüfe deine Eingabe.")

if __name__ == '__main__':
    print("=" * 50)
    print("Discord Counting Bot")
    print("=" * 50)
    print("\n  WICHTIG: Bevor du startest:")
    print("1. Füge deinen Bot-Token ein (Zeile 6)")
    print("2. Füge die Channel-ID ein (Zeile 9)")
    print("3. Aktiviere in Discord Developer Portal:")
    print("   - MESSAGE CONTENT INTENT")
    print("   - SERVER MEMBERS INTENT")
    print("=" * 50)
    
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print(" FEHLER: Ungültiger Bot-Token!")
        print("Bitte überprüfe deinen Token in Zeile 6")
    except Exception as e:
        print(f" FEHLER: {e}")