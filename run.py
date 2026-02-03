#!/usr/bin/env python3
"""
Jobezie Application Entry Point

Run the Flask development server:
    python run.py

Or with Flask CLI:
    flask run

For production, use gunicorn:
    gunicorn -w 4 -b 0.0.0.0:5000 "run:app"
"""

import os
from app import create_app

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    # Get configuration from environment
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))

    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     ██╗ ██████╗ ██████╗ ███████╗███████╗██╗███████╗          ║
║     ██║██╔═══██╗██╔══██╗██╔════╝╚══███╔╝██║██╔════╝          ║
║     ██║██║   ██║██████╔╝█████╗    ███╔╝ ██║█████╗            ║
║██   ██║██║   ██║██╔══██╗██╔══╝   ███╔╝  ██║██╔══╝            ║
║╚█████╔╝╚██████╔╝██████╔╝███████╗███████╗██║███████╗          ║
║ ╚════╝  ╚═════╝ ╚═════╝ ╚══════╝╚══════╝╚═╝╚══════╝          ║
║                                                               ║
║              Your AI Career Assistant                         ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

🚀 Starting Jobezie API Server...
   Mode: {'Development' if debug else 'Production'}
   URL:  http://{host}:{port}
   Health: http://{host}:{port}/health

Press CTRL+C to quit.
""")

    app.run(
        host=host,
        port=port,
        debug=debug
    )
