# Project description
The homework_bot project is designed to check the status of submitted 
homework on the Yandex server. Every 10 minutes, the bot sends a request
to the Telegram server. In case of a change in the status of the work,
the bot will send a message in the Telegram messenger.


# Tech
- Python 3.7
- Bot API
- Polling
- Dotenv
- Logging

# Running project

Create and activate virtual environment:

```
python -m venv env
```

```
source venv/bin/activate
```

```
python -m pip install --upgrade pip
```

Install dependencies requirements.txt:

```
pip install -r requirements.txt
```

Run project:

```
python homework.py
```


# Developer

[Bulankin Mihail](https://github.com/mvlbulankin)

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)
