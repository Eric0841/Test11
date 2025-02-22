import discord
from discord.ext import commands, tasks
from discord import app_commands
import requests
from datetime import datetime
from typing import Optional
import json
import os
import asyncio

TOKEN = os.getenv('DISCORD_BOT_TOKEN')  # .env에서 Discord Bot Token 불러오기
ROBLOX_API_KEY = os.getenv('ROBLOX_API_KEY')  # .env에서 Roblox API Key 불러오기
WEB_API_URL = 'https://games.roblox.com/v1/games?universeIds=7173302102'  # Replace 'id' with your universeId
ROBLOX_API_URL = "https://users.roblox.com/v1/usernames/users"
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
    # change_channel_name.start()
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
            await interaction.response.send_message(embed=discord.Embed(title=f'현재 활성 유저', description=f'실시간 유저: {active_users}명\n총 방문자 수: {visits}회', color=discord.Color.green()))
            # channel = bot.get_channel(998154513192063016)
            # channel2 = bot.get_channel(998154513192063016)
            # if channel and channel2:
            #     await channel.edit(name=f'현재 접속자: {active_users}명')
            #     await channel2.edit(name=f'총 방문자: {visits}회')
        else:
            await interaction.response.send_message(embed=discord.Embed(title=f'에러?!', description=f'활성 유저 데이터를 가져오는 데 실패했습니다.', color=discord.Color.red()))
    except Exception as e:
        await interaction.response.send_message(f'오류 발생: {str(e)}')

def get_roblox_profile_picture(user_id):
    url = f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=420x420&format=Png&isCircular=false"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "data" in data and data["data"]:
            image_url = data["data"][0].get("imageUrl", "No image URL found")
            return image_url
        else:
            return "No profile image data found"
    else:
        return f"Error: {response.status_code}"


# @app_commands.check(is_admin)
# @bot.tree.command(name="게임킥", description="게임 내 특정 플레이어 강퇴")
# async def kick(interaction: discord.Interaction, user: str, reason: str = "No reason provided"):
#     await interaction.response.defer()

#     # Initial embed: Your request is being processed
#     embed = discord.Embed(description=f"Your request is being processed", color=discord.Color.yellow())
#     initial_message = await interaction.followup.send(embed=embed)

#     # 1️⃣ 유저 이름으로 ID 가져오기 (Roblox API)
#     data = {"usernames": [user], "excludeBannedUsers": False}
#     response = requests.post(ROBLOX_API_URL, json=data)
    
#     result = response.json()

#     if not result["data"]:
#         await initial_message.edit(f"❌ `{user}` 닉네임을 가진 사용자를 찾을 수 없습니다.")
#         return

#     user_id = result["data"][0]["id"]

#     url = 'https://users.roblox.com/v1/usernames/users'
#     headers = {
#         'accept': 'application/json',
#         'Content-Type': 'application/json',
#         'x-api-key': ROBLOX_API_KEY,
#     }

#     payload = {
#         'usernames': [user],
#         'excludeBannedUsers': False
#     }

#     theresponse = requests.post(url, json=payload, headers=headers)
#     data = theresponse.json()

#     if 'data' not in data or not data['data']:
#         await initial_message.edit(f'사용자 `{user}`을(를) 찾을 수 없습니다.')
#         return

#     theUserId = data['data'][0]['id']
#     user_profile_image = data['data'][0].get('avatarUrl', '')  # Get the user’s profile image URL

#     # 강퇴 요청 API 호출
#     headers = {
#         'x-api-key': ROBLOX_API_KEY,
#         'Content-Type': 'application/json'
#     }

#     payload = {
#         'gameJoinRestriction': {
#             'active': True,
#             'duration': None,  # Duration을 None으로 설정하여 영구적으로 강퇴될 수 있게
#             'excludeAltAccounts': False,
#             'inherited': True,
#             'privateReason': "게임 내 킥 됨",
#             'displayReason': "킥 됨"
#         }
#     }

#     try:
#         patch_response = requests.patch(f'{PATCH_API_URL}{theUserId}', json=payload, headers=headers)

#         if patch_response.status_code == 200:
#             # 강퇴가 성공적으로 처리된 경우
#             profile_url = f"https://www.roblox.com/users/{theUserId}/profile"
#             avatar_url = get_roblox_profile_picture(theUserId)

