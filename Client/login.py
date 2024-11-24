from colorama import Fore
from utils.pretty import pretty_print
#placeholder
def login():
    pretty_print("╔═══════ RETURN TO YOUR QUEST ═══════╗", Fore.GREEN)
    while True:
        username = input("Brave adventurer, state your name: ").strip()
        
        if not username:
            pretty_print("A hero must have a name!", Fore.RED)
            continue
            
        password = input("Speak thy secret password: ").strip()
        
        if not password:
            pretty_print("The secret password cannot be empty!", Fore.RED)

        if len(username) >= 3 and len(password) >= 4:
            pretty_print(f"Welcome back, mighty {username}! Your legend continues...", Fore.GREEN)
            return username, password
        else:
            pretty_print("⚔️ Halt! A hero's name must be at least 3 characters and their password at least 4 characters strong!", Fore.RED)


def register():
    pretty_print("╔═══════ BEGIN YOUR EPIC JOURNEY ═══════╗", Fore.GREEN)
    while True:
        username = input("Declare your hero's name: ").strip()
        
        if not username:
            pretty_print("Every legend needs a name!", Fore.RED)
            continue
            
        password = input("Create your mystical password: ").strip()
        
        if not password:
            pretty_print("Your password must contain ancient power!", Fore.RED)

        if len(username) >= 3 and len(password) >= 4:
            pretty_print(f"The prophecy begins, {username}! Your tale shall be legendary!", Fore.GREEN)
            return username, password
        else:
            pretty_print("⚔️ Hold! A hero's name must be at least 3 characters and their password 4 characters of power!", Fore.RED)

def login_or_register():
    pretty_print("╔═══════ DESTINY AWAITS ═══════╗", Fore.GREEN)
    while True:
        choice = input("Do you wish to continue your quest or begin anew? [login/register]: ").strip().lower()
        
        if choice == "login":
            return login()
        elif choice == "register":
            return register()
        else:
            pretty_print("⚔️ Invalid path! Choose wisely: 'login' or 'register'", Fore.RED)