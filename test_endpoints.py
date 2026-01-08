#!/usr/bin/env python
import sys
import os
import threading
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from webapp import app

def run_server():
    app.run(debug=False, port=5000, use_reloader=False)

# Start server in background
thread = threading.Thread(target=run_server, daemon=True)
thread.start()

# Wait for server to start
time.sleep(2)

# Test using urllib instead of requests
import urllib.request
import urllib.error

endpoints = ['/', '/simulator', '/cohort', '/sensitivity', '/scenarios']
for ep in endpoints:
    try:
        response = urllib.request.urlopen(f'http://127.0.0.1:5000{ep}', timeout=3)
        status = '✓' if response.status == 200 else '✗'
        print(f'{status} {ep} ({response.status})')
    except urllib.error.HTTPError as e:
        print(f'✗ {ep} ({e.code})')
    except Exception as e:
        print(f'✗ {ep} (Error: {str(e)[:50]})')

print('\nTest complete')
time.sleep(1)
