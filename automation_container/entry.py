import subprocess

SCRIPTS = [ "scripts/scrape_1.py" , "scripts/check_and_upload.py"]

def run_script(script):
    print(f"\n🚀 Running {script}...")
    result = subprocess.run(["python", script], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"⚠️ Error in {script}: {result.stderr}")

if __name__ == "__main__":
    print("🔄 Starting the scraping process...")
    
    for script in SCRIPTS:
        run_script(script)

    print("\n✅ All tasks completed successfully.")
