from flask import Flask
import requests
from sqlite3 import connect

app = Flask(__name__)

def create_table():
    conn = connect('jokes.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jokes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            type TEXT,
            joke TEXT,
            setup TEXT,
            delivery TEXT,
            nsfw BOOLEAN,
            political BOOLEAN,
            sexist BOOLEAN,
            safe BOOLEAN,
            lang TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_joke(joke):
    conn = connect('jokes.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO jokes (
            category, type, joke, setup, delivery, nsfw, political, sexist, safe, lang
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        joke.get('category'),
        joke.get('type'),
        joke.get('joke') if joke.get('type') == 'single' else None,
        joke.get('setup') if joke.get('type') == 'twopart' else None,
        joke.get('delivery') if joke.get('type') == 'twopart' else None,
        joke.get('flags', {}).get('nsfw', False),
        joke.get('flags', {}).get('political', False),
        joke.get('flags', {}).get('sexist', False),
        joke.get('safe', True),
        joke.get('lang', 'en')
    ))
    conn.commit()
    conn.close()

JOKEAPI_URL = "https://v2.jokeapi.dev/joke/Any"

def fetch_jokes(amount=100):
    jokes = []
    for _ in range(amount):
        response = requests.get(JOKEAPI_URL)
        if response.status_code == 200:
            jokes.append(response.json())
    return jokes

@app.route('/fetch-and-store-jokes')
def fetch_and_store_jokes():
    try:
        create_table()
        jokes = fetch_jokes(amount=100)

        for joke in jokes:
            processed_joke = {
                "category": joke.get('category'),
                "type": joke.get('type'),
                "joke": joke.get('joke') if joke.get('type') == 'single' else None,
                "setup": joke.get('setup') if joke.get('type') == 'twopart' else None,
                "delivery": joke.get('delivery') if joke.get('type') == 'twopart' else None,
                "flags": {
                    "nsfw": joke.get('flags', {}).get('nsfw', False),
                    "political": joke.get('flags', {}).get('political', False),
                    "sexist": joke.get('flags', {}).get('sexist', False)
                },
                "safe": joke.get('safe', True),
                "lang": joke.get('lang', 'en')
            }
            insert_joke(processed_joke)

        return f"Successfully fetched and stored {len(jokes)} jokes."
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
