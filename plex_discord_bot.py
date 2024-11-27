import discord
from discord.ext import commands
from discord import app_commands
from plexapi.server import PlexServer
import random
import asyncio
import logging
import traceback
from discord import PCMVolumeTransformer

logging.basicConfig(level=logging.INFO)

# Tokens and URLs (Consider storing these in environment variables for security)
PLEX_URL = 'YOUR_PLEX_URL'
PLEX_TOKEN = 'YOUR_PLEX_TOKEN'
DISCORD_BOT_TOKEN = 'YOUR_DISCORD_BOT_TOKEN'
APPLICATION_ID = 'YOUR_APPLICATION_ID'  # Replace with your application's ID

# Initialize Plex
plex = PlexServer(PLEX_URL, PLEX_TOKEN)

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

# Define the album_search_results dictionary
album_search_results = {}

# Bot class
class MusicBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents, application_id=APPLICATION_ID)
        self.music_queues = {}  # Holds the music queue for each guild

    async def setup_hook(self):
        await self.clear_and_sync_commands()

    async def clear_and_sync_commands(self):
        # Remove the 'searchmusic' command
        global_commands = await self.tree.fetch_commands()
        for cmd in global_commands:
            if cmd.name == 'searchmusic':
                await cmd.delete()
                print(f"Deleted global command: {cmd.name}")

        # If using guild-specific commands, do the same for each guild
        # guild = discord.Object(id=YOUR_GUILD_ID)
        # guild_commands = await self.tree.fetch_commands(guild=guild)
        # for cmd in guild_commands:
        #     if cmd.name == 'searchmusic':
        #         await cmd.delete(guild=guild)
        #         print(f"Deleted guild command: {cmd.name}")

        # Sync the command tree
        await self.tree.sync()
        print("Command tree synced.")

bot = MusicBot()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

def get_guild_queue(guild_id):
    if guild_id not in bot.music_queues:
        bot.music_queues[guild_id] = []
    return bot.music_queues[guild_id]

# FFmpeg options
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

# In your play_next function
async def play_next(guild, text_channel):
    voice_client = guild.voice_client
    if not voice_client or not voice_client.is_connected():
        # Handle if the bot is not connected
        await bot.change_presence(activity=None)
        return

    guild_id = guild.id
    queue = get_guild_queue(guild_id)
    if queue:
        track = queue.pop(0)
        url = track.getStreamURL(token=PLEX_TOKEN)
        try:
            # Use FFmpegOpusAudio for better compatibility
            source = discord.FFmpegOpusAudio(url)
            voice_client.play(
                source, after=lambda e: bot.loop.create_task(play_next_wrapper(guild, text_channel))
            )

            # Update bot's activity status
            activity = discord.Activity(type=discord.ActivityType.listening, name=f"{track.artist().title} - {track.title}")
            await bot.change_presence(activity=activity)

            await text_channel.send(f'Now playing: {track.title} - {track.artist().title}')
        except Exception as e:
            await text_channel.send('An error occurred while trying to play the track.')
            logging.error(f'Error in play_next: {e}', exc_info=True)
            traceback.print_exc()
            # Proceed to the next track in case of error
            await play_next(guild, text_channel)
    else:
        await voice_client.disconnect()
        # Clear bot's activity status
        await bot.change_presence(activity=None)

# Wrapper to handle interaction expiry
async def play_next_wrapper(guild, text_channel):
    try:
        await play_next(guild, text_channel)
    except Exception as e:
        logging.error(f'Error in play_next_wrapper: {e}')
        traceback.print_exc()

# Join command
@bot.tree.command(name="join", description="Join your voice channel")
async def join(interaction: discord.Interaction):
    if interaction.user.voice:
        channel = interaction.user.voice.channel
        await channel.connect(self_deaf=False, self_mute=False)
        await interaction.response.send_message(f"Joined {channel}", ephemeral=True)
    else:
        await interaction.response.send_message(
            "You are not connected to a voice channel.", ephemeral=True
        )


