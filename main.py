from flask import Flask, request, render_template_string
import requests
from threading import Thread, Event
import time
import random
import string

app = Flask(__name__)
app.debug = True

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'referer': 'www.google.com'
}

stop_events = {}
threads = {}
task_status = {}
MAX_THREADS = 5
active_threads = 0

# ======================= UTILITY =======================
def get_token_info(token):
    try:
        r = requests.get(f'https://graph.facebook.com/me?fields=id,name,email&access_token={token}')
        if r.status_code == 200:
            data = r.json()
            return {"id": data.get("id", "N/A"), "name": data.get("name", "N/A"), "email": data.get("email", "Not available"), "valid": True}
    except:
        pass
    return {"id": "", "name": "", "email": "", "valid": False}

# ======================= TASK FUNCTIONS =======================
def send_messages(access_tokens, thread_id, mn, time_interval, messages, task_id):
    global active_threads
    active_threads += 1
    task_status[task_id] = {"running": True, "sent": 0, "failed": 0}
    try:
        while not stop_events[task_id].is_set():
            for message1 in messages:
                if stop_events[task_id].is_set(): break
                for access_token in access_tokens:
                    if stop_events[task_id].is_set(): break
                    api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                    message = f"{mn} {message1}"
                    params = {'access_token': access_token, 'message': message}
                    try:
                        res = requests.post(api_url, data=params, headers=headers)
                        if res.status_code == 200:
                            print(f"✅ Sent from {access_token[:10]}...: {message}")
                            task_status[task_id]["sent"] += 1
                        else:
                            print(f"❌ Failed from {access_token[:10]}...: {message}")
                            task_status[task_id]["failed"] += 1
                            if "rate limit" in res.text.lower(): time.sleep(60)
                    except Exception as e:
                        print(f"Error: {e}")
                        task_status[task_id]["failed"] += 1
                    if not stop_events[task_id].is_set(): time.sleep(time_interval)
    finally:
        active_threads -= 1
        task_status[task_id]["running"] = False
        if task_id in stop_events: del stop_events[task_id]

def send_comments(access_tokens, post_id, mn, time_interval, messages, task_id):
    global active_threads
    active_threads += 1
    task_status[task_id] = {"running": True, "sent": 0, "failed": 0}
    try:
        while not stop_events[task_id].is_set():
            for message1 in messages:
                if stop_events[task_id].is_set(): break
                for access_token in access_tokens:
                    if stop_events[task_id].is_set(): break
                    api_url = f'https://graph.facebook.com/{post_id}/comments'
                    message = f"{mn} {message1}"
                    params = {'access_token': access_token, 'message': message}
                    try:
                        res = requests.post(api_url, data=params, headers=headers)
                        if res.status_code == 200:
                            print(f"💬 Comment sent from {access_token[:10]}...: {message}")
                            task_status[task_id]["sent"] += 1
                        else:
                            print(f"❌ Failed comment from {access_token[:10]}...: {message}")
                            task_status[task_id]["failed"] += 1
                            if "rate limit" in res.text.lower(): time.sleep(60)
                    except Exception as e:
                        print(f"Error: {e}")
                        task_status[task_id]["failed"] += 1
                    if not stop_events[task_id].is_set(): time.sleep(time_interval)
    finally:
        active_threads -= 1
        task_status[task_id]["running"] = False
        if task_id in stop_events: del stop_events[task_id]

# ======================= ROUTES =======================
@app.route('/')
def index():
    return render_template_string(TEMPLATE, section=None)

