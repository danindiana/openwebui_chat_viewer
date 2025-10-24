# Customization Guide

## Common Customizations

### 1. Add Your Specific JSON Path

If your OpenWebUI database uses a different structure, add it to `app.py`:

```python
# In get_chat_messages function, around line 76:

# Add your custom path here
elif 'your_custom_key' in messages_data:
    messages = messages_data['your_custom_key']
elif 'conversations' in messages_data:
    messages = messages_data['conversations']
```

### 2. Add Markdown Rendering

Install markdown library:
```bash
pip install markdown2 --break-system-packages
```

Update `app.py`:
```python
import markdown2

# In get_chat_messages, before returning:
for msg in messages:
    if msg.get('role') == 'assistant' and 'content' in msg:
        msg['content_html'] = markdown2.markdown(msg['content'])
```

Update `templates/index.html`:
```javascript
// In createMessageElement function:
const content = message.content_html || escapeHtml(String(content));
messageDiv.innerHTML = `
    <div class="message-header">
        <span class="message-role ${role}">${escapeHtml(role)}</span>
    </div>
    <div class="message-content">${content}</div>  // Note: No escapeHtml here if using HTML
`;
```

### 3. Add Syntax Highlighting for Code

Add to `<head>` in `templates/index.html`:
```html
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
```

Add to JavaScript:
```javascript
// After appending message to container:
messagesContainer.querySelectorAll('pre code').forEach((block) => {
    hljs.highlightBlock(block);
});
```

### 4. Add Search Functionality

Add to `templates/index.html` sidebar:
```html
<div class="sidebar-header">
    <h1>💬 Chat History</h1>
    <input type="text" id="searchInput" placeholder="Search chats..." style="
        width: 100%;
        padding: 8px;
        margin-top: 10px;
        border: 1px solid #ccc;
        border-radius: 4px;
    ">
</div>
```

Add JavaScript:
```javascript
document.getElementById('searchInput').addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase();
    document.querySelectorAll('.chat-item').forEach(item => {
        const title = item.querySelector('.chat-title').textContent.toLowerCase();
        item.style.display = title.includes(query) ? 'block' : 'none';
    });
});
```

### 5. Add Export Functionality

Add export button to chat header in `templates/index.html`:
```html
<div class="chat-header" id="chatHeader">
    <h2 id="chatTitle">Select a chat to view</h2>
    <button onclick="exportChat()" style="
        padding: 8px 16px;
        background: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
    ">Export</button>
</div>
```

Add JavaScript function:
```javascript
function exportChat() {
    const title = document.getElementById('chatTitle').textContent;
    const messages = Array.from(document.querySelectorAll('.message')).map(msg => {
        const role = msg.querySelector('.message-role').textContent;
        const content = msg.querySelector('.message-content').textContent;
        return `${role}: ${content}`;
    }).join('\n\n');
    
    const blob = new Blob([`${title}\n${'='.repeat(50)}\n\n${messages}`], 
                          {type: 'text/plain'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${title.replace(/[^a-z0-9]/gi, '_')}.txt`;
    a.click();
}
```

### 6. Add Pagination

Update `app.py`:
```python
@app.route('/api/chats', methods=['GET'])
def get_chats():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    offset = (page - 1) * per_page
    
    # ... existing code ...
    
    cursor.execute('''
        SELECT id, title, created_at, updated_at 
        FROM chat 
        ORDER BY updated_at DESC
        LIMIT ? OFFSET ?
    ''', (per_page, offset))
    
    # Add total count
    cursor.execute('SELECT COUNT(*) as count FROM chat')
    total = cursor.fetchone()['count']
    
    return jsonify({
        'chats': chats,
        'page': page,
        'per_page': per_page,
        'total': total,
        'pages': (total + per_page - 1) // per_page
    })
