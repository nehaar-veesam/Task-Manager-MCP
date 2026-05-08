from mcp.server.fastmcp import FastMCP
from pathlib import Path 
from datetime import datetime
from typing import List, Optional, Dict
import json
import os

BASE_DIR = Path(__file__).resolve().parent
TASK_DATA_FILE = BASE_DIR / "task_data.json"

if not TASK_DATA_FILE.exists():
    with open(TASK_DATA_FILE, "w") as f:
        json.dump([], f)

with open(TASK_DATA_FILE, "r") as f:
    task_data = json.load(f)

mcp = FastMCP(name="task-manager")

"""
Features

create_task(title, description?, priority?)
get_task(task_id)
list_tasks()
update_task(task_id, title?, description?, priority?)
update_task_status(task_id, status)
delete_task(task_id)
"""



def save_task_data():
    with open(TASK_DATA_FILE, "w") as f:
        json.dump(task_data, f, indent=4)
        


#Create a new task
@mcp.tool()
def create_task(title: str, description: str, priority: str) -> str:
    """ Create a new task with given title, description and priority"""
    new_task = {
        "id": len(task_data) + 1,
        "title": title,
        "description": description, 
        "priority": priority,
        "status": "todo",
        "created_at": f"{datetime.now()}",
        "updated_at": f"{datetime.now()}",
        "completed_at": None
    }
    task_data.append(new_task)
    save_task_data()
    return f"Task Created Successfully for {new_task['id']} and title is {new_task['title']}"

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
def update_task_status(id: int, title: str, status: str) -> str:
    "Update the task with given id , title and status"
    for task in task_data:
        if task["id"] == id or title == task["title"]:
            task["status"] = status
            task["updated_at"] = f"{datetime.now()}"
            if status == "completed":
                task["completed_at"] = f"{datetime.now()}"
            save_task_data()
            return f"Task updated successfully for {task['id']} and title is {task['title']} and status is {task['status']}"
    return f"Task not present with id {id} or title {title}"

# Update task information
@mcp.tool()
def update_task(id:int, title:str, description:str, priority:str) -> str:
    """Update the task with given id, title, description and priority"""
    for task in task_data:
        if task['id'] == id or title == task['title']:
            task['title'] = title
            task['description'] = description
            task['priority'] = priority
            task['updated_at'] = f"{datetime.now()}"
            save_task_data()
            return f"Task updated successfully for {task['id']} and title is {task['title']} and description is {task['description']} and priority is {task['priority']}"
    return f"Task not present with id {id} or title {title}"

#Delete Task
@mcp.tool()
def delete_task(id:int, title:str) -> str:
    """Delete the task with given id and title"""
    for task in task_data:
        if task['id'] == id or title == task['title']:
            task_data.remove(task)
            save_task_data()
            return f"Task deleted successfully for {task['id']} and title is {task["title"]}"
    return f"Task not present with id {id} or title {title}"




if __name__ == "__main__":
    mcp.run()
