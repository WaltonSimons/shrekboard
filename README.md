# ShrekBoard
Flask-based Imageboard
## Current features
- Creating boards
- Posting and replying
- Image uploads
- Very basic admin panel (Allows to create new boards and ban IPs)
## How to run
1. Set database path, secret key and host in shrekboard.py
2. Initialize database:
```
python run.py --init-db
```
3. Create admin account:
```
python run.py --create-admin [YOUR_PASSWORD]
```
4. Start the server
```
python run.py
```
