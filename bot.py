import discord
from discord.ext import commands, tasks
from discord import app_commands
import requests
from datetime import datetime
from typing import Optional
import json
import os


TOKEN = os.getenv('DISCORD_BOT_TOKEN')  # .env에서 Discord Bot Token 불러오기
ROBLOX_API_KEY = os.getenv('ROBLOX_API_KEY')  # .env에서 Roblox API Key 불러오기
WEB_API_URL = 'https://games.roblox.com/v1/games?universeIds=7173302102'  # Replace 'id' with your universeId
PATCH_API_URL = 'https://apis.roblox.com/cloud/v2/universes/7173302102/user-restrictions/'  # Replace 'id' with your universeId

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='pls ', intents=intents)

def is_admin(interaction: discord.Interaction) -> bool:
    roles = [role.name for role in interaction.user.roles]
    print(f"사용자: {interaction.user.name}, 역할: {roles}")
    return 'Admin' in roles or 'dev' in roles or 'Trial Mod' in roles

@bot.event
async def on_ready():
    print(f'봇 로그인 완료: {bot.user}')
    change_channel_name.start()
    try:
        synced = await bot.tree.sync()
        print(f'동기화된 명령어 개수: {len(synced)} 개')
    except Exception as e:
        print(f'명령어 동기화 실패: {e}')

@app_commands.check(is_admin)
@bot.tree.command(name='활성유저', description='현재 게임을 플레이 중인 유저 수를 확인합니다.')
async def activeusers(interaction: discord.Interaction):
    """로블록스 게임에서 활성 유저 수를 가져와 표시합니다."""
    try:
        response = requests.get(WEB_API_URL)
        if response.status_code == 200:
            data = response.json()
            active_users = data['data'][0].get('playing', '데이터 없음')
            visits = data['data'][0].get('visits', '데이터 없음')
            await interaction.response.send_message(f'현재 활성 유저: {active_users}명\n총 방문자 수: {visits}회')
            channel = bot.get_channel(998154513192063016)
            channel2 = bot.get_channel(998154513192063016)
            if channel and channel2:
                await channel.edit(name=f'현재 접속자: {active_users}명')
                await channel2.edit(name=f'총 방문자: {visits}회')
        else:
            await interaction.response.send_message('활성 유저 데이터를 가져오는 데 실패했습니다.')
    except Exception as e:
        await interaction.response.send_message(f'오류 발생: {str(e)}')

@app_commands.check(is_admin)
@bot.tree.command(name='강퇴', description='게임 내에서 특정 플레이어를 강퇴합니다.')
async def kick(interaction: discord.Interaction, username: str, reason: str = None):
    url = 'https://users.roblox.com/v1/usernames/users'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }

    payload = {
        'usernames': [username],
        'excludeBannedUsers': False
    }

    theresponse = requests.post(url, json=payload, headers=headers)
    data = theresponse.json()

    if 'data' not in data or not data['data']:
        await interaction.response.send_message(f'사용자 `{username}`을(를) 찾을 수 없습니다.')
        return

    theUserId = data['data'][0]['id']

    headers = {
        'x-api-key': ROBLOX_API_KEY,
    }

    payload = {
        'gameJoinRestriction': {
            'active': True,
            'duration': 1,  # ⏳ 1초 동안 강제 퇴장
            'excludeAltAccounts': False,
            'privateReason': "강퇴됨",
            'displayReason': reason or "강퇴됨"
        }
    }

    try:
        response = requests.patch(f'{PATCH_API_URL}{theUserId}', json=payload, headers=headers)
        if response.status_code == 200:
            channel = bot.get_channel(998154513192063016)
            await interaction.response.send_message(f'{username}님이 강퇴되었습니다. 사유: {reason or "사유 없음"}')
            await channel.send(f'{interaction.user.name}님이 {username}님을 강퇴했습니다. 사유: {reason or "사유 없음"}')
        else:
            await interaction.response.send_message(f'강퇴 실패. 상태 코드: {response.status_code}')
    except Exception as e:
        await interaction.response.send_message(f'오류 발생: {str(e)}')

