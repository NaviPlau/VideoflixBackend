# Videoflix Backend

This is the backend for **Videoflix**, a video streaming platform. The backend is built using **Django**, with **PostgreSQL**, **Redis**, **Celery**, and **FFmpeg** for handling video processing.

## Table of Contents
1. [Features](#features)
2. [Setup & Installation](#setup--installation)
   - [Prerequisites](#prerequisites)
   - [Step 1: Clone the Repository](#step-1-clone-the-repository)
   - [Step 2: Environment Variables](#step-2-environment-variables)
   - [Step 3: Create and Activate Virtual Environment](#step-3-create-and-activate-virtual-environment)
   - [Step 4: Install Dependencies](#step-4-install-dependencies)
   - [Step 5: Apply Migrations](#step-5-apply-migrations)
   - [Step 6: Create a Superuser](#step-6-create-a-superuser)
   - [Step 7: Run the Server](#step-7-run-the-server)
   - [Step 8: Start Celery & Redis](#step-8-start-celery--redis)
   - [Step 9: Create `celery.py` File](#step-9-create-celerypy-file)
3. [API Endpoints](#api-endpoints)
4. [URL Configuration](#url-configuration)
5. [License](#license)
6. [Contact](#contact)

## Features
- User authentication & management
- Video upload & HLS conversion (Only superusers can upload videos via the admin panel)
- Background tasks with Celery
- Caching with Redis
- API endpoints for frontend integration

## Setup & Installation

### Prerequisites
Make sure you have the following installed:
- Python 3.10+
- PostgreSQL
- Redis
- FFmpeg
- Virtual environment (optional but recommended)

### Step 1: Clone the Repository
```sh
git clone https://github.com/your-repo/videoflix-backend.git
cd videoflix-backend
```

### Step 2: Environment Variables
Rename the `.env-template` file to `.env`:
```sh
mv .env-template .env
```
Then, open `.env` and fill in the necessary fields with your own data (database credentials, secret keys, etc.).

### Step 3: Create and Activate Virtual Environment
```sh
python -m venv env
source env/bin/activate  # On Windows use: env\Scripts\activate
```

### Step 4: Install Dependencies
```sh
pip install -r requirements.txt
```

### Step 5: Apply Migrations
```sh
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create a Superuser (Required for Video Upload)
```sh
python manage.py createsuperuser
```
Follow the prompts to create an admin account. Only superusers can upload videos via the admin panel.

### Step 7: Run the Server
```sh
python manage.py runserver
```

### Step 8: Start Celery & Redis (for background tasks)
Run Redis:
```sh
redis-server
```
Run Celery:
```sh
celery -A videoflix worker --loglevel=info
```

### Step 9: Create `celery.py` File
You need to create your own `celery.py` file for Celery configuration.


## 📊 Tests Report  
[View Tests Report](https://docs.paul-ivan.com/videoflix-backend/report.html?sort=result)  

## 📈 Tests Coverage Report  
[View Coverage Report](https://docs.paul-ivan.com/videoflix-backend/htmlcov/index.html)  

## 🔗 API Endpoints  
For detailed API documentation, check out [ENDPOINTS.md](ENDPOINTS.md).  

## 📬 Contact  
You can reach me through my portfolio:  
[paul-ivan.com](https://paul-ivan.com) 

