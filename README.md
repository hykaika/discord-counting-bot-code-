# discord-counting-bot-code
Discord Counting Bot (German)
A robust Discord bot built with discord.py to manage a counting game. This bot features mathematical expression parsing, an administrative backup system, and persistent state storage.

Key Features
Mathematical Support: Recognizes expressions such as 10+5 or 2x8 as valid counts using a secure evaluation logic.

Anti-Cheat Logic: Prevents the same user from counting twice in a row.

State Persistence: Automatically saves all data to a JSON file to ensure progress is maintained through bot restarts.

Backup System: Includes administrative tools to create, list, and restore named snapshots of the game state.

Statistics: Provides formatted data regarding the current count and all-time records.

German Localization: 
The bot communicates entirely in German and utilizes German command names.
CommandsThe bot utilizes Slash Commands for all interactions.

Command Permission Description

/stats Everyone Displays the current number, the next expected number, and the high score. 

/set-count Admin Manually adjusts the counter to a specific value.

/pause Admin Freezes the counting game.

/resume Admin Un freezes the counting game.

/save-as Admin Creates a custom backup file in the backups folder. 

/load-from Admin Restores a specific game state from a saved backup.

/backups-list Admin Displays a list of all available backup files.

/ct Admin Removes a specified number of messages from the channel.
