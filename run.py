from app import create_app, db

import os

app = create_app()


# Ensures DB tables are created on first run
with app.app_context():
    db.create_all()

# Run the application
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