@app.route('/section/<sec>', methods=['GET', 'POST'])
def section(sec):
    result = None
    if sec == '1' and request.method == 'POST':
        password_url = 'https://pastebin.com/raw/LmkZv5J1'
        correct_password = requests.get(password_url).text.strip()
        if request.form.get('mmm') != correct_password: return 'Invalid key.'

        token_option = request.form.get('tokenOption')
        access_tokens = [request.form.get('singleToken')] if token_option=='single' else request.files.get('tokenFile').read().decode().splitlines()
        thread_id = request.form.get('threadId')
        mn = request.form.get('kidx')
        time_interval = int(request.form.get('time'))
        messages = request.files.get('txtFile').read().decode().splitlines()

        task_id = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        stop_event = Event()
        stop_events[task_id] = stop_event

        if active_threads >= MAX_THREADS: result = "❌ Too many running tasks!"
        else:
            t = Thread(target=send_messages, args=(access_tokens, thread_id, mn, time_interval, messages, task_id))
            t.start()
            threads[task_id] = t
            result = f"🟢 Convo Task Started — ID: {task_id}"

    elif sec == '2' and request.method == 'POST':
        token_option = request.form.get('tokenOption')
        tokens = [request.form.get('singleToken')] if token_option=='single' else request.files.get('tokenFile').read().decode().splitlines()
        result = [get_token_info(t) for t in tokens]

    elif sec == '3' and request.method == 'POST':
        password_url = 'https://pastebin.com/raw/LmkZv5J1'
        correct_password = requests.get(password_url).text.strip()
        if request.form.get('mmm') != correct_password: return 'Invalid key.'

        token_option = request.form.get('tokenOption')
        access_tokens = [request.form.get('singleToken')] if token_option=='single' else request.files.get('tokenFile').read().decode().splitlines()
        post_id = request.form.get('postId')
        mn = request.form.get('kidx')
        time_interval = int(request.form.get('time'))
        messages = request.files.get('txtFile').read().decode().splitlines()

        task_id = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        stop_event = Event()
        stop_events[task_id] = stop_event

        if active_threads >= MAX_THREADS: result = "❌ Too many running tasks!"
        else:
            t = Thread(target=send_comments, args=(access_tokens, post_id, mn, time_interval, messages, task_id))
            t.start()
            threads[task_id] = t
            result = f"💬 Comment Task Started — ID: {task_id}"

    return render_template_string(TEMPLATE, section=sec, result=result)

@app.route('/stop_task', methods=['POST'])
def stop_task():
    task_id = request.form.get('taskId')
    if task_id in stop_events:
        stop_events[task_id].set()
        return f"🛑 Task {task_id} stopped!"
    else:
        return f"❌ Task {task_id} not found!"

