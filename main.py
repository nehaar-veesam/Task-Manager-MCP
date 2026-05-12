"""
Task Manager MCP Server 
This server is used to manage tasks and log the actions performed on the tasks.

Author: Nehaar Veesam
"""

import json
import time
import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pathlib import Path 
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parent
TASK_DATA_FILE = BASE_DIR / "task_data.json"
LOG_FILE = BASE_DIR / "log_data.json"

if not TASK_DATA_FILE.exists():
    with open(TASK_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, indent=4)

if not LOG_FILE.exists():
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, indent=4)


def json_default(value):
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"Type not serializable: {type(value)}")


def load_task_data() -> list[dict]:
    try:
        with open(TASK_DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except json.JSONDecodeError:
        return []

def load_log_data() -> list[dict]:
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except json.JSONDecodeError:
        return []

task_data = load_task_data()
log_data = load_log_data()

mcp = FastMCP(name="task-manager")


# Validate Tokens
def validate_token(token:str) -> str:
    load_dotenv(BASE_DIR / ".env")
    token = token.strip()
    if token == os.getenv("VIEWER_TOKEN"):
        return "viewer"
    elif token == os.getenv("EDITOR_TOKEN"):
        return "editor"
    elif token == os.getenv("ADMIN_TOKEN"):
        return "admin"
    else:
        return "Invalid Token"


# Util Functions
def to_iso(value: datetime | str | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def parse_due_at(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def normalize_due_input(due_at: str) -> str | None:
    raw = (due_at or "").strip()
    if not raw:
        return None
    try:
        # Accept YYYY-MM-DD and full ISO timestamps.
        parsed = datetime.fromisoformat(raw)
        return parsed.isoformat()
    except ValueError:
        try:
            parsed = datetime.strptime(raw, "%Y-%m-%d")
            return parsed.isoformat()
        except ValueError:
            return None


def save_task_data(**kwargs):
    log_data.append(kwargs)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=4, default=json_default)

    with open(TASK_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(task_data, f, indent=4, default=json_default)
        

#Create a new task
@mcp.tool()
def create_task(token: str, title: str, description: str, priority: str, due_at: str, status: str) -> str:
    """ Create a new task with given title, description and priority"""
    user_role = validate_token(token)
    if user_role =="editor" or user_role == "admin":
        normalized_due_at = normalize_due_input(due_at)
        if due_at and normalized_due_at is None:
            return "Invalid due_at format. Use YYYY-MM-DD or ISO datetime."
            
        existing_ids = [task["id"] for task in task_data]
        new_task = {
            "id": max(existing_ids)+1,
            "title": title,
            "description": description, 
            "priority": priority,
            "status": status,
            "created_at": f"{datetime.now()}",
            "updated_at": f"{datetime.now()}",
            "completed_at": None,
            "due_at": normalized_due_at
        }
        task_data.append(new_task)
        audit_data = {
            "event_id": int(float(time.time())),
            "timestamp": f"{datetime.now()}",
            "action": "create_task",
            "target_id": new_task["id"],
            "actor":"system"
        }
        save_task_data(**audit_data)
        return f"Task Created Successfully for {new_task['id']} and title is {new_task['title']}"
    elif user_role == "viewer":
        return "You are not authorized to create tasks"
    else:
        return "Invalid Token provided"
        


# Get Task information by task_id
@mcp.tool()
def get_task(title: str, id: int):
    """ Get Task Information by task id"""
    for task in task_data:
        if task["id"] == id or title == task["title"]:
            return task
    return f"Task not found with id {id} or title {title}"


#List all tasks
@mcp.tool()
def list_tasks() -> list[dict]:
    """List all tasks available in the task_data"""
    return task_data


#Update Task 
@mcp.tool()
def update_task_status(token: str, id: int, title: str, status: str) -> str:
    "Update the task with given id , title and status"
    user_role = validate_token(token)
    if user_role =="editor" or user_role == "admin":
        for task in task_data:
            if task["id"] == id or title == task["title"]:
                task["status"] = status
                task["updated_at"] = f"{datetime.now()}"
                if status == "completed":
                    task["completed_at"] = f"{datetime.now()}"
                audit_data = {
                    "event_id": int(float(time.time())),
                    "timestamp": f"{datetime.now()}",
                    "action": "update_task_status",
                    "target_id": task["id"],
                    "actor":"system"
                }
                save_task_data(**audit_data)
                return f"Task updated successfully for {task['id']} and title is {task['title']} and status is {task['status']}"
        return f"Task not present with id {id} or title {title}"
    elif user_role == "viewer":
        return "You are not authorized to create tasks"
    else:
        return "Invalid Token provided"

# Update task information
@mcp.tool()
def update_task(token: str, id:int, title:str, description:str, priority:str) -> str:
    """Update the task with given id, title, description and priority"""
    user_role = validate_token(token)
    if user_role =="editor" or user_role == "admin":
        for task in task_data:
            if task['id'] == id or title == task['title']:
                task['title'] = title
                task['description'] = description
                task['priority'] = priority
                task['updated_at'] = f"{datetime.now()}"
                audit_data = {
                    "event_id": int(float(time.time())),
                    "timestamp": f"{datetime.now()}",
                    "action": "update_task",
                    "target_id": task["id"],
                    "actor":"system"
                }
                save_task_data(**audit_data)
                return f"Task updated successfully for {task['id']} and title is {task['title']} and description is {task['description']} and priority is {task['priority']}"
        return f"Task not present with id {id} or title {title}"
    elif user_role == "viewer":
        return "You are not authorized to create tasks"
    else:
        return "Invalid Token provided"

#Delete Task
@mcp.tool()
def delete_task(token: str, id:int, title:str) -> str:
    """Delete the task with given id and title"""
    user_role = validate_token(token)
    if user_role =="admin":
        for task in task_data:
            if task['id'] == id or title == task['title']:
                task_data.remove(task)
                audit_data = {
                    "event_id": int(float(time.time())),
                    "timestamp": f"{datetime.now()}",
                    "action": "delete_task",
                    "target_id": task["id"],
                    "actor":"system"
                }
                save_task_data(**audit_data)
                return f"Task deleted successfully for {task['id']} and title is {task['title']}"
        return f"Task not present with id {id} or title {title}"
    elif user_role == "viewer" or user_role == "editor":
        return "You are not authorized to delete tasks"
    else:
        return "Invalid Token provided"


#List Tasks by status
@mcp.tool()
def list_tasks_by_status(status:str):
    """ List all tasks by status """
    return [task for task in task_data if task["status"] == status]


#List Tasks by Priority 
@mcp.tool()
def list_tasks_by_priority(priority:str):
    """ List all tasks by priority """
    return [task for task in task_data if task["priority"] == priority]


# set_due_date for task 
@mcp.tool()
def set_due_date(token: str, task_id:int, due_at:str, title:str) -> dict:
    """ Set the due date for a task """
    user_role = validate_token(token)
    if user_role =="editor" or user_role == "admin":
        normalized_due_at = normalize_due_input(due_at)
        if normalized_due_at is None:
            return {
                "ok": False,
                "error": "Invalid due_at format. Use YYYY-MM-DD or ISO datetime.",
            }

        for task in task_data:
            if task["id"] == task_id or task["title"] == title:
                task["due_at"] = normalized_due_at
                task["updated_at"] = f"{datetime.now()}"
                audit_data = {
                    "event_id": int(float(time.time())),
                    "timestamp": f"{datetime.now()}",
                    "action": "set_due_date",
                    "target_id": task["id"],
                    "actor":"system"
                }
                save_task_data(**audit_data)
                return {
                    "ok": True,
                    "task_id": task["id"],
                    "title": task["title"],
                    "due_at": task["due_at"],
                }
        return {"ok": False, "error": f"Task not present with id {task_id} or title {title}"}
    elif user_role == "viewer" :
        return "You are not authorized to set due date for tasks"
    else:
        return "Invalid Token provided"

#List Overdue Tasks
@mcp.tool()
def list_overdue_tasks(now:datetime) -> list[dict]:
    """ List all overdue tasks """
    overdue_tasks = []
    now = datetime.now()
    for task in task_data:
        due_at = parse_due_at(task.get("due_at"))
        if due_at and due_at < now:
            overdue_tasks.append(task)
    return overdue_tasks


#List Due soon Tasks
@mcp.tool()
def list_due_soon_tasks(now:datetime) -> list[dict]:
    """ List all due soon tasks where due_at is within next 24 hrs """
    due_soon_tasks = []
    now = datetime.now()
    for task in task_data:
        due_at = parse_due_at(task.get("due_at"))
        if due_at and now < due_at < now + timedelta(hours=24):
            due_soon_tasks.append(task)
    return due_soon_tasks


if __name__ == "__main__":
    mcp.run()
