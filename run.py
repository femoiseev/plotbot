from server import server
import os

server.run(host='0.0.0.0', port=os.environ.get('PORT', 8443))
