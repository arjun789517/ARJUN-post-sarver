from flask import Flask, request, render_template_string, jsonify
import threading
import time
import requests
import datetime
import os
app = Flask(__name__)
HTML_PAGE = """
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>ARJUN POST PENAL</title>
    <link href='https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css' rel='stylesheet'>
    <link href='https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap' rel='stylesheet'>
    <link href='https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&display=swap' rel='stylesheet'>
    <style>
        :root {
            --main-bg-color: #0f0c29;
            --card-bg: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%);
            --neon-red: #ff003c;
            --neon-blue: #00d9ff;
            --neon-purple: #8a2be2;
            --text-glow: 0 0 10px currentColor, 0 0 20px currentColor, 0 0 30px currentColor;
        }
        body { 
            background: var(--main-bg-color);
            background: linear-gradient(to right, #24243e, var(--main-bg-color), #24243e);
            color: #fff; 
            min-height: 100vh;
            font-family: 'Rajdhani', sans-serif;
            overflow-x: hidden;
        }
        .container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }
        .glow {
            font-family: 'Orbitron', sans-serif;
            text-shadow: 0 0 10px var(--neon-red), 0 0 20px var(--neon-red), 0 0 30px var(--neon-red);
            color: #fff;
            letter-spacing: 2px;
            animation: pulsate 1.5s infinite alternate;
        }
        @keyframes pulsate {
            0% { text-shadow: 0 0 10px var(--neon-red), 0 0 20px var(--neon-red); }
            100% { text-shadow: 0 0 15px var(--neon-red), 0 0 30px var(--neon-red), 0 0 40px var(--neon-red); }
        }
        .card {
            background: var(--card-bg);
            border: none;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            transform-style: preserve-3d;
            transition: transform 0.5s, box-shadow 0.5s;
            margin-bottom: 2rem;
            overflow: hidden;
        }
        .card:hover {
            transform: translateY(-5px) rotateX(5deg);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.6);
        }
        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 5px;
            background: linear-gradient(to right, var(--neon-red), var(--neon-purple), var(--neon-blue));
            z-index: 1;
        }
        .card-body {
            padding: 2rem;
            position: relative;
        }
        .form-control { 
            background: rgba(0, 0, 0, 0.3);
            color: #fff; 
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 0.8rem 1rem;
            transition: all 0.3s;
        }
        .form-control:focus {
            background: rgba(0, 0, 0, 0.5);
            border-color: var(--neon-blue);
            box-shadow: 0 0 15px rgba(0, 217, 255, 0.3);
            color: #fff;
        }
        label {
            font-weight: 600;
            color: #e0e0e0;
            margin-bottom: 0.5rem;
            display: block;
        }
        .btn {
            border-radius: 8px;
            padding: 0.8rem 1.5rem;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
            transition: all 0.3s;
            position: relative;
            overflow: hidden;
            z-index: 1;
            border: none;
        }
        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 0%;
            height: 100%;
            background: rgba(255, 255, 255, 0.1);
            transition: all 0.3s;
            z-index: -1;
        }
        .btn:hover::before {
            width: 100%;
        }
        .btn-danger {
            background: linear-gradient(45deg, var(--neon-red), #ff0066);
            box-shadow: 0 5px 15px rgba(255, 0, 60, 0.4);
        }
        .btn-danger:hover {
            background: linear-gradient(45deg, #ff0066, var(--neon-red));
            box-shadow: 0 8px 25px rgba(255, 0, 60, 0.6);
            transform: translateY(-2px);
        }
        .btn-info {
            background: linear-gradient(45deg, var(--neon-blue), #0099ff);
            box-shadow: 0 5px 15px rgba(0, 217, 255, 0.4);
        }
        .btn-warning {
            background: linear-gradient(45deg, #ff9900, #ff6600);
            box-shadow: 0 5px 15px rgba(255, 153, 0, 0.4);
        }
        .btn-success {
            background: linear-gradient(45deg, #00cc66, #00cc99);
            box-shadow: 0 5px 15px rgba(0, 204, 102, 0.4);
        }
        #logBox { 
            max-height: 300px; 
            overflow-y: scroll; 
            background: rgba(0, 0, 0, 0.3); 
            padding: 15px; 
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            font-family: monospace;
            font-size: 0.9rem;
        }
        #logBox::-webkit-scrollbar {
            width: 5px;
        }
        #logBox::-webkit-scrollbar-thumb {
            background: var(--neon-red);
            border-radius: 10px;
        }
        .log-entry {
            padding: 5px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            animation: fadeIn 0.5s;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(5px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .subtitle {
            color: var(--neon-blue);
            text-shadow: 0 0 10px rgba(0, 217, 255, 0.5);
            font-weight: 700;
            margin-bottom: 1.5rem;
            letter-spacing: 1px;
        }
        .file-input-wrapper {
            position: relative;
            overflow: hidden;
            margin-bottom: 1rem;
        }
        .file-input-wrapper input[type=file] {
            position: absolute;
            left: 0;
            top: 0;
            opacity: 0;
            width: 100%;
            height: 100%;
            cursor: pointer;
        }
        .file-input-label {
            background: rgba(0, 0, 0, 0.3);
            color: #fff;
            padding: 0.8rem 1rem;
            border-radius: 8px;
            border: 1px dashed rgba(255, 255, 255, 0.2);
            text-align: center;
            transition: all 0.3s;
        }
        .file-input-wrapper:hover .file-input-label {
            border-color: var(--neon-blue);
            background: rgba(0, 0, 0, 0.5);
        }
        .pulse {
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(255, 0, 60, 0.7); }
            70% { box-shadow: 0 0 0 10px rgba(255, 0, 60, 0); }
            100% { box-shadow: 0 0 0 0 rgba(255, 0, 60, 0); }
        }
        .floating {
            animation: floating 3s ease-in-out infinite;
        }
        @keyframes floating {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
            100% { transform: translateY(0px); }
        }
        .particles {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
        }
        .particle {
            position: absolute;
            background: rgba(255, 0, 60, 0.5);
            border-radius: 50%;
            opacity: 0;
            animation: particleAnimation 10s infinite linear;
        }
        @keyframes particleAnimation {
            0% { 
                transform: translateY(0) translateX(0) scale(0); 
                opacity: 0;
            }
            10% {
                opacity: 1;
            }
            100% { 
                transform: translateY(-100vh) translateX(100vw) scale(1); 
                opacity: 0;
            }
        }
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }
        .status-active {
            background: var(--neon-red);
            box-shadow: 0 0 10px var(--neon-red);
        }
        .status-inactive {
            background: #666;
        }
        .tooltip-x {
            position: relative;
            display: inline-block;
        }
        .tooltip-x .tooltiptext {
            visibility: hidden;
            width: 120px;
            background-color: rgba(0, 0, 0, 0.8);
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 5px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -60px;
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 0.8rem;
        }
        .tooltip-x:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }
    </style>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Create animated particles
            createParticles();
            
            // Update logs every 2 seconds
            setInterval(updateLogs, 2000);
            
            // Add animation to buttons on hover
            const buttons = document.querySelectorAll('.btn');
            buttons.forEach(btn => {
                btn.addEventListener('mouseenter', function() {
                    this.classList.add('floating');
                });
                
                btn.addEventListener('mouseleave', function() {
                    this.classList.remove('floating');
                });
            });
        });
        
        function createParticles() {
            const particlesContainer = document.createElement('div');
            particlesContainer.className = 'particles';
            document.body.appendChild(particlesContainer);
            
            for (let i = 0; i < 30; i++) {
                const particle = document.createElement('div');
                particle.className = 'particle';
                
                const size = Math.random() * 5 + 2;
                const posX = Math.random() * 100;
                const delay = Math.random() * 10;
                
                particle.style.width = `${size}px`;
                particle.style.height = `${size}px`;
                particle.style.left = `${posX}vw`;
                particle.style.bottom = '0';
                particle.style.animationDelay = `${delay}s`;
                
                particlesContainer.appendChild(particle);
            }
        }
        
        function updateLogs() {
            fetch('/log')
                .then(res => res.json())
                .then(data => {
                    const logBox = document.getElementById('logBox');
                    logBox.innerHTML = data.map(entry => {
                        let className = 'log-entry';
                        if (entry.includes('[✅]')) className += ' text-success';
                        else if (entry.includes('[❌]') || entry.includes('[🛑]')) className += ' text-danger';
                        else if (entry.includes('[⚠️]')) className += ' text-warning';
                        else if (entry.includes('[⚙️]') || entry.includes('[🔍]')) className += ' text-info';
                        return `<div class="${className}">${entry}</div>`;
                    }).join("");
                    logBox.scrollTop = logBox.scrollHeight;
                });
        }
        
        function updateDelay() {
            const newDelay = document.getElementById('newDelay').value;
            if (!newDelay || newDelay < 5) {
                alert('Please enter a valid delay (minimum 5 seconds)');
                return;
            }
            
            fetch('/update_delay', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ delay: newDelay })
            }).then(() => {
                const indicator = document.getElementById('delayIndicator');
                indicator.classList.add('pulse');
                setTimeout(() => indicator.classList.remove('pulse'), 2000);
            });
        }
        
        function stopPosting() {
            if (confirm('Are you sure you want to stop posting?')) {
                fetch('/stop', { method: 'POST' });
            }
        }
        
        function updateStatusIndicator() {
            fetch('/status')
                .then(res => res.json())
                .then(data => {
                    const indicator = document.getElementById('statusIndicator');
                    const statusText = document.getElementById('statusText');
                    if (data.active) {
                        indicator.className = 'status-indicator status-active';
                        statusText.textContent = 'Active';
                        indicator.title = 'Posting active';
                    } else {
                        indicator.className = 'status-indicator status-inactive';
                        statusText.textContent = 'Inactive';
                        indicator.title = 'Not posting';
                    }
                });
        }
    </script>
</head>
<body>
<div class='particles'></div>
<div class='container py-5'>
    <div class='text-center mb-5 floating'>
        <h1 class='glow mb-2'>ARJUN POST SARVER</h1>
        <h4 class='text-light'>ARJUN WEB <span class='text-danger'>@ᴍᴀᴅᴇ ʙʏ ᴍᴀᴊɴᴜ xᴇ ʀᴀʜᴀᴛ ʙᴀʙᴀ</span></h4>
        <div class='mt-3'>
            <span class='status-indicator status-inactive' id='statusIndicator'></span>
            <small>Status: <span id='statusText'>Inactive</span></small>
        </div>
    </div>
    <div class='row'>
        <div class='col-lg-8 mx-auto'>
            <div class='card'>
                <div class='card-body'>
                    <h4 class='subtitle text-center'><i class='fas fa-rocket'></i> POSTING CONFIGURATION</h4>
                    <form method='post' enctype='multipart/form-data'>
                        <div class='form-group'>
                            <label>Post ID:</label>
                            <input type='text' name='threadId' class='form-control' required placeholder='Enter Facebook Post ID'>
                        </div>
                        <div class='form-group'>
                            <label>Hater Name:</label>
                            <input type='text' name='kidx' class='form-control' required placeholder='Enter username for comments'>
                        </div>
                        <div class='form-group'>
                            <label>Messages File (TXT):</label>
                            <div class='file-input-wrapper'>
                                <div class='file-input-label'>
                                    <i class='fas fa-file-alt mr-2'></i>
                                    <span class='file-name'>Choose messages file</span>
                                </div>
                                <input type='file' name='messagesFile' accept='.txt' required onchange="updateFileName(this, '.file-name')">
                            </div>
                        </div>
                        <div class='form-group'>
                            <label>Tokens File (TXT):</label>
                            <div class='file-input-wrapper'>
                                <div class='file-input-label'>
                                    <i class='fas fa-key mr-2'></i>
                                    <span class='file-name'>Choose tokens file</span>
                                </div>
                                <input type='file' name='txtFile' accept='.txt' required onchange="updateFileName(this, '.file-name')">
                            </div>
                        </div>
                        <div class='form-group'>
                            <label>Speed (seconds):</label>
                            <input type='number' name='time' class='form-control' min='5' value='20' required id='delayInput'>
                            <small class='form-text text-muted'>Minimum 5 seconds between requests</small>
                        </div>
                        <button type='submit' class='btn btn-danger btn-block pulse'>
                            <i class='fas fa-play-circle mr-2'></i> Start Posting
                        </button>
                    </form>
                </div>
            </div>
            <div class='card'>
                <div class='card-body'>
                    <h4 class='subtitle'><i class='fas fa-terminal mr-2'></i> LIVE LOGS</h4>
                    <div id='logBox' class='mb-3'>Waiting for logs...</div>
                    
                    <div class='row'>
                        <div class='col-md-6'>
                            <label>Change Delay (seconds):</label>
                            <input type='number' id='newDelay' class='form-control' placeholder='Enter new delay' min='5'>
                        </div>
                        <div class='col-md-6 d-flex align-items-end'>
                            <button onclick='updateDelay()' class='btn btn-info btn-block'>
                                <i class='fas fa-cog mr-2'></i> Update Delay
                            </button>
                        </div>
                    </div>
                    
                    <div class='mt-3'>
                        <button onclick='stopPosting()' class='btn btn-warning btn-block'>
                            <i class='fas fa-stop-circle mr-2'></i> Stop Posting
                        </button>
                    </div>
                </div>
            </div>
            <div class='card'>
                <div class='card-body'>
                    <h4 class='subtitle'><i class='fas fa-check-circle mr-2'></i> TOKEN HEALTH CHECK</h4>
                    <form method='post' action='/check_tokens' enctype='multipart/form-data'>
                        <div class='file-input-wrapper'>
                            <div class='file-input-label'>
                                <i class='fas fa-file-code mr-2'></i>
                                <span class='file-name'>Choose tokens file to check</span>
                            </div>
                            <input type='file' name='txtFile' accept='.txt' required onchange="updateFileName(this, '.file-name')">
                        </div>
                        <button type='submit' class='btn btn-success btn-block'>
                            <i class='fas fa-heartbeat mr-2'></i> Check Token Health
                        </button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
<script>
    function updateFileName(input, selector) {
        const fileName = input.files[0]?.name || 'Choose file';
        document.querySelector(selector).textContent = fileName;
    }
    
    // Check status every 5 seconds
    setInterval(updateStatusIndicator, 5000);
    updateStatusIndicator();
</script>
<script src="https://kit.fontawesome.com/a076d05399.js" crossorigin="anonymous"></script>
</body>
</html>
"""
log_output = []
runtime_delay = {"value": 20}
stop_event = threading.Event()
is_posting = False
def post_comments(thread_id, hater_name, tokens, messages):
    global is_posting
    is_posting = True
    log_output.append(f"[⏱️] Started at {datetime.datetime.now().strftime('%H:%M:%S')}")
    i = 0
    while not stop_event.is