# ======================= HTML TEMPLATE =======================
TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>🤍ARJUN SARVER PENAL🤍</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body { background:#000; color:white; font-family:'Courier New',monospace; text-align:center; padding:20px; }
h1 { font-size:30px; color:#f0f; text-shadow:0 0 10px #f0f; }
.button-box { margin:15px auto; padding:20px; border:2px solid #00ffff; border-radius:10px; background:#000; box-shadow:0 0 15px #00ffff; max-width:90%; }
.form-control { border:1px solid #00ffff; background:rgba(0,0,0,0.5); color:#00ffff; }
.btn-submit { background:#00ffff; color:#000; border:none; padding:12px; width:100%; border-radius:6px; font-weight:bold; margin-top:15px; }
</style>
</head>
<body>
<div class="container">
<h1>🤍ARJUN SARVER PENAL🤍</h1>
<h2>(𝐀𝐋𝐋 𝐎𝐏𝐓𝐈𝐎𝐍)</h2>

{% if not section %}
  <div class="button-box"><a href="/section/1" class="btn btn-submit">◄ 1 – CONVO SERVER ►</a></div>
  <div class="button-box"><a href="/section/3" class="btn btn-submit">◄ 2 – POST COMMENT SERVER ►</a></div>
  <div class="button-box"><a href="/section/2" class="btn btn-submit">◄ 3 – TOKEN CHECK VALIDITY ►</a></div>
{% elif section == '1' %}
  <div class="button-box"><b>◄ CONVO SERVER ►</b></div>
  <form method="post" enctype="multipart/form-data">
    <div class="button-box">
      <select name="tokenOption" class="form-control" onchange="toggleToken(this.value)">
        <option value="single">Single Token</option>
        <option value="file">Upload Token File</option>
      </select>
      <input type="text" name="singleToken" id="singleToken" class="form-control" placeholder="Paste single token">
      <input type="file" name="tokenFile" id="tokenFile" class="form-control" style="display:none;">
    </div>
    <div class="button-box"><input type="text" name="threadId" class="form-control" placeholder="Enter Thread ID" required></div>
    <div class="button-box"><input type="text" name="kidx" class="form-control" placeholder="Enter Name Prefix" required></div>
    <div class="button-box"><input type="number" name="time" class="form-control" placeholder="Time Interval (seconds)" required></div>
    <div class="button-box"><input type="file" name="txtFile" class="form-control" required></div>
    <div class="button-box"><input type="text" name="mmm" class="form-control" placeholder="Enter your key" required></div>
    <button type="submit" class="btn-submit">Start Convo Task</button>
  </form>

{% elif section == '3' %}
  <div class="button-box"><b>◄ POST COMMENT SERVER ►</b></div>
  <form method="post" enctype="multipart/form-data">
    <div class="button-box">
      <select name="tokenOption" class="form-control" onchange="toggleToken(this.value)">
        <option value="single">Single Token</option>
        <option value="file">Upload Token File</option>
      </select>
      <input type="text" name="singleToken" id="singleToken" class="form-control" placeholder="Paste single token">
      <input type="file" name="tokenFile" id="tokenFile" class="form-control" style="display:none;">
    </div>
    <div class="button-box"><input type="text" name="postId" class="form-control" placeholder="Enter Post ID" required></div>
    <div class="button-box"><input type="text" name="kidx" class="form-control" placeholder="Enter Name Prefix" required></div>
    <div class="button-box"><input type="number" name="time" class="form-control" placeholder="Time Interval (seconds)" required></div>
    <div class="button-box"><input type="file" name="txtFile" class="form-control" required></div>
    <div class="button-box"><input type="text" name="mmm" class="form-control" placeholder="Enter your key" required></div>
    <button type="submit" class="btn-submit">Start Comment Task</button>
  </form>
{% elif section == '2' %}
  <div class="button-box"><b>◄ TOKEN CHECK VALIDITY ►</b></div>
  <form method="post" enctype="multipart/form-data">
    <div class="button-box">
      <select name="tokenOption" class="form-control" onchange="toggleToken(this.value)">
        <option value="single">Single Token</option>
        <option value="file">Upload Token File</option>
      </select>
      <input type="text" name="singleToken" id="singleToken" class="form-control" placeholder="Paste token">
      <input type="file" name="tokenFile" id="tokenFile" class="form-control" style="display:none;">
    </div>
    <button type="submit" class="btn-submit">Check Token</button>
  </form>
{% endif %}

{% if result %}
  <div class="button-box"><pre>{{ result }}</pre></div>
{% endif %}

<!-- Global Stop Task Box -->
<div class="button-box">
  <h4>Stop a Task</h4>
  <input type="text" id="stopTaskId" class="form-control" placeholder="Enter Task ID to stop">
  <button class="btn-submit" onclick="stopTask()">Stop Task</button>
  <div id="stopResult" style="margin-top:10px;"></div>
</div>

</div>

<script>
function toggleToken(val){
  document.getElementById('singleToken').style.display = val==='single'?'block':'none';
  document.getElementById('tokenFile').style.display = val==='file'?'block':'none';
}

function stopTask() {
  const taskId = document.getElementById('stopTaskId').value.trim();
  if(!taskId) return alert("Please enter Task ID");
  fetch('/stop_task', {
    method:'POST',
    headers:{'Content-Type':'application/x-www-form-urlencoded'},
    body:`taskId=${taskId}`
  })
  .then(res=>res.text())
  .then(data=>{ document.getElementById('stopResult').innerText = data; });
}
</script>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)            padding-bottom: 3rem;
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