#             # 2️⃣ 강퇴 요청을 처리하는 기본 임베드
#             embed = discord.Embed(
#                 title="Confirm details",
#                 description=f"Target User: [{user}]({profile_url}) ({theUserId})\nUniverse: [대한재단](https://www.roblox.com/games/95455103629227/2025#ropro-quick-play) (95455103629227)\n\nAction: Kick from server\nReason: {reason}",
#                 color=discord.Color.yellow()
#             )
#             embed.set_thumbnail(url=avatar_url)

#             # 3️⃣ Confirm / Cancel 버튼 추가
#             class ConfirmView(discord.ui.View):
#                 def __init__(self):
#                     super().__init__()

#                 @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
#                 async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
#                     # 강퇴 요청이 제대로 되었을 경우의 성공 메시지
#                     success_embed = discord.Embed(description="Successfully sent request to kick the user.", color=discord.Color.green())
#                     await initial_message.edit(embed=success_embed, view=None)

#                 @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
#                 async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
#                     cancel_embed = discord.Embed(description="작업 취소됨.", color=discord.Color.red())
#                     await initial_message.edit(embed=cancel_embed, view=None)

#             # Update the initial message with the confirmation embed and buttons
#             await initial_message.edit(embed=embed, view=ConfirmView())
#         else:
#             await initial_message.edit(f"❌ 강퇴 요청 실패. 상태 코드: {patch_response.status_code}")

#     except Exception as e:
#         await initial_message.edit(f"오류 발생: {str(e)}")


import asyncio

@app_commands.check(is_admin)
@bot.tree.command(name="게임킥", description="게임 내 특정 플레이어 강퇴")
async def kick(interaction: discord.Interaction, user: str, reason: str = "No reason provided"):
    await interaction.response.defer()

    # Initial embed: Your request is being processed
    embed = discord.Embed(description=f"귀하의 요청이 처리 중입니다.", color=discord.Color.yellow())
    initial_message = await interaction.followup.send(embed=embed)

    # 1️⃣ 유저 이름으로 ID 가져오기 (Roblox API)
    data = {"usernames": [user], "excludeBannedUsers": False}
    response = requests.post(ROBLOX_API_URL, json=data)
    
    result = response.json()

    if not result["data"]:
        await initial_message.edit(embed=discord.Embed(title=f'에러?!', description=f'사용자 `{user}`을(를) 찾을 수 없습니다.', color=discord.Color.red()))
        return

    user_id = result["data"][0]["id"]

    url = 'https://users.roblox.com/v1/usernames/users'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'x-api-key': ROBLOX_API_KEY,
    }

    payload = {
        'usernames': [user],
        'excludeBannedUsers': False
    }

    theresponse = requests.post(url, json=payload, headers=headers)
    data = theresponse.json()

    if 'data' not in data or not data['data']:
        await initial_message.edit(embed=discord.Embed(title=f'에러?!', description=f'사용자 `{username}`을(를) 찾을 수 없습니다.', color=discord.Color.red()))
        return

    theUserId = data['data'][0]['id']
    user_profile_image = data['data'][0].get('avatarUrl', '')  # Get the user’s profile image URL

    # 강퇴 요청 API 호출
    headers = {
        'x-api-key': ROBLOX_API_KEY,
        'Content-Type': 'application/json'
    }

    payload = {
        'gameJoinRestriction': {
            'active': True,
            'duration': None,  # Duration을 None으로 설정하여 영구적으로 강퇴될 수 있게
            'excludeAltAccounts': False,
            'inherited': True,
            'privateReason': "게임 내 킥 됨",
            'displayReason': "킥 됨"
        }
    }

    try:
        # 2️⃣ 기본 임베드 설정
        profile_url = f"https://www.roblox.com/users/{theUserId}/profile"
        avatar_url = get_roblox_profile_picture(theUserId)
        embed = discord.Embed(
            title="사용자 정보",
            description=f"유저: [{user}]({profile_url}) ({theUserId})\n체험: [대한재단](https://www.roblox.com/games/95455103629227/2025#ropro-quick-play) (95455103629227)\n\행위: 서버에서 킥\n사유: {reason}",
            color=discord.Color.yellow()
        )
        embed.set_thumbnail(url=avatar_url)
    
        # 3️⃣ Confirm / Cancel 버튼 추가
        class ConfirmView(discord.ui.View):
            def __init__(self):
                super().__init__()
    
            @discord.ui.button(label="확인", style=discord.ButtonStyle.green)
            async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
                try:
                    # Confirm 버튼 클릭 시에만 강퇴 요청을 보내도록 함
                    patch_response = requests.patch(f'{PATCH_API_URL}{theUserId}', json=payload, headers=headers)
    
                    if patch_response.status_code == 200:
                        # 강퇴 요청이 성공적일 경우
                        success_embed = discord.Embed(description="사용자를 서버에서 킥 하는 요청을 성공적으로 보냈습니다.", color=discord.Color.green())
                        await initial_message.edit(embed=success_embed, view=None)
    
                        # 1초 후에 언밴 처리
                        await asyncio.sleep(1)
    
                        # Unban (재입장 허용) API 호출
                        unban_payload = {
                            'gameJoinRestriction': {
                                'active': False  # Unban 설정
                            }
                        }
                        unban_response = requests.patch(f'{PATCH_API_URL}{theUserId}', json=unban_payload, headers=headers)
    
                        # if unban_response.status_code == 200:
                        #     success_embed = discord.Embed(description=f"❗ User `{user}` has been unbanned.", color=discord.Color.green())
                        #     await initial_message.edit(embed=success_embed, view=None)
                        # else:
                        #     success_embed = discord.Embed(description=f"❌ Unban failed for user `{user}`. Status code: {unban_response.status_code}", color=discord.Color.green())
                        #     await initial_message.edit(embed=success_embed, view=None)
                    else:
                        error_embed = discord.Embed(description=f"❌ 킥 요청이 실패했습니다. 상태 코드: {patch_response.status_code}", color=discord.Color.red())
                        await initial_message.edit(embed=error_embed, view=None)
    
                except Exception as e:
                    await initial_message.edit(f"오류 발생: {str(e)}")
    
            @discord.ui.button(label="취소", style=discord.ButtonStyle.red)
            async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
                cancel_embed = discord.Embed(description="작업 취소됨.", color=discord.Color.red())
                await initial_message.edit(embed=cancel_embed, view=None)
    
        # Update the initial message with the confirmation embed and buttons
        await initial_message.edit(embed=embed, view=ConfirmView())
    
    except Exception as e:
        await initial_message.edit(f"오류 발생: {str(e)}")