@app_commands.check(is_admin)
@bot.tree.command(name='게임밴', description='게임 내에서 특정 플레이어를 차단합니다.')
async def ingameban(interaction: discord.Interaction, username: str, reason: str = None):
    duration = None

    url = 'https://users.roblox.com/v1/usernames/users'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }

    payload = {
        'usernames': [username],
        'excludeBannedUsers': False
    }

    theresponse = requests.post(url,json = payload,headers=headers)
    data = theresponse.json()

    theUserId = data['data'][0]['id']

    headers = {
        'x-api-key': ROBLOX_API_KEY,
    }

    payload = {
        'gameJoinRestriction': {
            'active': True,
            'duration': duration,
            'excludeAltAccounts': False,
            'inherited': True,
            'privateReason': "게임 내 차단됨",
            'displayReason': "차단됨"
        }
    }

    if reason is None:
        reason = "사유 없음"

    try:
        response = requests.patch(f'{PATCH_API_URL}{theUserId}', json=payload, headers=headers)
        if response.status_code == 200:
            channel = bot.get_channel(998154513192063016)
            await interaction.response.send_message(f'{username}님이 영구 차단되었습니다. 사유: {reason}')
            await channel.send(f'{interaction.user.name}님이 {username}님을 차단했습니다. 사유: {reason}')
        else:
            await interaction.response.send_message(f'차단 실패. 상태 코드: {response.status_code}')
    except Exception as e:
        await interaction.response.send_message(f'오류 발생: {str(e)}')

@bot.event
async def on_application_command_error(interaction: discord.Interaction, error: Exception):
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message("이 명령어를 사용할 권한이 없습니다.")
    else:
        await interaction.response.send_message(f'오류 발생: {str(error)}')


@app_commands.check(is_admin)
@bot.tree.command(name='게임밴해제', description='게임 내에서 플레이어 차단 해제 (관리자만 실행 가능)')
async def ingameunban(interaction: discord.Interaction, username: str, reason: str = None):
    url = 'https://users.roblox.com/v1/usernames/users'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }

    # 요청 데이터 정의
    payload = {
        'usernames': [username],
        'excludeBannedUsers': False
    }

    theresponse = requests.post(url, json=payload, headers=headers)
    data = theresponse.json()

    theUserId = data['data'][0]['id']

    headers = {
        'x-api-key': ROBLOX_API_KEY,  # 필요 시 API 키 변경
    }
    payload = {
        'gameJoinRestriction':
            {
                'active': False
            }
    }

    if reason is None:
        reason = "사유 없음"

    try:
        response = requests.patch(f'{PATCH_API_URL}{theUserId}', json=payload, headers=headers)
        if response.status_code == 200:
            channel = bot.get_channel(998154513192063016)
            await interaction.response.send_message(f'{username}님의 차단이 해제되었습니다. 관리 사유: {reason}')
            await channel.send(f'{interaction.user.name}님이 {username}님의 차단을 해제했습니다. 관리 사유: {reason}')
        else:
            await interaction.response.send_message(f'플레이어 차단 해제 실패. 상태 코드: {response.status_code}')
    except Exception as e:
        await interaction.response.send_message(f'오류 발생: {str(e)}')

async def ingameban_error(interaction: discord.Interaction, error):
    if isinstance(error, commands.MissingRole):
        await interaction.response.send_message("이 명령어를 사용할 권한이 없습니다.")

@bot.event
async def on_application_command_error(interaction: discord.Interaction, error: Exception):
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message("이 명령어를 사용할 권한이 없습니다.")
    else:
        await interaction.response.send_message(f'오류가 발생했습니다: {str(error)}')


@tasks.loop(minutes=6)  # 6분마다 실행
async def change_channel_name():
    channel = bot.get_channel(998154513192063016)
    channel2 = bot.get_channel(998154513192063016)
    if channel and channel2:
        try:
            response = requests.get(WEB_API_URL)
            if response.status_code == 200:
                data = response.json()
                active_users = data['data'][0].get('playing', '데이터 없음')
                visits = data['data'][0].get('visits', '데이터 없음')
                new_name = f"현재 접속자: {active_users}명"
                await channel.edit(name=new_name)
                await channel2.edit(name=f'총 방문자: {visits}회')
            else:
                print('게임 데이터를 가져오는 데 실패했습니다.')
        except Exception as e:
            print(f'오류 발생: {str(e)}')
    else:
        print(f'채널을 찾을 수 없습니다.')


bot.run(TOKEN)
