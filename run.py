from app import create_app
from app.seed import seed_data

app = create_app()

@app.before_request
def _seed_once():
    with app.app_context():
        seed_data()

if __name__ == "__main__":
    app.run(debug=True)
