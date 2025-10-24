#!/usr/bin/env python3
"""
OpenWebUI Database Inspector
This tool helps you understand the structure of your OpenWebUI database.
"""

import sqlite3
import json
import sys

def inspect_database(db_path):
    """Inspect the OpenWebUI database structure."""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("=" * 80)
        print("OpenWebUI Database Inspector")
        print("=" * 80)
        print()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"📊 Found {len(tables)} tables:")
        for table in tables:
            print(f"  - {table}")
        print()
        
        # Inspect the chat table
        if 'chat' in tables:
            print("=" * 80)
            print("Inspecting 'chat' table")
            print("=" * 80)
            print()
            
            # Get column info
            cursor.execute("PRAGMA table_info(chat)")
            columns = cursor.fetchall()
            
            print("Columns:")
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")
            print()
            
            # Get count
            cursor.execute("SELECT COUNT(*) as count FROM chat")
            count = cursor.fetchone()['count']
            print(f"Total chats: {count}")
            print()
            
            if count > 0:
                # Get a sample chat
                cursor.execute("SELECT * FROM chat LIMIT 1")
                sample = cursor.fetchone()
                
                print("=" * 80)
                print("Sample Chat Record")
                print("=" * 80)
                print()
                
                for key in sample.keys():
                    value = sample[key]
                    if key == 'chat' and value:
                        print(f"{key}:")
                        try:
                            chat_json = json.loads(value)
                            print(f"  Type: {type(chat_json).__name__}")
                            
                            if isinstance(chat_json, dict):
                                print(f"  Keys: {list(chat_json.keys())}")
                                print()
                                print("  Structure:")
                                for k, v in chat_json.items():
                                    if isinstance(v, list):
                                        print(f"    {k}: list with {len(v)} items")
                                        if len(v) > 0:
                                            print(f"      First item type: {type(v[0]).__name__}")
                                            if isinstance(v[0], dict):
                                                print(f"      First item keys: {list(v[0].keys())}")
                                    elif isinstance(v, dict):
                                        print(f"    {k}: dict with keys: {list(v.keys())}")
                                    else:
                                        print(f"    {k}: {type(v).__name__}")
                                
                                print()
                                print("  Full JSON structure (first 1000 chars):")
                                json_str = json.dumps(chat_json, indent=2)
                                print(json_str[:1000])
                                if len(json_str) > 1000:
                                    print("  ...")
                                    
                            elif isinstance(chat_json, list):
                                print(f"  List with {len(chat_json)} items")
                                if len(chat_json) > 0:
                                    print(f"  First item: {json.dumps(chat_json[0], indent=2)[:500]}")
                        except json.JSONDecodeError as e:
                            print(f"  ERROR: Failed to parse JSON: {e}")
                            print(f"  Raw value (first 200 chars): {str(value)[:200]}")
                    else:
                        # For other fields, just show the value (truncated)
                        value_str = str(value)
                        if len(value_str) > 100:
                            value_str = value_str[:100] + "..."
                        print(f"{key}: {value_str}")
                print()
                
                # Try to extract messages from the sample
                print("=" * 80)
                print("Attempting to Extract Messages")
                print("=" * 80)
                print()
                
                chat_data = sample['chat']
                if chat_data:
                    try:
                        chat_json = json.loads(chat_data)
                        messages = []
                        
                        # Try different possible locations for messages
                        if isinstance(chat_json, dict):
                            if 'messages' in chat_json:
                                messages = chat_json['messages']
                                print("✓ Found messages in 'messages' key")
                            elif 'history' in chat_json:
                                if isinstance(chat_json['history'], dict) and 'messages' in chat_json['history']:
                                    messages = chat_json['history']['messages']
                                    print("✓ Found messages in 'history.messages' key")
                                else:
                                    messages = chat_json['history']
                                    print("✓ Found messages in 'history' key")
                            else:
                                print("⚠ No 'messages' or 'history' key found")
                                print(f"  Available keys: {list(chat_json.keys())}")
                        elif isinstance(chat_json, list):
                            messages = chat_json
                            print("✓ Chat data is directly a list of messages")
                        
                        if messages:
                            print(f"\nFound {len(messages)} message(s)")
                            print("\nFirst message structure:")
                            if len(messages) > 0:
                                print(json.dumps(messages[0], indent=2))
                        else:
                            print("✗ Could not find messages in the expected locations")
                            
                    except Exception as e:
                        print(f"✗ Error extracting messages: {e}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 inspect_db.py <path_to_database.db>")
        sys.exit(1)
    
    db_path = sys.argv[1]
    inspect_database(db_path)
