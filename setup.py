# setup.py
import socket
import random
from cryptography.fernet import Fernet
import os

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def is_port_available(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

def generate_random_port():
    while True:
        port = random.randint(1024, 65535)
        if is_port_available(port):
            return port

def main():
    print("Made by BotanMethod/UntitledCatDev")
    print("=== Configuration Setup Wizard ===")
    
    
    # Определение IP
    local_ip = get_local_ip()
    use_default_ip = input(f"Found IP: {local_ip}. Do you want to use it? (y/n): ").lower() == 'y'
    host = local_ip if use_default_ip else input("Enter Your server IP: ")
    
    # Генерация порта
    random_port = generate_random_port()
    print(f"\nRandom free port generated: {random_port}")
    use_random_port = input("Do you want to use it? (y/n): ").lower() == 'y'
    port = random_port if use_random_port else int(input("Enter Your port (1024-65535): "))
    
    # Генерация ключа
    existing_key = None
    if os.path.exists("conf.py"):
        try:
            with open("conf.py", "r", encoding='utf-8') as f:  # Явно указываем кодировку
                for line in f:
                    if line.startswith("fernet_key"):
                        existing_key = line.split("=")[1].strip().strip("'")
        except UnicodeDecodeError:
            print("\nFile reading error conf.py ! The file may be corrupted or contain invalid characters.")
            existing_key = None
            if input("Do you want to delete old configuration file? (y/n): ").lower() == 'y':
                os.remove("conf.py")
            
    if existing_key:
        print(f"\nFound existing Fernet key: {existing_key}")
        use_existing_key = input("Do you want to use it? (y/n): ").lower() == 'y'
    
    if not existing_key or not use_existing_key:
        new_key = Fernet.generate_key().decode('utf-8')
        print(f"\nNew Fernet key generated: {new_key}")
        fernet_key = new_key
    else:
        fernet_key = existing_key
    
    # Подтверждение
    print("\n=== Final settings ===")
    print(f"Host IP: {host}")
    print(f"Port: {port}")
    print(f"Fernet key: {fernet_key}")
    
    confirm = input("\nDo you want to save settings? (y/n): ").lower() == 'y'
    if confirm:
        with open("conf.py", "w") as f:
            f.write(f"host = '{host}'\n")
            f.write(f"port = {port}\n")
            f.write(f"fernet_key = '{fernet_key}'\n")
        print("Configuration has successfully saved to conf.py!")
    else:
        print("Settings didn't save.")

if __name__ == "__main__":
    main()