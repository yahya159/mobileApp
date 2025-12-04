"""
Entry point for Streamlit web application
"""
import subprocess
import sys

if __name__ == '__main__':
    # Run streamlit with the web app
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        "src/web/app.py"
    ])