# @app_commands.check(is_admin)
# @bot.tree.command(name="게임킥", description="게임 내 특정 플레이어 강퇴")
# async def kick(interaction: discord.Interaction, user: str, reason: str = "No reason provided"):
#     await interaction.response.defer()

#     # Initial embed: Your request is being processed
#     embed = discord.Embed(description=f"Your request is being processed", color=discord.Color.yellow())
#     initial_message = await interaction.followup.send(embed=embed)

#     # 1️⃣ 유저 이름으로 ID 가져오기 (Roblox API)
#     data = {"usernames": [user], "excludeBannedUsers": False}
#     response = requests.post(ROBLOX_API_URL, json=data)
    
#     result = response.json()

#     if not result["data"]:
#         await initial_message.edit(f"❌ `{user}` 닉네임을 가진 사용자를 찾을 수 없습니다.")
#         return

#     user_id = result["data"][0]["id"]


#     url = 'https://users.roblox.com/v1/usernames/users'
#     headers = {
#         'accept': 'application/json',
#         'Content-Type': 'application/json',
#         'x-api-key': ROBLOX_API_KEY,
#     }

#     payload = {
#         'usernames': [user],
#         'excludeBannedUsers': False
#     }

#     theresponse = requests.post(url, json=payload, headers=headers)
#     data = theresponse.json()

#     if 'data' not in data or not data['data']:
#         await initial_message.edit(f'사용자 `{user}`을(를) 찾을 수 없습니다.')
#         return

#     theUserId = data['data'][0]['id']
#     user_profile_image = data['data'][0].get('avatarUrl', '')  # Get the user’s profile image URL

#     # headers = {
#     #     'x-api-key': ROBLOX_API_KEY,
#     #     'Content-Type': 'application/json'
#     # }
#     headers = {
#         'x-api-key': ROBLOX_API_KEY,
#     }

#     payload = {
#         'gameJoinRestriction': {
#             'active': True,
#             'duration': duration,
#             'excludeAltAccounts': False,
#             'inherited': True,
#             'privateReason': "게임 내 킥 됨",
#             'displayReason': "게임에서 킥 당했습니다!"
#         }
#     }

#     if reason is None:
#         reason = "사유 없음"

