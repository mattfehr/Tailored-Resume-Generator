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

    return {"status": "success"}

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

@router.post("/resumes/{resume_id}/delete")
async def delete_resume(resume_id: str, user = Depends(get_current_user)):
    user_id = user["sub"]

    response = requests.delete(
        f"{SUPABASE_URL}/rest/v1/resumes?id=eq.{resume_id}&user_id=eq.{user_id}",
        headers=headers
    )

    if response.status_code not in (200, 204):
        raise HTTPException(500, f"Failed to delete resume: {response.text}")

    return {"status": "deleted"}

# -------------------- RENAME RESUME --------------------

@router.post("/resumes/{resume_id}/rename")
async def rename_resume(
    resume_id: str,
    new_title: str = Form(...),
    user = Depends(get_current_user)
):
    user_id = user["sub"]

    payload = {"title": new_title}

    response = requests.patch(
        f"{SUPABASE_URL}/rest/v1/resumes?id=eq.{resume_id}&user_id=eq.{user_id}",
        headers=headers,
        data=json.dumps(payload)
    )

    if response.status_code not in (200, 204):
        raise HTTPException(500, f"Failed to rename resume: {response.text}")

    return {"status": "renamed"}

# -------------------- ADD EXPERIENCE --------------------

@router.post("/experiences/add")
async def add_experience(
    company: str = Form(None),
    role: str = Form(None),
    start_date: str = Form(None),
    end_date: str = Form(None),
    bullets_json: str = Form(...),
    user = Depends(get_current_user)
):
    user_id = user["sub"]
    bullets = json.loads(bullets_json)

    payload = {
        "user_id": user_id,
        "company": company,
        "role": role,
        "start_date": start_date,
        "end_date": end_date,
        "bullets": bullets
    }

    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/experiences",
        headers=headers,
        data=json.dumps(payload)
    )

    if response.status_code not in (200, 201):
        raise HTTPException(500, f"Insert failed: {response.text}")

    return {"status": "success"}

# -------------------- DELETE EXPERIENCE --------------------

@router.post("/experiences/{exp_id}/delete")
async def delete_experience(exp_id: str, user = Depends(get_current_user)):
    user_id = user["sub"]

    response = requests.delete(
        f"{SUPABASE_URL}/rest/v1/experiences?id=eq.{exp_id}&user_id=eq.{user_id}",
        headers=headers
    )

    if response.status_code not in (200, 204):
        raise HTTPException(500, "Failed to delete experience")

    return {"status": "deleted"}

# -------------------- ADD PROJECT --------------------

@router.post("/projects/add")
async def add_project(
    name: str = Form(None),
    tech_stack_json: str = Form(...),
    start_date: str = Form(None),
    end_date: str = Form(None),
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
        "start_date": start_date,
        "end_date": end_date,
        "bullets": bullets
    }

    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/projects",
        headers=headers,
        data=json.dumps(payload)
    )

    if response.status_code not in (200, 201):
        raise HTTPException(500, f"Insert failed: {response.text}")

    return {"status": "success"}

# -------------------- DELETE PROJECT --------------------

@router.post("/projects/{project_id}/delete")
async def delete_project(project_id: str, user = Depends(get_current_user)):
    user_id = user["sub"]

    response = requests.delete(
        f"{SUPABASE_URL}/rest/v1/projects?id=eq.{project_id}&user_id=eq.{user_id}",
        headers=headers
    )

    if response.status_code not in (200, 204):
        raise HTTPException(500, "Failed to delete project")

    return {"status": "deleted"}

# -------------------- GET USER EXPERIENCES --------------------

@router.get("/experiences")
async def get_experiences(user = Depends(get_current_user)):
    user_id = user["sub"]

    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/experiences?user_id=eq.{user_id}",
        headers=headers
    )

    if response.status_code != 200:
        raise HTTPException(500, f"Failed to fetch experiences: {response.text}")

    return response.json()

# -------------------- GET USER PROJECTS --------------------

@router.get("/projects")
async def get_projects(user = Depends(get_current_user)):
    user_id = user["sub"]

    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/projects?user_id=eq.{user_id}",
        headers=headers
    )

    if response.status_code != 200:
        raise HTTPException(500, f"Failed to fetch projects: {response.text}")

    return response.json()

# -------------------- SAVE TEMPLATE --------------------

@router.post("/templates/save")
async def save_template(
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
        f"{SUPABASE_URL}/rest/v1/resume_templates",
        headers=headers,
        data=json.dumps(payload)
    )

    if response.status_code not in (200, 201):
        raise HTTPException(500, f"Supabase insert failed: {response.text}")

    return {"status": "success"}

# -------------------- GET TEMPLATES --------------------

@router.get("/templates")
async def get_templates(user = Depends(get_current_user)):
    user_id = user["sub"]

    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/resume_templates?user_id=eq.{user_id}&order=updated_at.desc",
        headers=headers
    )

    if response.status_code != 200:
        raise HTTPException(500, f"Supabase query failed: {response.text}")

    return response.json()

# -------------------- DELETE TEMPLATE --------------------

@router.post("/templates/{template_id}/delete")
async def delete_template(template_id: str, user = Depends(get_current_user)):
    user_id = user["sub"]

    response = requests.delete(
        f"{SUPABASE_URL}/rest/v1/resume_templates?id=eq.{template_id}&user_id=eq.{user_id}",
        headers=headers
    )

    if response.status_code not in (200, 204):
        raise HTTPException(500, f"Failed to delete template: {response.text}")

    return {"status": "deleted"}

# -------------------- RENAME TEMPLATE --------------------

@router.post("/templates/{template_id}/rename")
async def rename_template(
    template_id: str,
    new_title: str = Form(...),
    user = Depends(get_current_user)
):
    user_id = user["sub"]

    payload = {"title": new_title}

    response = requests.patch(
        f"{SUPABASE_URL}/rest/v1/resume_templates?id=eq.{template_id}&user_id=eq.{user_id}",
        headers=headers,
        data=json.dumps(payload)
    )

    if response.status_code not in (200, 204):
        raise HTTPException(500, f"Failed to rename template: {response.text}")

    return {"status": "renamed"}

