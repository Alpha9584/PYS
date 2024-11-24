from colorama import Fore
from utils.pretty import console_welcome, pretty_print
from login import login, register, login_or_register

def main():
    console_welcome()
    login_or_register()

if __name__ == "__main__":
    main()