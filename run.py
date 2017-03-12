from server import server
import os

if __name__ == '__main__':
    server.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))
