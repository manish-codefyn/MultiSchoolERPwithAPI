import sys
import subprocess

def check_package(name):
    try:
        __import__(name)
        print(f"{name} is available")
        return True
    except ImportError:
        print(f"{name} is NOT available")
        return False

gtts_ok = check_package("gtts")
pyttsx3_ok = check_package("pyttsx3")