# Leave command
@bot.tree.command(name="leave", description="Leave the voice channel")
async def leave(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("Disconnected.", ephemeral=True)
    else:
        await interaction.response.send_message(
            "I'm not connected to a voice channel.", ephemeral=True
        )

# Search command
@bot.tree.command(name="search", description="Search for a track in your Plex library")
@app_commands.describe(query="The song title to search for")
async def search(interaction: discord.Interaction, query: str):
    await interaction.response.defer()
    tracks = plex.library.section('Music').searchTracks(title=query, maxresults=20)
    if tracks:
        response = '\n'.join(
            [f'{idx+1}. {track.title} - {track.artist().title}' for idx, track in enumerate(tracks)]
        )
        await interaction.followup.send(response)
    else:
        await interaction.followup.send('No tracks found.')
        
# Search Artist command
@bot.tree.command(name="searchartist", description="Search for an artist in your Plex library")
@app_commands.describe(query="The artist name to search for")
async def searchartist(interaction: discord.Interaction, query: str):
    await interaction.response.defer()
    artists = plex.library.section('Music').searchArtists(title=query, maxresults=20)
    if artists:
        response = '\n'.join(
            [f'{idx+1}. {artist.title}' for idx, artist in enumerate(artists)]
        )
        await interaction.followup.send(response)
    else:
        await interaction.followup.send('No artists found.')

# Play Artist command
@bot.tree.command(name="playartist", description="Play all songs by an artist")
@app_commands.describe(query="The artist name")
async def playartist(interaction: discord.Interaction, query: str):
    await interaction.response.defer()
    if not interaction.guild.voice_client:
        if interaction.user.voice:
            channel = interaction.user.voice.channel
            await channel.connect()
        else:
            await interaction.followup.send("You are not connected to a voice channel.")
            return

    artists = plex.library.section('Music').searchArtists(title=query, maxresults=1)
    if artists:
        artist = artists[0]
        tracks = artist.tracks()
        if tracks:
            guild_id = interaction.guild.id
            queue = get_guild_queue(guild_id)
            queue.clear()  # Optional: Clear existing queue
            queue.extend(tracks)
            await interaction.followup.send(f'Added all songs by "{artist.title}" to the queue.')

            # Start playback if not already playing
            if not interaction.guild.voice_client.is_playing():
                await play_next(interaction.guild, interaction.channel)
        else:
            await interaction.followup.send('No tracks found for this artist.')
    else:
        await interaction.followup.send('Artist not found.')

# Shuffle Artist command
@bot.tree.command(name="shuffleartist", description="Shuffle and play songs by an artist")
@app_commands.describe(query="The artist name")
async def shuffleartist(interaction: discord.Interaction, query: str):
    await interaction.response.defer()
    if not interaction.guild.voice_client:
        if interaction.user.voice:
            channel = interaction.user.voice.channel
            await channel.connect()
        else:
            await interaction.followup.send("You are not connected to a voice channel.")
            return

    artists = plex.library.section('Music').searchArtists(title=query, maxresults=1)
    if artists:
        artist = artists[0]
        tracks = artist.tracks()
        if tracks:
            random.shuffle(tracks)
            guild_id = interaction.guild.id
            queue = get_guild_queue(guild_id)
            queue.clear()  # Optional: Clear existing queue
            queue.extend(tracks)
            await interaction.followup.send(f'Shuffled and added songs by "{artist.title}" to the queue.')

            # Start playback if not already playing
            if not interaction.guild.voice_client.is_playing():
                await play_next(interaction.guild, interaction.channel)
        else:
            await interaction.followup.send('No tracks found for this artist.')
    else:
        await interaction.followup.send('Artist not found.')


# Search Album command        
@bot.tree.command(name="searchalbum", description="Search for an album in your Plex library")
@app_commands.describe(query="The album title to search for")
async def searchalbum(interaction: discord.Interaction, query: str):
    await interaction.response.defer()
    albums = plex.library.section('Music').searchAlbums(title=query, maxresults=20)
    if albums:
        response = '\n'.join(
            [f'ID {album.ratingKey}: {album.title} - {album.artist().title}' for album in albums]
        )
        await interaction.followup.send(response + "\nUse `/playalbumbyid id:<ID>` to play an album.")
    else:
        await interaction.followup.send('No albums found.')

# Play By album ID
@bot.tree.command(name="playalbumbyid", description="Play an album by its ID")
@app_commands.describe(id="The ID of the album from the search results")
async def playalbumbyid(interaction: discord.Interaction, id: int):
    # Defer the interaction to give the bot more time to respond
    await interaction.response.defer()
    try:
        # Attempt to fetch the album using the provided ID
        album = plex.fetchItem(int(id))
        if album and album.type == 'album':
            tracks = album.tracks()
            if tracks:
                # Ensure the bot is connected to a voice channel
                if not interaction.guild.voice_client:
                    if interaction.user.voice:
                        channel = interaction.user.voice.channel
                        await channel.connect()
                    else:
                        await interaction.followup.send("You are not connected to a voice channel.")
                        return
                guild_id = interaction.guild.id
                queue = get_guild_queue(guild_id)
                queue.clear()  # Optional: Clear existing queue
                queue.extend(tracks)
                await interaction.followup.send(f'Added album \"{album.title}\" by {album.artist().title} to the queue.')

                # Start playback if not already playing
                if not interaction.guild.voice_client.is_playing():
                    await play_next(interaction.guild, interaction.channel)
            else:
                await interaction.followup.send('No tracks found in this album.')
        else:
            await interaction.followup.send('Album not found. Please ensure you have the correct ID.')
    except Exception as e:
        # Log the exception and inform the user
        logging.error(f'Error in playalbumbyid: {e}')
        traceback.print_exc()
        await interaction.followup.send('An error occurred while fetching the album.')

# Album Info command
@bot.tree.command(name="albuminfo", description="Get detailed information about an album")
@app_commands.describe(query="The album title")
async def albuminfo(interaction: discord.Interaction, query: str):
    await interaction.response.defer()
    albums = plex.library.section('Music').searchAlbums(title=query, maxresults=1)
    if albums:
        album = albums[0]
        track_list = '\n'.join([f'{idx+1}. {track.title}' for idx, track in enumerate(album.tracks())])
        response = f'Album: {album.title}\nArtist: {album.artist().title}\nTracks:\n{track_list}'
        await interaction.followup.send(response)
    else:
        await interaction.followup.send('Album not found.')

# Play Album command
@bot.tree.command(name="playalbum", description="Play an album from your Plex library")
@app_commands.describe(query="The album title to play")
async def playalbum(interaction: discord.Interaction, query: str):
    await interaction.response.defer()
    if not interaction.guild.voice_client:
        if interaction.user.voice:
            channel = interaction.user.voice.channel
            await channel.connect()
        else:
            await interaction.followup.send("You are not connected to a voice channel.")
            return

    albums = plex.library.section('Music').searchAlbums(title=query, maxresults=1)
    if albums:
        album = albums[0]
        tracks = album.tracks()
        if tracks:
            guild_id = interaction.guild.id
            queue = get_guild_queue(guild_id)
            queue.clear()  # Optional: Clear existing queue to play the album immediately
            queue.extend(tracks)
            await interaction.followup.send(f'Added album "{album.title}" by {album.artist().title} to the queue.')

            # Start playback if not already playing
            if not interaction.guild.voice_client.is_playing():
                await play_next(interaction.guild, interaction.channel)
        else:
            await interaction.followup.send('No tracks found in this album.')
    else:
        await interaction.followup.send('Album not found.')

# Play command
@bot.tree.command(name="play", description="Play a track from your Plex library")
@app_commands.describe(query="The song title to play")
async def play(interaction: discord.Interaction, query: str):
    await interaction.response.defer()
    if not interaction.guild.voice_client:
        if interaction.user.voice:
            channel = interaction.user.voice.channel
            await channel.connect()
        else:
            await interaction.followup.send("You are not connected to a voice channel.")
            return

    tracks = plex.library.section('Music').searchTracks(title=query, maxresults=1)
    if tracks:
        track = tracks[0]
        guild_id = interaction.guild.id
        queue = get_guild_queue(guild_id)
        queue.append(track)
        if not interaction.guild.voice_client.is_playing():
            await play_next(interaction.guild, interaction.channel)
        else:
            await interaction.followup.send(
                f'Added to queue: {track.title} - {track.artist().title}'
            )
    else:
        await interaction.followup.send('Track not found.')

# Queue command
@bot.tree.command(name="queue", description="Add a track to the queue")
@app_commands.describe(query="The song title to queue")
async def queue_track(interaction: discord.Interaction, query: str):
    await interaction.response.defer()
    tracks = plex.library.section('Music').searchTracks(title=query, maxresults=1)
    if tracks:
        track = tracks[0]
        guild_id = interaction.guild.id
        queue = get_guild_queue(guild_id)
        queue.append(track)
        await interaction.followup.send(
            f'Added to queue: {track.title} - {track.artist().title}'
        )
    else:
        await interaction.followup.send('Track not found.')

# Next command
@bot.tree.command(name="next", description="Skip to the next track")
async def next_track(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        interaction.guild.voice_client.stop()
        await interaction.response.send_message('Skipping to the next track.')
    else:
        await interaction.response.send_message('Nothing is playing.')

# Pause command
@bot.tree.command(name="pause", description="Pause the current track")
async def pause(interaction: discord.Interaction):
    if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
        interaction.guild.voice_client.pause()
        await interaction.response.send_message('Playback paused.')

        # Update bot's activity status to indicate paused state
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="Paused"))
    else:
        await interaction.response.send_message('Nothing is playing.')