#     try:
#         response = requests.patch(f'{PATCH_API_URL}{theUserId}', json=payload, headers=headers)
#         print(user_id)
#         profile_url = f"https://www.roblox.com/users/{user_id}/profile"
            
#         avatar_url = get_roblox_profile_picture(user_id)


#         # 2️⃣ 강퇴 요청을 처리하는 기본 임베드
#         embed = discord.Embed(title="Confirm details", description=f"Target User: [{user}]({profile_url}) ({user_id})\nUniverse: [대한재단](https://www.roblox.com/games/95455103629227/2025#ropro-quick-play) (95455103629227)\n\nAction: Kick from server\nReason: {reason}", color=discord.Color.yellow())
#         embed.set_thumbnail(url=avatar_url)
        
#             # 3️⃣ Confirm / Cancel 버튼 추가
#         class ConfirmView(discord.ui.View):
#             def __init__(self):
#                 super().__init__()

#             @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
#             async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
#                 # 강퇴 요청 API 호출
#                 headers = {"Content-Type": "application/json"}
#                 payload = {"userId": user, "action": "kick", "reason": reason}
#                 response = requests.patch(f'{PATCH_API_URL}{theUserId}', json=payload, headers=headers)

#                 if response.status_code == 200:
#                     success_embed = discord.Embed(description="Successfully sent request to servers to execute your request!", color=discord.Color.green())
#                     await initial_message.edit(embed=success_embed, view=None)
#                 else:
#                     print(response.status_code)
#                     # 실패 시 상태 코드 및 응답 내용 출력
#                     error_embed = discord.Embed(description=f"Failed to execute request. Status code: {response.status_code}\nResponse: {response.text}", color=discord.Color.red())
#                     await initial_message.edit(embed=error_embed, view=None)

#             @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
#             async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
#                 cancel_embed = discord.Embed(description="작업 취소됨.", color=discord.Color.red())
#                 await initial_message.edit(embed=cancel_embed, view=None)

#         await initial_message.edit(embed=embed, view=ConfirmView())


#     except Exception as e:
#         await initial_message.edit(f"오류 발생: {str(e)}")


# @app_commands.check(is_admin)
# @bot.tree.command(name='게임밴', description='게임 내에서 특정 플레이어를 차단합니다.')
# async def ingameban(interaction: discord.Interaction, username: str, reason: str = None):
#     duration = None

#     url = 'https://users.roblox.com/v1/usernames/users'
#     headers = {
#         'accept': 'application/json',
#         'Content-Type': 'application/json',
#     }

#     payload = {
#         'usernames': [username],
#         'excludeBannedUsers': False
#     }

#     theresponse = requests.post(url,json = payload,headers=headers)
#     data = theresponse.json()

#     theUserId = data['data'][0]['id']

#     headers = {
#         'x-api-key': ROBLOX_API_KEY,
#     }

#     payload = {
#         'gameJoinRestriction': {
#             'active': True,
#             'duration': duration,
#             'excludeAltAccounts': False,
#             'inherited': True,
#             'privateReason': "게임 내 차단됨",
#             'displayReason': "차단됨"
#         }
#     }

#     if reason is None:
#         reason = "사유 없음"

#     try:
#         response = requests.patch(f'{PATCH_API_URL}{theUserId}', json=payload, headers=headers)
#         if response.status_code == 200:
#             channel = bot.get_channel(998154513192063016)
#             await interaction.response.send_message(f'{username}님이 영구 차단되었습니다. 사유: {reason}')
#             await channel.send(f'{interaction.user.name}님이 {username}님을 차단했습니다. 사유: {reason}')
#         else:
#             await interaction.response.send_message(f'차단 실패. 상태 코드: {response.status_code}')
#     except Exception as e:
#         await interaction.response.send_message(f'오류 발생: {str(e)}')


