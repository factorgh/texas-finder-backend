import threading
import subprocess

def run_script(script):
    subprocess.run(["python", script])

scripts = ["scripts/scrape_1.py", "scripts/scrape_2.py", "scripts/scrape_3.py", "scripts/scrape_4.py"]

threads = [threading.Thread(target=run_script, args=(script,)) for script in scripts]

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

subprocess.run(["python", "scripts/check_and_upload.py"])
