import subprocess
import os

# List of scripts to run in order
scripts = ['test.py', 'detail.py', 'save.py']

# Get the absolute path of the current directory
current_dir = os.path.abspath(os.path.dirname(__file__))
os.chdir(current_dir)

try:
    for script in scripts:
        print(f"Running {script}...")
        subprocess.run(['python', script], check=True)
        print(f"{script} completed successfully.")
    print("All scripts executed successfully.")
except subprocess.CalledProcessError as e:
    print(f"Error running {e.cmd[-1]}. Exit code: {e.returncode}")
    exit(1)