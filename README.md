# 🛒 Auction App

A full-featured **online auction platform** built with **Flask + MongoEngine**, where users can register, log in, create auctions, and place bids in real-time.  
It demonstrates a layered architecture with clear separation of concerns (routers, services, repositories, models).

---

## ✨ Features
- 🔐 User authentication (JWT-based)
- 🏷️ Auction creation with image upload (Cloudinary integration)
- 💸 Real-time bidding system
- 📦 Persistent storage with MongoDB
- 🧪 Unit and integration tests (pytest)
- 📖 Swagger API documentation

---

## 🛠 Tech Stack
- **Backend**: Flask, Flask-JWT-Extended
- **Database**: MongoEngine (MongoDB)
- **Cloud Storage**: Cloudinary
- **Testing**: Pytest
- **Docs**: Swagger (OpenAPI), UML Diagrams

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/auction-app.git
cd auction-app
```

### 2. Setup Environment
```bash
python3 -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a ```.env``` file
```bash
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret
MONGODB_HOST=mongodb://localhost:27017/auctiondb
MONGODB_DATABASE=your_database_name
CLOUDINARY_CLOUD_NAME=xxx
CLOUDINARY_API_KEY=xxx
CLOUDINARY_API_SECRET=xxx
```
### 4. Run the Application
#### Option A: Flask(Local)
```bash
flask run
```
The app will be available at: http://127.0.0.1:5000

##### Option B: Docker (Recommended)
If you prefer Docker, you can run the app + MongoDB together:

```bash
docker-compose up --build
```
App available at: http://localhost:5000
MongoDB available at: mongodb://localhost:27017

#### To stop:
```bash 
docker-compose down
```

### 5. 🧪 Running Tests
```bash
pytest -v
```

### 6. 📖 API Documentation

Interactive Swagger docs available at:
👉 http://127.0.0.1:5000/apidocs

Alternatively, check the OpenAPI spec:
```bash
openapi.yaml
```

### 7. 📊 Architecture

The project follows a layered design:

- **Routers** → Flask Blueprints for endpoints

- **Services** → Business logic

- **Repositories** → Database operations

- **Models** → MongoEngine schemas

### 8. 📌 UML & Use Cases

- Use Case Diagram

- Class Diagram

- Sequence Diagram (Place Bid)

### 9. ☁️ Deployment on Render (Dockerized)

This project includes a Dockerfile and docker-compose.yml so it can run anywhere.

- Deploy on Render

- Push the repo to GitHub.

- Go to Render → New Web Service → connect your repo.

- Choose Dockerfile as the deploy method.

- Add environment variables under Settings → Environment (Render ignores .env).

- Deploy 🚀

Render will build and run your app inside a container the same way as Docker Compose locally.

### 10. 🤝 Contribution

Contributions, issues, and feature requests are welcome!
Feel free to fork and submit PRs.

### 11. 📜 License

This project is licensed under the MIT License.