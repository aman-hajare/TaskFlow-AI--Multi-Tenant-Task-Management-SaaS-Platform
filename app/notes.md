# service layer
Router → Service → Repository

Layer	             Responsibility
  Router	    =       only HTTP handling(api)
  Service	    =       business logic + logging
  Repository	=       database queries


# Standard Response Utility = app.utils.responses
# Custom Exception Class = app.core.exceptions
# Global Exception Handler = app.middleware.exception_handler

# logger.info -> system logs 
2026-03-14 10:02:21 | INFO | taskflow | User created task 45

# ActivityLog ->  database history (use for create, update, delete)
# (what user did)
User Aman created task "Fix Login Bug"
User Rahul updated task status → Done
User Aman deleted task
User Aman logged in

# Audit Logs -> Track data changes (audit log mainly for update )
# (what data changed)
#Example
Task status changed
Old value: pending
New value: completed
Changed by: Aman


### project now supports:
Multi-Tenant SaaS Architecture
RBAC Authorization
Redis Caching
Structured Logging
Centralized Exception Handling
Activity Logging
Audit Logging
Background Workers (Celery)
Notification System
Real-Time WebSockets
Event-Driven Architecture(Event Bus)
Rate Limiting Security(redis_based) slowapi
Distributed Task Scheduling(celery Beat)
monitoring
production openapi docs
AI Task Intelligence

# AI Capabilities
• AI Skill Detection  
• AI Priority Prediction  
• AI Tag Generation  
• Smart Workload Balancing  
• Task Risk Prediction  
• Overdue Task Analysis  

# System Architecture
API → Service → Repository → Database

### Technologies
FastAPI  
PostgreSQL  
SQLAlchemy  
Redis  
Celery  
Docker

###
Your API documentation is now production-grade.

It includes:

OpenAPI Metadata
Tags
Endpoint summaries
Detailed descriptions
Request examples
Response models
Error schemas
JWT security docs
Improved Swagger UI

###
🌍 Your Services
Service	URL
FastAPI	http://localhost:8000

Swagger	http://localhost:8000/docs

Flower	http://localhost:5555

Postgres	localhost:5432
Redis	localhost:6379


xysm ajez fwnd hwlt


celery -A app.background.celery_app worker -Q emails --loglevel=info
celery -A app.background.celery_app worker -Q notifications --loglevel=info
celery -A app.background.celery_app worker -Q analytics --loglevel=info
celery -A app.background.celery_app worker -Q cleanup --loglevel=info
celery -A app.background.celery_app beat --loglevel=info


first start redis
docker run -d -p 6379:6379 redis
celery -A app.background.celery_app worker -Q taskflow_queue --loglevel=info
celery -A app.background.celery_app beat --loglevel=info


celery -A app.background.celery_app flower
http://localhost:5555

docker logs -f taskflow_celery_worker
docker logs taskflow_celery_worker

>> docker commands
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"; Start-Sleep -Seconds 20; docker compose up -d --build

start docker-desktop(for desktop)
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe" (for only terminal)
docker compose up -d   # normal fast start
docker compose up  (if not want to rebuild image)
docker compose up --build (if want to rebuild image after changes) (by defult attach mood)
docker compose up --build -d  (container keep running even if close terminal, and not allow to check logs)(-d detach mood)
(actully all -d is detach mood)

docker compose exec api alembic revision --autogenerate -m "add task deadline"
docker compose exec api alembic upgrade head

# commands for databse container -it 
docker ps
docker exec -it taskflow_postgres psql -U postgres -d taskflow_db
\l
\c taskflow_db 
\dt
\pset pager off
\d [table name]
\d+ [table name]
\q 


stop all container run always in terminal
docker stop $(docker ps -q)

Policy	Meaning
"no"	restart nahi karega
always	hamesha restart karega
on-failure	sirf error pe restart
unless-stopped	jab tak manually stop na karo

🐘 Postgres → database
⚡ Redis → queue / cache
🚀 API → FastAPI server
🧵 Celery  → background worker
⏰ Celery Beat → scheduled tasks
🌸 Flower → monitoring UI


apt get update  = Linuz ubuntu adavanc package tool, get update


Command 	              work                where use
docker compose up	run    containers	        dev/debug
docker compose up -d	   run in background	 ✅production
docker compose build	    image build	        dependency change
docker compose up --build	     build + run	  quick dev
docker compose down	         stop + remove	  reset
docker compose build api	  specific build	  fast rebuild

# check and remove volume
docker volume ls
docker volume rm postgres_data

wsl --shutdown

\\wsl$\docker-desktop\mnt\docker-desktop-disk\data\docker\volumes


Create Task
↓
TaskService
↓
EventBus (TASK_ASSIGNED)
↓
Subscriber
↓
Celery Task
↓
NotificationService
↓
"You have been assigned task #ID"



docker exec -it taskflow_celery_worker python
from app.background.tasks import cleanup_old_activity_logs
cleanup_old_activity_logs.delay()