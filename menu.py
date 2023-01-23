"""
Данный код не является полноценным плеером, а служит лишь для
иллюстрации возможности использования терминального меню.

Для работы с меню необходимо установить пакет: simple-term-menu.
Установка пакета: pip install simple-term-menu

Для работы данного кода требуется установка медиа-плеера mpv.
Установка в Linux Mint/Debian/Ubuntu: sudo apt install mpv

В ОС Windows библиотека использующаяся в скрипте не работает.

Меню не работает при запуске в IDE, по крайней мере в PyCharm. VSCode не тестировался.
Для корректной работы код необходимо запускать в терминале.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

from simple_term_menu import TerminalMenu

media = dict()
options = []


def open_playlist(path: str):
    """
    Функция для парсинга плейлиста.

    :param path: Путь к плейлисту.
    """
    key = ""
    num = 0
    try:
        with open(path, 'r', encoding='utf-8') as file:
            for item in file.readlines():
                if item.startswith("#EXTINF"):
                    key = item.split(',')[-1].replace('#EXTGRP:', '').strip()
                    continue
                elif item.startswith("http"):
                    num += 1
                    key = f'{num}. {key}'
                    media.update({key: item.strip()})
                    options.append(key)
    except UnicodeDecodeError:
        print("Не могу декодировать данные")
        sys.exit(0)


def dir_scan(path: str):
    """
    Функция для сканирования файлов в директории.

    :param path: Путь к директории.
    """
    # Добавьте нужные форматы. Подробнее о поддерживаемых mpv
    # форматах см. в документации: https://mpv.io/manual/master/
    suf = [".mp3", ".wav", ".mp4", ".avi"]
    files = [x for x in os.listdir(path) if Path(x).suffix in suf]

    for num, file in enumerate(files):
        name = f'{num+1}.{Path(file).name.split(Path(file).suffix)[0]}'
        media.update({name: str(Path(path) / file)})
        options.append(name)


def menu():
    """
    Функция создания меню.

    :return: Возвращает индекс выбранного пункта меню в списке.
    """
    return TerminalMenu(options).show()


def play(n: int):
    """
    Функция проигрывания плейлиста с указанной позиции.

    :param n: Индекс пункта меню в списке.
    """
    try:
        m = media[options[n]]
        print(f'\n{"-"*50}\n{options[n]}\n{"-"*50}\n')
        s = subprocess.check_call(f"mpv --volume=50 '{m}'", shell=True)
        print(s)
        if s == 0:
            n += 1
            print("\nДля выхода в плейлист нажмите 'Ctrl+C'\n")
            time.sleep(0.5)
            play(n)
    except subprocess.CalledProcessError:
        print("\nОШИБКА ОТКРЫТИЯ ССЫЛКИ\n")
        n += 1
        time.sleep(0.5)
        play(n)
    except IndexError:
        print("Конец плейлиста")
        time.sleep(0.5)
        menu_run()
    except KeyboardInterrupt:
        menu_run()


def menu_run():
    """
    Функция запуска проигрывания плейлиста.
    """
    try:
        subprocess.call("clear", shell=True)
        print(f"ПЛЕЙЛИСТ:\n(для возврата в 'Главное меню' нажмите 'Ctrl+C')\n{'-' * 25}")
        m = menu()
        play(m)
        menu_run()
    except (KeyboardInterrupt, TypeError):
        subprocess.call("clear", shell=True)
        options.clear()
        media.clear()
        main()


def main():
    """
    Главная функция. Выбор пользователя. Запуск сканирования директории
    или парсинга плейлиста. Запуск меню после сканирования.
    """
    try:
        print(f"\nГлавное меню\n{'-'*25}")
        opt = ["1. Ввести путь к плейлисту", "2. Открыть директорию", "3. Выход"]
        ch = TerminalMenu(opt).show()
        if opt[ch] == "1. Ввести путь к плейлисту":
            path = input("Путь к плейлисту >>> ")
            if not Path(path).exists() or not Path(path).is_file() or Path(path).suffix != ".m3u" or path == "":
                print("Неверная ссылка")
                main()
            open_playlist(path)
            menu_run()
        elif opt[ch] == "2. Открыть директорию":
            path = input("Путь к директории >>> ")
            if not Path(path).exists() or not Path(path).is_dir() or path == "":
                print("Неверная ссылка")
                main()
            dir_scan(path)
            menu_run()
        elif opt[ch] == "3. Выход":
            raise KeyboardInterrupt
    except (KeyboardInterrupt, TypeError):
        subprocess.call("clear", shell=True)
        print("\nGood By!\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
