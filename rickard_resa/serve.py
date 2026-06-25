#!/usr/bin/env python3
"""Starta Rickards reseapp lokalt. Kör: python serve.py"""
import http.server, webbrowser, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
PORT = 8080
print(f"Öppnar http://localhost:{PORT}/ — tryck Ctrl+C för att stänga.")
webbrowser.open(f"http://localhost:{PORT}/")
http.server.test(HandlerClass=http.server.SimpleHTTPRequestHandler, port=PORT, bind="localhost")