@app_commands.check(is_admin)
@bot.tree.command(name='게임밴', description='게임 내에서 특정 플레이어를 차단합니다.')
async def ingameban(interaction: discord.Interaction, username: str, reason: str = None):
    await interaction.response.defer()

    # Initial embed: Your request is being processed
    embed = discord.Embed(description=f"귀하의 요청이 처리 중입니다.", color=discord.Color.yellow())
    initial_message = await interaction.followup.send(embed=embed)

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
        await initial_message.edit(embed=discord.Embed(title=f'에러?!', description=f'사용자 `{username}`을(를) 찾을 수 없습니다.', color=discord.Color.red()))
        return

    theUserId = data['data'][0]['id']
    user_profile_image = data['data'][0].get('avatarUrl', '')  # Get the user’s profile image URL

    # 2️⃣ 기본 임베드 설정
    profile_url = f"https://www.roblox.com/users/{theUserId}/profile"
    avatar_url = get_roblox_profile_picture(theUserId)
    embed = discord.Embed(
        title="사용자 정보",
        description=f"유저: [{username}]({profile_url}) ({theUserId})\n체험: [대한재단](https://www.roblox.com/games/95455103629227/2025#ropro-quick-play) (95455103629227)\n\n행위: 사용자를 서버에서 차단\n사유: {reason if reason else '사유 없음'}",
        color=discord.Color.red()
    )
    embed.set_thumbnail(url=avatar_url)

    class ConfirmView(discord.ui.View):
        def __init__(self):
            super().__init__()

        @discord.ui.button(label="확인", style=discord.ButtonStyle.green)
        async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
            try:
                headers = {
                    'x-api-key': ROBLOX_API_KEY,
                }

                duration = None  # You can adjust this if you want a timed ban

                payload = {
                    'gameJoinRestriction': {
                        'active': True,
                        'duration': duration,
                        'excludeAltAccounts': False,
                        'inherited': True,
                        'privateReason': "게임 내 차단됨",
                        'displayReason': reason if reason else "차단됨"
                    }
                }

                response = requests.patch(f'{PATCH_API_URL}{theUserId}', json=payload, headers=headers)

                if response.status_code == 200:
                    channel = bot.get_channel(998154513192063016)  # Adjust to your channel ID
                    await initial_message.edit(embed=discord.Embed(description=f'{username}님이 영구 차단되었습니다. 사유: {reason if reason else "사유 없음"}', color=discord.Color.green()), view=None)
                    await channel.send(f'{interaction.user.name}님이 {username}님을 차단했습니다. 사유: {reason if reason else "사유 없음"}')
                else:
                    await initial_message.edit(embed=discord.Embed(description=f'차단 실패. 상태 코드: {response.status_code}', color=discord.Color.red()), view=None)

            except Exception as e:
                await initial_message.edit(embed=discord.Embed(description=f'오류 발생: {str(e)}', color=discord.Color.red()), view=None)

        @discord.ui.button(label="취소", style=discord.ButtonStyle.red)
        async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
            cancel_embed = discord.Embed(description="작업 취소됨.", color=discord.Color.red())
            await initial_message.edit(embed=cancel_embed, view=None)

    # Update the initial message with the confirmation embed and buttons
    await initial_message.edit(embed=embed, view=ConfirmView())



@bot.event
async def on_application_command_error(interaction: discord.Interaction, error: Exception):
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message("이 명령어를 사용할 권한이 없습니다.")
    else:
        await interaction.response.send_message(f'오류 발생: {str(error)}')


# @app_commands.check(is_admin)
# @bot.tree.command(name='게임밴해제', description='게임 내에서 플레이어 차단 해제 (관리자만 실행 가능)')
# async def ingameunban(interaction: discord.Interaction, username: str, reason: str = None):
#     url = 'https://users.roblox.com/v1/usernames/users'
#     headers = {
#         'accept': 'application/json',
#         'Content-Type': 'application/json',
#     }

#     # 요청 데이터 정의
#     payload = {
#         'usernames': [username],
#         'excludeBannedUsers': False
#     }

#     theresponse = requests.post(url, json=payload, headers=headers)
#     data = theresponse.json()

#     theUserId = data['data'][0]['id']

#     headers = {
#         'x-api-key': ROBLOX_API_KEY,  # 필요 시 API 키 변경
#     }
#     payload = {
#         'gameJoinRestriction':
#             {
#                 'active': False
#             }
#     }

#     if reason is None:
#         reason = "사유 없음"

#     try:
#         response = requests.patch(f'{PATCH_API_URL}{theUserId}', json=payload, headers=headers)
#         if response.status_code == 200:
#             channel = bot.get_channel(998154513192063016)
#             await interaction.response.send_message(f'{username}님의 차단이 해제되었습니다. 관리 사유: {reason}')
#             await channel.send(f'{interaction.user.name}님이 {username}님의 차단을 해제했습니다. 관리 사유: {reason}')
#         else:
#             await interaction.response.send_message(f'플레이어 차단 해제 실패. 상태 코드: {response.status_code}')
#     except Exception as e:
#         await interaction.response.send_message(f'오류 발생: {str(e)}')


