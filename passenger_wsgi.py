import sys
import os

# If you have a virtual environment:
# INTERP = os.path.expanduser("/path/to/your/venv/bin/python3")  # Adjust the path!
# if sys.executable != INTERP:
#     os.execl(INTERP, INTERP, *sys.argv)

# Add the project directory to the Python path
sys.path.append(os.getcwd()) # This is usually enough for Namecheap

from app import app as application # Your Flask app

# If you need to initialize something when Passenger starts:
# def application(environ, start_response):
#     # ... your initialization code here ...
#     return app(environ, start_response)