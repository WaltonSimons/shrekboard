from shrekboard import app, db
from utils import create_admin
import sys

if __name__ == '__main__':
    if '--init-db' in sys.argv:
        db.create_all()
        sys.exit()
    if len(sys.argv) > 1:
        if '--create-admin' == sys.argv[1]:
            password = sys.argv[2].encode('utf-8')
            create_admin(password)
            sys.exit()
    app.run(debug=True, host='0.0.0.0')