@app_commands.check(is_admin)
@bot.tree.command(name='게임밴해제', description='게임 내에서 플레이어 차단 해제')
async def ingameunban(interaction: discord.Interaction, username: str, reason: str = None):
    await interaction.response.defer()

    # Initial embed: Your request is being processed
    embed = discord.Embed(description=f"귀하의 요청이 처리 중입니다.", color=discord.Color.yellow())
    initial_message = await interaction.followup.send(embed=embed)
    
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
        await initial_message.edit(embed=discord.Embed(title=f'에러?!', description=f'사용자 `{username}`을(를) 찾을 수 없습니다.', color=discord.Color.red()))
        return

    theUserId = data['data'][0]['id']
    user_profile_image = data['data'][0].get('avatarUrl', '')  # Get the user’s profile image URL

    # 기본 임베드 설정
    profile_url = f"https://www.roblox.com/users/{theUserId}/profile"
    avatar_url = get_roblox_profile_picture(theUserId)
    embed = discord.Embed(
        title="사용자 정보",
        description=f"유저: [{username}]({profile_url}) ({theUserId})\n체험: [대한재단](https://www.roblox.com/games/95455103629227/2025#ropro-quick-play) (95455103629227)\n\n행위: 유저에게 부여된 밴을 해제\n사유: {reason if reason else '사유 없음'}",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=avatar_url)

    class ConfirmView(discord.ui.View):
        def __init__(self):
            super().__init__()

        @discord.ui.button(label="확인", style=discord.ButtonStyle.green)
        async def unban(self, interaction: discord.Interaction, button: discord.ui.Button):
            try:
                headers = {
                    'x-api-key': ROBLOX_API_KEY,
                }

                payload = {
                    'gameJoinRestriction': {
                        'active': False  # Lifting the ban
                    }
                }

                response = requests.patch(f'{PATCH_API_URL}{theUserId}', json=payload, headers=headers)

                if response.status_code == 200:
                    channel = bot.get_channel(998154513192063016)  # Adjust to your channel ID
                    await initial_message.edit(embed=discord.Embed(description=f'{username}님의 차단이 해제되었습니다. 사유: {reason if reason else "사유 없음"}', color=discord.Color.green()), view=None)
                    await channel.send(f'{interaction.user.name}님이 {username}님의 차단을 해제했습니다. 사유: {reason if reason else "사유 없음"}')
                else:
                    await initial_message.edit(f'차단 해제 실패. 상태 코드: {response.status_code}')

            except Exception as e:
                await initial_message.edit(f'오류 발생: {str(e)}')

        @discord.ui.button(label="취소", style=discord.ButtonStyle.red)
        async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
            cancel_embed = discord.Embed(description="작업 취소됨.", color=discord.Color.red())
            await initial_message.edit(embed=cancel_embed, view=None)

    # Update the initial message with the confirmation embed and buttons
    await initial_message.edit(embed=embed, view=ConfirmView())


async def ingameban_error(interaction: discord.Interaction, error):
    if isinstance(error, commands.MissingRole):
        await interaction.response.send_message("이 명령어를 사용할 권한이 없습니다.")

@bot.event
async def on_application_command_error(interaction: discord.Interaction, error: Exception):
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message("이 명령어를 사용할 권한이 없습니다.")
    else:
        await interaction.response.send_message(f'오류가 발생했습니다: {str(error)}')


# @tasks.loop(minutes=6)  # 6분마다 실행
# async def change_channel_name():
#     channel = bot.get_channel(998154513192063016)
#     channel2 = bot.get_channel(998154513192063016)
#     if channel and channel2:
#         try:
#             response = requests.get(WEB_API_URL)
#             if response.status_code == 200:
#                 data = response.json()
#                 active_users = data['data'][0].get('playing', '데이터 없음')
#                 visits = data['data'][0].get('visits', '데이터 없음')
#                 new_name = f"현재 접속자: {active_users}명"
#                 await channel.edit(name=new_name)
#                 await channel2.edit(name=f'총 방문자: {visits}회')
#             else:
#                 print('게임 데이터를 가져오는 데 실패했습니다.')
#         except Exception as e:
#             print(f'오류 발생: {str(e)}')
#     else:
#         print(f'채널을 찾을 수 없습니다.')


bot.run(TOKEN)
