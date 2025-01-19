# Local Leak Finder

A Telegram bot that interacts with a local PostgreSQL database to store and search for leaked data. The bot allows users to search data via commands and uses efficient mechanisms to handle large datasets.

## Features
- Store large datasets in PostgreSQL.
- Search leaks through a Telegram bot interface.
- Real-time interaction with PostgreSQL.
- Clean and import large datasets efficiently.
- Simple, secure, and scalable.

## Requirements
- Python 3.8+
- PostgreSQL 14+
- A Telegram bot token from [BotFather](https://core.telegram.org/bots#botfather).
- An active PostgreSQL database connection.

## Installation

1. Clone the repository:
```bash
   git clone https://github.com/onurcangnc/local_leak_finder.git
   cd local_leak_finder
```

2. Set up a virtual environment:

```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    venv\Scripts\activate     # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up PostgreSQL:

- Create the database and tables:

```bash
CREATE TABLE leaks (
  id SERIAL PRIMARY KEY,
  data TEXT NOT NULL
);

CREATE TABLE bot_users (
  chat_id BIGINT PRIMARY KEY,
  is_authorized BOOLEAN NOT NULL DEFAULT FALSE
);
```

- Update the connection details in your Python scripts (host, user, password, port).

5. Add your Telegram bot token:

- Replace YOUR_TELEGRAM_BOT_TOKEN in the bot.py script with your actual bot token from BotFather.

## Usage

### Clean and Import Data

Use the `add_leak_csv.py` script to clean and import large datasets efficiently:

```bash
python add_leak.py
```

### Run the Telegram Bot

Start the bot to interact with the database:

```bash
python bot.py
```

### Commands

- **/start**: Start the bot.
- **/help**: Get help information.
- **/search <keyword>**: Search for a specific keyword in the leaks database.
- **/authorize**: Allow the bot to register your chat ID as an authorized user.

## Contributions

Feel free to fork the repository and contribute by submitting a pull request. Contributions are welcome !

## License

This project is licensed under the MIT License. See the LICENSE file for details.

For more details, visit the project repository: [Local Leak Finder](https://github.com/onurcangnc/local_leak_finder).


### Customization Notes:

- Add additional commands or features as your bot evolves.
- Update the repository URL if any changes are made. 
- Include the required environment variables or `.env` setup if used for configuration.
