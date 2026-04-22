from fastapi import FastAPI
from app.api import auth,users,companies,tasks,ws_notifications,notifications,ai,health,monitoring,invites,admin,reset_password

from app.middleware.request_logger import RequestLogginMiddleware
from app.middleware.exception_handler import (
    app_exeception_handler, generic_exception_handler
    )
from app.core.exceptions import AppException
from slowapi.middleware import SlowAPIMiddleware

from fastapi.middleware.cors import CORSMiddleware

from app.core.rate_limiter import limiter, rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.events.subscribers import *

from app.utils.openapi_tags import tags_metadata

app = FastAPI(
    title="TaskFlow AI",
    description="""
# 🚀 TaskFlow AI — Multi-Tenant AI Powered Task Management Platform

TaskFlow AI is a **production-grade SaaS backend system** designed for modern productivity platforms like Jira, ClickUp, and Notion.

It combines **scalable architecture, real-time communication, and AI-powered intelligence** to manage tasks efficiently across multiple organizations.

---

# 🧠 Key Features

• 🏢 Multi-Tenant Architecture (company-level data isolation)  
• 🔐 JWT Authentication (Access & Refresh Tokens)  
• 👥 Role-Based Access Control (Admin, Manager, Employee)  
• ⚡ Event-Driven Architecture (decoupled system using Event Bus)  
• 🔄 Background Processing (Celery + Redis)  
• 📡 Real-Time Notifications (WebSockets)  
• 🚀 Redis Caching & Rate Limiting (SlowAPI)  
• 📊 Activity Logging & Audit Logging  
• 🐳 Dockerized Production Deployment  
• 📄 Production-ready OpenAPI Documentation  

---

# 🤖 AI Capabilities

• AI Skill Detection  
• AI Task Priority Prediction  
• AI Tag Generation  
• Smart Workload Balancing  
• Task Risk Prediction  
• Overdue Task Analysis  

---

# 🔔 Notification System

• In-app notifications (database)  
• Real-time WebSocket updates  
• Async email notifications via Celery  

---

# ⚙️ Background Jobs & Scheduling

• Celery Workers for async processing  
• Celery Beat for scheduled jobs  
• Deadline reminders & reports  
• Automatic retry & failure handling  

---

# 🏗️ System Architecture

API → Service → Repository → Database  
        ↓  
    Event Bus → Celery → Notifications / Email  
        ↓  
    Redis → Cache & Queue Broker  
        ↓  
    WebSocket → Real-Time Updates  

---

# 🔐 Security Features

• Secure password hashing (bcrypt)  
• JWT-based authentication  
• Role-based authorization  
• Redis-based rate limiting  
• Multi-tenant data isolation  


# 🛠 Tech Stack

FastAPI  
PostgreSQL  
SQLAlchemy  
Redis  
Celery  
WebSockets  
Docker  

---

# 💡 Why This Project Stands Out

• Implements real-world SaaS architecture  
• Uses event-driven design (rare in student projects)  
• Includes AI-powered task intelligence  
• Supports real-time communication  
• Fully containerized and production-ready  

---

""",
    version="1.0.0",
    contact={
        "name": "TaskFlow AI Engineering Team",
        "email": "support@taskflow.ai"
    },
    openapi_tags=tags_metadata
)



app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    rate_limit_exceeded_handler
)


app.add_middleware(SlowAPIMiddleware)
app.add_middleware(RequestLogginMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppException, app_exeception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(invites.router)
app.include_router(companies.router)
app.include_router(admin.router)
app.include_router(tasks.router)
app.include_router(ws_notifications.router)
app.include_router(notifications.router)
app.include_router(ai.router)
app.include_router(health.router)
app.include_router(monitoring.router)
app.include_router(reset_password.router)


@app.get("/")
def root():
    return {"message": "TaskFlow AI Backend Running"}