# Resume command
@bot.tree.command(name="resume", description="Resume playback")
async def resume(interaction: discord.Interaction):
    if interaction.guild.voice_client and interaction.guild.voice_client.is_paused():
        interaction.guild.voice_client.resume()
        await interaction.response.send_message('Playback resumed.')

        # Restore bot's activity status to current track
        guild_id = interaction.guild.id
        queue = get_guild_queue(guild_id)
        if queue:
            # The currently playing track is the first in the queue
            track = queue[0]
            activity = discord.Activity(type=discord.ActivityType.listening, name=f"{track.artist().title} - {track.title}")
            await bot.change_presence(activity=activity)
        else:
            await bot.change_presence(activity=None)
    else:
        await interaction.response.send_message('Nothing is paused.')

# Stop command
@bot.tree.command(name="stop", description="Stop playback and clear the queue")
async def stop(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    if interaction.guild.voice_client:
        interaction.guild.voice_client.stop()
        get_guild_queue(guild_id).clear()
        await interaction.response.send_message('Playback stopped and queue cleared.')

        # Clear bot's activity status
        await bot.change_presence(activity=None)
    else:
        await interaction.response.send_message('Nothing is playing.')

# Add the shuffle command
@bot.tree.command(name="shuffle", description="Shuffle and play random tracks from your Plex library")
async def shuffle(interaction: discord.Interaction):
    await interaction.response.defer()

    if not interaction.guild.voice_client:
        if interaction.user.voice:
            channel = interaction.user.voice.channel
            await channel.connect()
        else:
            await interaction.followup.send("You are not connected to a voice channel.")
            return

    await interaction.followup.send('Shuffling your music library. This may take a moment...')

    try:
        # Fetch random tracks from the Plex Music Library
        music_section = plex.library.section('Music')
        max_tracks = 50  # Adjust this number as needed

        # Fetch random tracks using sort='random' and limit maxresults
        shuffled_tracks = music_section.searchTracks(sort='random', maxresults=max_tracks)

        if not shuffled_tracks:
            await interaction.followup.send('No tracks found in your music library.')
            return

        # Clear the current queue and add shuffled tracks
        guild_id = interaction.guild.id
        queue = get_guild_queue(guild_id)
        queue.clear()
        queue.extend(shuffled_tracks)

        await interaction.followup.send(f'Added {len(shuffled_tracks)} shuffled tracks to the queue.')

        # Start playback if not already playing
        if not interaction.guild.voice_client.is_playing():
            await play_next(interaction.guild, interaction.channel)
    except Exception as e:
        await interaction.followup.send('An error occurred while shuffling the tracks.')
        logging.error(f'Error in shuffle command: {e}')
        traceback.print_exc()
        
bot.run("YOUR_DISCORD_BOT_TOKEN")