```

### 7. Add Timestamps to Messages

Update `templates/index.html`:
```javascript
// In createMessageElement:
const timestamp = message.timestamp || message.created_at || message.date;
if (timestamp) {
    messageDiv.innerHTML = `
        <div class="message-header">
            <span class="message-role ${role}">${escapeHtml(role)}</span>
            <span class="message-time" style="
                font-size: 12px;
                color: #888;
                margin-left: 10px;
            ">${new Date(timestamp * 1000).toLocaleTimeString()}</span>
        </div>
        <div class="message-content">${escapeHtml(String(content))}</div>
    `;
}
```

### 8. Add Dark Mode Toggle

Add to `templates/index.html` CSS:
```css
body.dark-mode {
    background-color: #1a1a1a;
    color: #e0e0e0;
}

body.dark-mode .sidebar,
body.dark-mode .main-content {
    background-color: #2a2a2a;
}

body.dark-mode .message-content {
    background-color: #3a3a3a;
}
```

Add toggle button and JavaScript:
```html
<button onclick="toggleDarkMode()" style="position: fixed; top: 10px; right: 10px;">
    🌙
</button>

<script>
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
}

// Load preference
if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
}
</script>
```

### 9. Add Authentication (Basic)

Update `app.py`:
```python
from functools import wraps
from flask import session, redirect, url_for, request

app.secret_key = 'your-secret-key-here'  # Change this!

USERS = {
    'admin': 'password123'  # Use proper password hashing in production!
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in USERS and USERS[username] == password:
            session['user'] = username
            return redirect(url_for('index'))
    return '''
        <form method="post">
            <input name="username" placeholder="Username">
            <input name="password" type="password" placeholder="Password">
            <button type="submit">Login</button>
        </form>
    '''

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# Add @login_required to protected routes
@app.route('/')
@login_required
def index():
    return render_template('index.html')
```

### 10. Add Message Filtering

Add filter buttons to `templates/index.html`:
```html
<div style="padding: 10px; border-bottom: 1px solid #e0e0e0;">
    <button onclick="filterMessages('all')">All</button>
    <button onclick="filterMessages('user')">User</button>
    <button onclick="filterMessages('assistant')">Assistant</button>
</div>
```

Add JavaScript:
```javascript
function filterMessages(role) {
    document.querySelectorAll('.message').forEach(msg => {
        if (role === 'all' || msg.classList.contains(role)) {
            msg.style.display = 'flex';
        } else {
            msg.style.display = 'none';
        }
    });
}
```

## Database Schema Customization

If you need to support additional metadata:

```python
# In get_chats endpoint:
cursor.execute('''
    SELECT 
        id, 
        title, 
        created_at, 
        updated_at,
        user_id,
        model,
        tags
    FROM chat 
    ORDER BY updated_at DESC
''')
```

## Performance Optimizations

### 1. Add Caching

```bash
pip install flask-caching --break-system-packages
```

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/chats')
@cache.cached(timeout=60)  # Cache for 60 seconds
def get_chats():
    # ... existing code ...
```

### 2. Add Database Indexing

```python
# Run once to add index
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_updated ON chat(updated_at DESC)')
conn.commit()
conn.close()
```

## Testing Your Customizations

Always test after making changes:

```bash
# 1. Check Python syntax
python3 -m py_compile app.py

# 2. Restart server
./start.sh

# 3. Check browser console for JS errors

# 4. Test with different chats

# 5. Check terminal for Python errors
```

## Common Pitfalls

1. **Forgetting to escape HTML** - Always use `escapeHtml()` for user content
2. **Not handling missing fields** - Use `message.field || 'default'`
3. **Breaking JSON parsing** - Test with multiple chat formats
4. **Forgetting to restart server** - Flask needs restart after Python changes
5. **Cache issues** - Clear browser cache if changes don't appear

## Need More Help?

- Check browser console (F12) for errors
- Check terminal for Python errors
- Use `/api/debug/chat/<id>` endpoint
- Run `inspect_db.py` to verify structure
- Test with curl: `curl http://localhost:5000/api/chats`
