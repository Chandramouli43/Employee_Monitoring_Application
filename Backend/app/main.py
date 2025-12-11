# app/main.py
from fastapi import FastAPI
from sqlalchemy.orm import Session
from app.core.database import Base, engine, SessionLocal
from fastapi.middleware.cors import CORSMiddleware
from app.models import employee, department, team, activity, productivity, screenshot
from app.services.employee_service import create_employee, get_employee_by_email
from app.schemas.employee_schema import EmployeeCreate  # ✅ Ensure schema import
from app.routers import (
    alerts_router,
    department_router,
    employee_router,
    activity_router,
    productivity_router,
    screenshot_router,
    realtime_router,
    analytics_router,
    insights_router,
    auth_router,
    settings_router,
    stats_router,
    attendance,
    leave,
    tasks,
    projects,
    notifications,
    admin_productivity_router,
    admin_config_router,
    admin_reports_router,
)

# ---------------------------
# Create tables if they don't exist
# ---------------------------
Base.metadata.create_all(bind=engine)

# ---------------------------
# FastAPI app
# ---------------------------
app = FastAPI(title="Employee activity and productivity tracking system")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ---------------------------
# Include Routers
# ---------------------------
app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
app.include_router(employee_router.router, )
app.include_router(department_router.router, )
app.include_router(activity_router.router, )
app.include_router(productivity_router.router, )
app.include_router(screenshot_router.router, )
app.include_router(analytics_router.router, )
app.include_router(realtime_router.router, )
app.include_router(insights_router.router, )
app.include_router(alerts_router.router, )
app.include_router(settings_router.router, )
app.include_router(stats_router.router, )

# Attendance Management
app.include_router(attendance.router,)
app.include_router(leave.router, )

# Project Management
app.include_router(tasks.router, )
app.include_router(projects.router,)
app.include_router(notifications.router, )

# Reports
app.include_router(admin_productivity_router.router, )
app.include_router(admin_config_router.router, )
app.include_router(admin_reports_router.router, )


# ---------------------------
# Create Default Admin
# ---------------------------
def create_default_admin():
    """
    Automatically creates a default Admin user if one doesn't exist.
    """
    db = SessionLocal()
    try:
        admin = get_employee_by_email(db, "sam@example.com")
        if not admin:
            # ✅ Matches EmployeeCreate schema fields
            admin_data = EmployeeCreate(
                first_name="sameer",
                last_name="shaik",
                name="sameer shaik",
                email="sam@example.com",
                password="sam123",
                role="Admin",
            )
            create_employee(db, admin_data)
            print("✅ Default admin created: admin@example.com / admin123")
        else:
            print("ℹ️ Admin already exists — skipping creation.")
    except Exception as e:
        print(f"⚠️ Error creating default admin: {e}")
    finally:
        db.close()


# ---------------------------
# Startup Event
# ---------------------------
@app.on_event("startup")
async def startup_event():
    """
    Initialize app — create default admin, start Redis listener, etc.
    """
    print("⚙️ Redis check skipped — using in-memory fallback if not running.")
    create_default_admin()
    print("✅ Startup event completed: app ready.")


# ---------------------------
# Root Endpoint
# ---------------------------
@app.get("/", tags=["Root"])
def root():
    """Simple health check endpoint."""
    return {"message": "Employee Monitoring System is running ✅"}
