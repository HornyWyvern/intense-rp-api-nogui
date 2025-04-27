import threading, webbrowser, api, re, os, sys
import utils.config_manager as config_manager
import customtkinter as ctk
from gui import create_gui

import argparse

def run_cli():
    parser = argparse.ArgumentParser(description="Intense RP API CLI")
    parser.add_argument('--cli', action='store_true', help='Запуск только в консольном режиме (без GUI)')
    parser.add_argument('--headless', action='store_true', help='Запускать браузер в headless режиме')
    parser.add_argument('--browser', type=str, default='Chrome', help='Браузер (Chrome, Firefox, Edge, Safari)')
    parser.add_argument('--email', type=str, help='Email DeepSeek')
    parser.add_argument('--password', type=str, help='Пароль DeepSeek')
    parser.add_argument('--config', type=str, help='Путь к конфигу')
    parser.add_argument('--grid-host', type=str, help='Адрес Selenium Grid')
    parser.add_argument('--grid-port', type=str, help='Порт Selenium Grid')
    args = parser.parse_args()

    # Загружаем конфиг
    if args.config:
        import json
        with open(args.config, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        from gui import config as default_config
        config = default_config.copy()

    config['browser'] = args.browser
    config['headless'] = args.headless
    if args.grid_host or args.grid_port:
        config['selenium_grid'] = {
            'host': args.grid_host or '',
            'port': args.grid_port or ''
        }
    if args.email:
        config['models']['deepseek']['email'] = args.email
    if args.password:
        config['models']['deepseek']['password'] = args.password
    if args.email and args.password:
        config['models']['deepseek']['auto_login'] = True

    def print_log_console(text, *_):
        clean = re.sub(r'\[color:[^\]]+\]', '', text)
        print(clean)

    api.assign_config(config)
    if args.cli:
        api.assign_textbox(print_log_console)
    api.run_services()

if __name__ == "__main__":
    if '--cli' in sys.argv:
        run_cli()
    else:
        create_gui()