from fastapi import APIRouter, Form, Depends, HTTPException
from app.utils.auth import get_current_user
from app.config import Config
import requests
import json

router = APIRouter()

SUPABASE_URL = Config.SUPABASE_URL
SUPABASE_KEY = Config.SUPABASE_SERVICE_ROLE_KEY  # backend-only key

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# -------------------- SAVE RESUME --------------------

@router.post("/save-resume")
async def save_resume(
    title: str = Form(...),
    latex: str = Form(...),
    user = Depends(get_current_user)
):
    user_id = user["sub"]

    payload = {
        "user_id": user_id,
        "title": title,
        "latex": latex
    }

    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/resumes",
        headers=headers,
        data=json.dumps(payload)
    )

    if response.status_code not in (200, 201):
        raise HTTPException(500, f"Supabase insert failed: {response.text}")

    return { "status": "success" }

# -------------------- GET USER RESUMES --------------------

@router.get("/resumes")
async def get_resumes(user = Depends(get_current_user)):
    user_id = user["sub"]

    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/resumes?user_id=eq.{user_id}&order=updated_at.desc",
        headers=headers
    )

    if response.status_code != 200:
        raise HTTPException(500, f"Supabase query failed: {response.text}")

    return response.json()

# -------------------- DELETE RESUME --------------------

@router.delete("/resumes/{resume_id}")
async def delete_resume(resume_id: str, user = Depends(get_current_user)):
    user_id = user["sub"]

    response = requests.delete(
        f"{SUPABASE_URL}/rest/v1/resumes?id=eq.{resume_id}&user_id=eq.{user_id}",
        headers=headers
    )

    if response.status_code not in (200, 204):
        raise HTTPException(500, "Failed to delete resume")

    return { "status": "deleted" }

# -------------------- ADD EXPERIENCE --------------------

@router.post("/experiences/add")
async def add_experience(
    company: str = Form(None),
    role: str = Form(None),
    bullets_json: str = Form(...),
    user = Depends(get_current_user)
):
    user_id = user["sub"]
    bullets = json.loads(bullets_json)

    payload = {
        "user_id": user_id,
        "company": company,
        "role": role,
        "bullets": bullets
    }

    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/experiences",
        headers=headers,
        data=json.dumps(payload)
    )

    if response.status_code not in (200, 201):
        raise HTTPException(500, f"Insert failed: {response.text}")

    return { "status": "success" }

# -------------------- DELETE EXPERIENCE --------------------

@router.delete("/experiences/{exp_id}")
async def delete_experience(exp_id: str, user = Depends(get_current_user)):
    user_id = user["sub"]

    response = requests.delete(
        f"{SUPABASE_URL}/rest/v1/experiences?id=eq.{exp_id}&user_id=eq.{user_id}",
        headers=headers
    )

    if response.status_code not in (200, 204):
        raise HTTPException(500, "Failed to delete experience")

    return { "status": "deleted" }

# -------------------- ADD PROJECT --------------------

@router.post("/projects/add")
async def add_project(
    name: str = Form(None),
    tech_stack_json: str = Form(...),
    bullets_json: str = Form(...),
    user = Depends(get_current_user)
):
    user_id = user["sub"]
    tech_stack = json.loads(tech_stack_json)
    bullets = json.loads(bullets_json)

    payload = {
        "user_id": user_id,
        "name": name,
        "tech_stack": tech_stack,
        "bullets": bullets
    }

    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/projects",
        headers=headers,
        data=json.dumps(payload)
    )

    if response.status_code not in (200, 201):
        raise HTTPException(500, f"Insert failed: {response.text}")

    return { "status": "success" }

# -------------------- DELETE PROJECT --------------------

@router.delete("/projects/{project_id}")
async def delete_project(project_id: str, user = Depends(get_current_user)):
    user_id = user["sub"]

    response = requests.delete(
        f"{SUPABASE_URL}/rest/v1/projects?id=eq.{project_id}&user_id=eq.{user_id}",
        headers=headers
    )

    if response.status_code not in (200, 204):
        raise HTTPException(500, "Failed to delete project")

    return { "status": "deleted" }
