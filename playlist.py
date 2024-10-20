import re
import discord
from discord.ext import commands
from youtubesearchpython import Video
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

SPOTIPY_CLIENT_ID = 'a'
SPOTIPY_CLIENT_SECRET = 'b'
SPOTIPY_REDIRECT_URI = 'http://localhost:8080'
spotify_channel_id = 1296104795190329404
spotify_playlist_id = 'your playlist id'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope="user-modify-playback-state user-read-playback-state playlist-modify-public"))
def get_youtube_title(url):
    try:
        video_info = Video.getInfo(url)
        return video_info['title']
    except Exception as e:
        return None
class LinkHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.youtube_regex = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/')
        self.spotify_regex = re.compile(r'https?://open\.spotify\.com/')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id == spotify_channel_id:
            if self.youtube_regex.search(message.content):
                await self.handle_youtube_link(message)
            elif self.spotify_regex.search(message.content):
                await self.spotify(message)

    async def handle_youtube_link(self, message):
        title = get_youtube_title(message.content)
        if title==None:
            await message.channel.send('タイトルの取得に失敗しました。もう一度試してみてください。')
            return
        results = sp.search(q=title, limit=1)
        try:
            track = results['tracks']['items'][0]
            album_art_url = track['album']['images'][0]['url']
            track_info = {'name': track['name'], 'artist': track['artists'][0]['name'], 'album':track['album']['name'], 'url':  track['uri'], 'album_art': album_art_url}
        except:
            await message.channel.send('Spotifyで曲が見つかりませんでした。')

        embed = discord.Embed(title="この曲でいいですか？", description="曲が間違っていたらいいえを押してください。", color=0x002bff)
        embed.add_field(name="曲名", value=f"``{track_info['name']}``", inline=False)
        embed.add_field(name="アルバム", value=f"``{track_info['album']}``", inline=False)
        embed.add_field(name="アーティスト", value=f"``{track_info['artist']}``", inline=False)
        embed.set_thumbnail(url=album_art_url)
        view = YouTubeView(message, track_info)
        await message.channel.send(embed=embed, view=view)

    async def spotify(self, message):
        track_id = message.content.split("/")[-1].split("?")[0]
        uri = f"spotify:track:{track_id}"
        track = sp.track(track_id)
        track_info = {
            'name': track['name'],
            'album': track['album']['name'],
            'artist': track['artists'][0]['name'],
            'album_art': track['album']['images'][0]['url'] if track['album']['images'] else None
        }
        embed = discord.Embed(title="曲が追加されました :thumbsup:", color=0x34e718)
        embed.add_field(name="曲名", value=f"``{track_info['name']}``", inline=False)
        embed.add_field(name="アルバム", value=f"``{track_info['album']}``", inline=False)
        embed.add_field(name="アーティスト", value=f"``{track_info['artist']}``", inline=False)
        
        if track_info['album_art']:
            embed.set_thumbnail(url=track_info['album_art'])
        sp.playlist_add_items(spotify_playlist_id, [uri])
        await message.channel.send(embed=embed)

class YouTubeView(discord.ui.View):
    def __init__(self, message, track_info):
        super().__init__(timeout=60)
        self.message = message
        self.track_info = track_info

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.message.author.id

    @discord.ui.button(label="はい", style=discord.ButtonStyle.green)
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        sp.playlist_add_items(spotify_playlist_id, [self.track_info['url']])
        embed = discord.Embed(title="曲が追加されました :thumbsup:", color=0x34e718)
        embed.add_field(name="曲名", value=f"``{self.track_info['name']}``", inline=False)
        embed.add_field(name="アルバム", value=f"``{self.track_info['album']}``", inline=False)
        embed.add_field(name="アーティスト", value=f"``{self.track_info['artist']}``", inline=False)
        embed.set_thumbnail(url=self.track_info['album_art'])
        await interaction.response.edit_message(embed=embed, view=None)
        self.stop()

    @discord.ui.button(label="いいえ", style=discord.ButtonStyle.red)
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="おけ", embed=None, view=None)
        self.stop()

async def setup(bot):
    await bot.add_cog(LinkHandler(bot))