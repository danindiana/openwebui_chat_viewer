# OpenWebUI Chat Viewer

A simple web-based viewer for OpenWebUI chat logs stored in SQLite database.

## Features

- Browse all chat sessions
- View complete message history for each chat
- Clean, responsive UI
- Handles various OpenWebUI database schema versions
- Debug endpoints for troubleshooting

## Setup Instructions

### 1. Prerequisites

- Python 3.7 or higher
- Your OpenWebUI database file (usually `webui.db`)

### 2. Install Dependencies

```bash
pip install flask --break-system-packages
```

### 3. Configure Database Path

Edit `app.py` and update the `DB_PATH` variable to point to your database file:

```python
DB_PATH = 'webui_backup_20250918_102142.db'  # Update this path
```

Or use a relative/absolute path:
```python
DB_PATH = '/path/to/your/webui.db'
```

### 4. Inspect Your Database (Optional but Recommended)

Before running the app, it's helpful to understand your database structure:

```bash
python3 inspect_db.py /path/to/your/webui.db
```

This will show you:
- All tables in the database
- Column structure of the chat table
- Sample chat data structure
- Message extraction attempt

### 5. Run the Application

```bash
python3 app.py
```

The server will start on `http://0.0.0.0:5000`

### 6. Access the Viewer

Open your browser and navigate to:
- Local: `http://localhost:5000`
- Network: `http://YOUR_IP:5000` (from other devices on your network)

## Troubleshooting

### Issue: No messages are displayed when clicking a chat

**Solution 1: Use the Debug Endpoint**

Visit: `http://localhost:5000/api/debug/chat/<chat_id>`

Replace `<chat_id>` with the ID of a chat (you can get this from the chat list).

This will show you:
- The raw database structure
- Parsed JSON structure
- Available keys in the chat data

**Solution 2: Check the Console**

Open your browser's developer console (F12) and look for:
- JavaScript errors
- The structure of the data being received
- Network request failures

**Solution 3: Check Server Logs**

The Flask server will print errors to the terminal. Look for:
- JSON parsing errors
- Database query errors
- Python exceptions

### Issue: Database file not found

Make sure:
1. The database file path in `app.py` is correct
2. The file has read permissions: `chmod 644 your_database.db`
3. You're running the app from the correct directory

### Issue: Empty chat list

This could mean:
1. The database file is empty or corrupted
2. The schema is different than expected
3. Check with: `python3 inspect_db.py your_database.db`

### Common OpenWebUI Schema Variations

The `chat` column can have different JSON structures:

**Structure 1: Direct messages array**
```json
{
  "messages": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there!"}
  ]
}
```

**Structure 2: Nested in history**
```json
{
  "history": {
    "messages": [...]
  }
}
```

**Structure 3: Top-level properties**
```json
{
  "id": "...",
  "messages": [...],
  "title": "..."
}
```

The application attempts to handle all these variations automatically.

## API Endpoints

### GET `/api/chats`
Returns list of all chats:
```json
[
  {
    "id": "chat_id",
    "title": "Chat title",
    "created_at": 1234567890,
    "updated_at": 1234567890
  }
]
```

### GET `/api/chats/<chat_id>`
Returns messages for a specific chat:
```json
{
  "title": "Chat title",
  "messages": [...],
  "raw_structure": ["messages", "title", ...]
}
```

### GET `/api/debug/chat/<chat_id>`
Returns complete raw database record with parsed JSON for debugging.

## Customization

### Changing the Port

Edit `app.py`:
```python
app.run(host='0.0.0.0', port=8080, debug=True)  # Change port here
```

### Styling

The CSS is embedded in `templates/index.html`. You can modify:
- Colors
- Fonts
- Layout dimensions
- Message styling

### Message Rendering

The `createMessageElement()` function in `index.html` handles message rendering. Modify this to:
- Add markdown support
- Format code blocks
- Add timestamps
- Change message appearance

## Security Notes

⚠️ **This application is designed for LOCAL NETWORK use only!**

- Do not expose to the public internet without authentication
- The debug endpoint reveals database contents
- Flask debug mode should be disabled in production
- Consider adding authentication if needed

## File Structure

```
.
├── app.py                    # Flask backend
├── templates/
│   └── index.html           # Frontend HTML/CSS/JS
├── inspect_db.py            # Database inspection tool
├── README.md                # This file
└── webui_backup_*.db        # Your database file
```

## Common Fixes

### If messages appear as JSON strings

The issue is in the message content parsing. Check the `createMessageElement()` function in `index.html`.

### If only some chats work

Different chats might have different JSON structures. The code attempts to handle variations, but you might need to add custom logic for your specific schema.

### Performance with large databases

For databases with thousands of chats or very long conversations:
1. Add pagination to the chat list
2. Implement message loading limits
3. Add search/filter functionality

## Support

For issues related to:
- OpenWebUI itself: https://github.com/open-webui/open-webui
- This viewer: Check the debug endpoints and inspect_db.py output

## License

This is a simple utility script provided as-is for personal use.
