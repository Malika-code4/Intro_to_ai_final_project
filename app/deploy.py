"""
Deploy helper for local/demo usage. This script does not publish anywhere
but provides commands and guidance to run or package the Streamlit app.
"""
import subprocess


def run_local():
    """Start the streamlit app locally."""
    cmd = ["streamlit", "run", "app/streamlit_app.py"]
    subprocess.run(cmd)


def print_instructions():
    print("To run locally:\n  pip install -r requirements.txt\n  streamlit run app/streamlit_app.py")


if __name__ == '__main__':
    print_instructions()
