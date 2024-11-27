PlexStreamBot 🎵🤖
Stream your Plex music library directly into Discord voice channels!


📋 Features
🎶 Stream Music: Play tracks, albums, or shuffled playlists directly from your Plex library.
🔍 Search and Queue: Find songs, albums, or artists and add them to the queue with simple slash commands.
🎤 Artist Functions: Search for artists, play all songs by an artist, or shuffle their entire discography.
📀 Album Playback: Search for albums, play an album by title, or play by unique album ID.
🔀 Shuffle: Shuffle your entire library or specific artist's discography.
🎛️ Control Playback: Commands for pausing, resuming, skipping, stopping, and clearing the queue.
🎧 Rich Presence: Displays the currently playing track and artist in the bot’s Discord activity status.
🛠️ Slash Commands: Intuitive and easy-to-use commands for interacting with the bot.
🚀 Getting Started
Prerequisites
Python 3.8+
Plex Media Server with a configured music library.
Discord Application: Create a bot on the Discord Developer Portal.
FFmpeg: Installed and accessible from your system's PATH.
Installation
Clone the Repository:

bash
Copy code
git clone https://github.com/ianarsenault-tn/Plex-Discord-Music-Bot.git
cd Plex-Discord-Music-Bot
Set Up a Virtual Environment:

bash
Copy code
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install Dependencies:

bash
Copy code
pip install -r requirements.txt
Configure Environment Variables: Create a .env file in the project root and add the following:

env
Copy code
PLEX_URL=http://<your-plex-server-ip>:32400
PLEX_TOKEN=<your-plex-token>
DISCORD_BOT_TOKEN=<your-discord-bot-token>
APPLICATION_ID=<your-discord-application-id>
Run the Bot:

bash
Copy code
python plex_discord_bot.py
🛠️ Commands
Command	Description
/join	Make the bot join your current voice channel.
/leave	Disconnect the bot from the voice channel.
/play	Play a specific track from your Plex library.
/queue	Add a track to the queue.
/search	Search for tracks in your Plex library.
/searchartist	Search for an artist in your Plex library.
/playartist	Play all songs by a specific artist.
/shuffleartist	Shuffle and play songs by a specific artist.
/searchalbum	Search for albums in your Plex library.
/playalbum	Play an album by its title.
/playalbumbyid	Play an album by its unique ID.
/albuminfo	Get detailed information about an album.
/shuffle	Shuffle and play random tracks from your library.
/next	Skip to the next track in the queue.
/pause	Pause the current track.
/resume	Resume playback.
/stop	Stop playback and clear the queue.
📖 Usage
Example Commands:
Search for a Track:
/search query:<track name>

Play a Song:
/play query:<song title>

Shuffle Your Library:
/shuffle

Search for an Artist:
/searchartist query:<artist name>

Play All Songs by an Artist:
/playartist query:<artist name>

Shuffle Songs by an Artist:
/shuffleartist query:<artist name>

Search for an Album:
/searchalbum query:<album name>

Play an Album by ID:
/playalbumbyid id:<album ID>

🛡️ Security Tips
Environment Variables:
Store sensitive information (Plex and Discord tokens) in a .env file. Never hardcode these in your code.

Restrict Access:
Ensure your Plex server is only accessible to authorized users.

.gitignore:
Add .env to .gitignore to prevent accidental sharing of sensitive information.

🌟 Contributing
Contributions, feature requests, and bug reports are welcome!

Fork the repository.
Create a new branch for your feature or fix.
Submit a pull request with a clear description of the changes.
📜 License
This project is licensed under the MIT License. See the LICENSE file for details.

❤️ Acknowledgments
PlexAPI: Python library for interacting with Plex.
Discord.py: Discord API wrapper for Python.
FFmpeg: Enables high-quality audio streaming.
