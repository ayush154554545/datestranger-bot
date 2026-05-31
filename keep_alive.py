# -*- coding: utf-8 -*-
# ============================================================
#        KEEP ALIVE - Web Server for 24/7 Uptime
# ============================================================

from flask import Flask
from threading import Thread

app = Flask('')


@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Date Stranger Bot</title>
            <meta charset="UTF-8">
            <style>
                body {
                    background: linear-gradient(135deg, #1a1a2e, #16213e);
                    color: #fff;
                    font-family: Arial, sans-serif;
                    text-align: center;
                    padding: 50px;
                    margin: 0;
                    min-height: 100vh;
                }
                h1 {
                    color: #e94560;
                    font-size: 56px;
                    margin-bottom: 10px;
                }
                .status {
                    color: #00ff88;
                    font-weight: bold;
                    font-size: 24px;
                    margin: 20px 0;
                }
                .info {
                    background: rgba(255,255,255,0.1);
                    border-radius: 15px;
                    padding: 20px;
                    margin: 20px auto;
                    max-width: 400px;
                }
                a {
                    color: #00d9ff;
                    text-decoration: none;
                    font-weight: bold;
                }
                .pulse {
                    animation: pulse 2s infinite;
                    display: inline-block;
                }
                @keyframes pulse {
                    0% { opacity: 1; }
                    50% { opacity: 0.5; }
                    100% { opacity: 1; }
                }
            </style>
        </head>
        <body>
            <h1>💘 Date Stranger</h1>
            <p class="status">
                <span class="pulse">●</span> ONLINE
            </p>
            <div class="info">
                <p>Anonymous Chat Bot</p>
                <p>Running 24/7 ✅</p>
                <p>
                    Join: <a href="https://t.me/datestranger_chatbot">
                        @datestranger_chatbot
                    </a>
                </p>
            </div>
        </body>
    </html>
    """


@app.route('/health')
def health():
    return "OK", 200


@app.route('/ping')
def ping():
    return "pong", 200


def run():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    server = Thread(target=run)
    server.daemon = True
    server.start()
    print("✅ Keep-alive server started on port 8080")