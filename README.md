# Python User Service

A **FastAPI** microservice for secure, scalable user management. Features include:
- JWT authentication & role-based access control (`user`, `admin`, `superadmin`)
- CRUD operations with paginated search and a search endpoint with multiple simultaneous filters support
- Rate limiting (`slowapi`)
- Real-time WebSocket subscriptions for user changes
- Containerized with Docker & Docker Compose

Role-based access control (`user`, `admin`, `superadmin`) with specific privileges for each role:


    - **user**: Can access the list API and get a user by ID.
    - **admin**: Can access all GET APIs, search API, update user roles (excluding deletion), and update their own information.
    - **superadmin**: Has full access to all operations.

---

## 🔧 Tech Stack

- **Framework**: FastAPI  
- **Database**: PostgreSQL  
- **Auth**: JWT (PyJWT) + custom RBAC  
- **Rate Limiting**: slowapi  
- **WebSockets**: FastAPI native support  
- **Logging**: Loguru  
- **Containerization**: Docker, Docker Compose  

---

## 🚀 Quick Start

### 1. Clone the Repo

```bash
git clone https://github.com/your-username/python-user-service.git
cd python-user-service
```


### 2. Prepare the environment

```
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Run the server 

a) Using Docker : 
```
docker-compose up --build
```

b) Locally (once postgres db is running ):
```
uvicorn app.main:app --reload
```

### 4. Import the users from .csv file to database usign python script import_users.py
In another terminal, 
```
python -m app.import_users
```

### 5. Explore the apis 
Go to : http://127.0.0.1:8000/docs#/

Get authenticated by clicking the "Authorize" button and entering the email and password of any user (default password - 'ChangeMe123!').
To test all APIs with different roles, change the role of one user to `superadmin` and one to `admin` directly in the database before logging in with those credentials.

### 6. Subscribe to changes 
Go to Hoppscotch Realtime:
`https://hoppscotch.io/realtime/websocket`

Connect to:
`ws://127.0.0.1:8000/api/v1/users/ws`

Send subscription JSON:
for subscribing to a particular user_id all actions, send : `` { "action": "subscribe_id",    "user_id": 1 } ``
for subscribing to new records created with a paricular type of email (for example ending with '@gmail.com') : `` { "action": "subscribe_search","email": "@gmail.com" } ``

