import discord
import re
import json
import os
import datetime
import logging
from discord.ext import commands
from discord import app_commands
from typing import Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger('CountingBot')

if not os.path.exists("backups"):
    os.makedirs("backups")

TOKEN = 'Bot-Token'
COUNTING_CHANNEL_ID = Channel-ID
GUILD_ID = Server-ID 
SAVE_FILE = "counting_save.json"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True


class GameState:
    def __init__(self):
        self.current_number = 0
        self.high_score = 0
        self.high_score_holder = "Niemand"
        self.last_user_id = None
        self.is_paused = False
        self.total_mistakes = 0

    def to_dict(self):
        return {
            "current_number": self.current_number,
            "high_score": self.high_score,
            "high_score_holder": self.high_score_holder,
            "last_user_id": self.last_user_id,
            "is_paused": self.is_paused,
            "total_mistakes": self.total_mistakes
        }

    def load_dict(self, data):
        self.current_number = data.get("current_number", 0)
        self.high_score = data.get("high_score", 0)
        self.high_score_holder = data.get("high_score_holder", "Niemand")
        self.last_user_id = data.get("last_user_id", None)
        self.is_paused = data.get("is_paused", False)
        self.total_mistakes = data.get("total_mistakes", 0)

game_state = GameState()


def save_game(custom_path=None):
    path = custom_path or SAVE_FILE
    try:
        with open(path, "w") as f:
            json.dump(game_state.to_dict(), f, indent=4)
        return True
    except Exception as e:
        logger.error(f"Fehler beim Speichern ({path}): {e}")
        return False

def load_game(custom_path=None):
    path = custom_path or SAVE_FILE
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                game_state.load_dict(json.load(f))
            return True
        except Exception as e:
            logger.error(f"Fehler beim Laden ({path}): {e}")
    return False

def calculate_expression(expr: str) -> Optional[int]:
    if not re.match(r'^[\d\s\+\-\*\/\(\)x×]+$', expr):
        return None
    try:
        clean_expr = expr.replace('x', '*').replace('×', '*')
        result = eval(clean_expr, {"__builtins__": {}}, {})
        if isinstance(result, (int, float)) and not isinstance(result, bool):
            return int(result) if float(result).is_integer() else None
    except:
        return None
    return None


class CountingBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        load_game()
        guild = discord.Object(id=GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        logger.info(f"✅ Bot bereit und Commands synchronisiert.")

bot = CountingBot()


@bot.tree.command(name="ct", description="Löscht eine Anzahl an Nachrichten (Admin)")
@app_commands.checks.has_permissions(administrator=True)
async def clear_chat(interaction: discord.Interaction, anzahl: int):
    await interaction.response.send_message(f"🧹 Lösche {anzahl} Nachrichten...", ephemeral=True)
    await interaction.channel.purge(limit=anzahl)

@bot.tree.command(name="set-count", description="Setzt den Zähler manuell auf eine Zahl (Admin)")
@app_commands.checks.has_permissions(administrator=True)
async def set_count(interaction: discord.Interaction, zahl: int):
    game_state.current_number = zahl
    game_state.last_user_id = None
    save_game()
    await interaction.response.send_message(f"✅ Zähler auf **{zahl}** gesetzt. Nächste Zahl: **{zahl + 1}**")

@bot.tree.command(name="save-as", description="Speichert ein Backup des Spielstands (Admin)")
@app_commands.checks.has_permissions(administrator=True)
async def save_as(interaction: discord.Interaction, name: str):
    clean_name = "".join(x for x in name if x.isalnum())
    path = f"backups/{clean_name}.json"
    if save_game(path):
        await interaction.response.send_message(f"💾 Backup `{clean_name}` wurde erstellt.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Fehler beim Speichern.", ephemeral=True)

@bot.tree.command(name="load-from", description="Lädt ein Backup (Admin)")
@app_commands.checks.has_permissions(administrator=True)
async def load_from(interaction: discord.Interaction, name: str):
    clean_name = "".join(x for x in name if x.isalnum())
    path = f"backups/{clean_name}.json"
    if load_game(path):
        save_game()
        await interaction.response.send_message(f"📂 Backup `{clean_name}` erfolgreich geladen!")
    else:
        await interaction.response.send_message(f"❌ Backup `{clean_name}` nicht gefunden.", ephemeral=True)

@bot.tree.command(name="backups-list", description="Zeigt alle verfügbaren Backups (Admin)")
@app_commands.checks.has_permissions(administrator=True)
async def list_backups(interaction: discord.Interaction):
    files = [f.replace(".json", "") for f in os.listdir("backups") if f.endswith(".json")]
    if not files:
        await interaction.response.send_message("Keine Backups vorhanden.", ephemeral=True)
    else:
        liste = "\n".join([f"- {name}" for name in files])
        await interaction.response.send_message(f"**Verfügbare Backups:**\n{liste}", ephemeral=True)

@bot.tree.command(name="pause", description="Pausiert das Zählen (Admin)")
@app_commands.checks.has_permissions(administrator=True)
async def pause_game(interaction: discord.Interaction):
    game_state.is_paused = True
    save_game()
    await interaction.response.send_message("⏸️ Spiel pausiert.", ephemeral=True)

@bot.tree.command(name="resume", description="Setzt das Zählen fort (Admin)")
@app_commands.checks.has_permissions(administrator=True)
async def resume_game(interaction: discord.Interaction):
    game_state.is_paused = False
    save_game()
    await interaction.response.send_message("▶️ Spiel fortgesetzt.", ephemeral=True)

@bot.tree.command(name="stats", description="Zeigt den aktuellen Spielstand")
async def stats(interaction: discord.Interaction):
    embed = discord.Embed(title="📊 Counting Stats", color=discord.Color.gold(), timestamp=datetime.datetime.now())
    embed.add_field(name="Zähler", value=f"**{game_state.current_number}**", inline=True)
    embed.add_field(name="Nächste Zahl", value=f"**{game_state.current_number + 1}**", inline=True)
    embed.add_field(name="🏆 Rekord", value=f"**{game_state.high_score}** von {game_state.high_score_holder}", inline=False)
    await interaction.response.send_message(embed=embed)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name=f"Zahl {game_state.current_number}"))

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot or message.channel.id != COUNTING_CHANNEL_ID:
        return
    if game_state.is_paused:
        return

    val = calculate_expression(message.content.strip())
    if val is None: return

    expected = game_state.current_number + 1

    if message.author.id == game_state.last_user_id:
        game_state.current_number = 0
        game_state.last_user_id = None
        save_game()
        await message.channel.send(f"❌ {message.author.mention} hat zweimal gezählt! Reset auf 0.")
        return

    if val == expected:
        game_state.current_number = val
        game_state.last_user_id = message.author.id
        if val > game_state.high_score:
            game_state.high_score = val
            game_state.high_score_holder = message.author.display_name
        save_game()
        await message.add_reaction('✅')
    else:
        
        game_state.current_number = 0
        game_state.last_user_id = None
        save_game()
        await message.channel.send(f"💥 Fehler! {message.author.mention} hat die Kette unterbrochen. Reset!")
        await message.add_reaction('❌')

if __name__ == '__main__':
    bot.run(TOKEN)
