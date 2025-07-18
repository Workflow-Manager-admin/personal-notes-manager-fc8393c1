from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas, auth
from .database import engine, Base
from fastapi.security import OAuth2PasswordRequestForm

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Personal Notes Backend",
    description="A backend API for personal notes application with JWT authentication and CRUD endpoints.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set to the real frontend origin(s)!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", summary="Health Check")
def health_check():
    """Health check endpoint."""
    return {"message": "Healthy"}


# REGION: Auth endpoints

# PUBLIC_INTERFACE
@app.post("/api/auth/register", response_model=schemas.UserResponse, tags=["Auth"], summary="Register new user")
def register(user_in: schemas.UserCreate, db: Session = Depends(auth.get_db)):
    """Register a new user."""
    if db.query(models.User).filter(models.User.username == user_in.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    if db.query(models.User).filter(models.User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = auth.get_password_hash(user_in.password)
    db_user = models.User(username=user_in.username, email=user_in.email, hashed_password=hashed_pw)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# PUBLIC_INTERFACE
@app.post("/api/auth/login", response_model=schemas.Token, tags=["Auth"], summary="User login to get JWT")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(auth.get_db)):
    """Authenticate and get JWT."""
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = auth.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

# PUBLIC_INTERFACE
@app.get("/api/users/me", response_model=schemas.UserResponse, tags=["Auth"], summary="Get current user info")
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    """Return info about the authenticated user."""
    return current_user

# REGION: Notes endpoints (JWT-protected)

# PUBLIC_INTERFACE
@app.post("/api/notes/", response_model=schemas.NoteResponse, tags=["Notes"], summary="Create a new note")
def create_note(note: schemas.NoteCreate, db: Session = Depends(auth.get_db),
                current_user: models.User = Depends(auth.get_current_user)):
    """Create a note for the current user."""
    db_note = models.Note(**note.dict(), owner_id=current_user.id)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

# PUBLIC_INTERFACE
@app.get("/api/notes/", response_model=List[schemas.NoteResponse], tags=["Notes"], summary="List user's notes")
def list_notes(db: Session = Depends(auth.get_db),
               current_user: models.User = Depends(auth.get_current_user)):
    """List all notes for the current user."""
    notes = db.query(models.Note).filter(models.Note.owner_id == current_user.id).order_by(models.Note.created_at.desc()).all()
    return notes

# PUBLIC_INTERFACE
@app.get("/api/notes/{note_id}", response_model=schemas.NoteResponse, tags=["Notes"], summary="Get a note by ID")
def get_note(note_id: int, db: Session = Depends(auth.get_db),
             current_user: models.User = Depends(auth.get_current_user)):
    """Get a specific note by ID, if owned by the current user."""
    note = db.query(models.Note).filter(models.Note.id == note_id, models.Note.owner_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

# PUBLIC_INTERFACE
@app.put("/api/notes/{note_id}", response_model=schemas.NoteResponse, tags=["Notes"], summary="Update an existing note")
def update_note(note_id: int, note_in: schemas.NoteUpdate, db: Session = Depends(auth.get_db),
                current_user: models.User = Depends(auth.get_current_user)):
    """Update a note."""
    note = db.query(models.Note).filter(models.Note.id == note_id, models.Note.owner_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    update_data = note_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(note, key, value)
    db.commit()
    db.refresh(note)
    return note

# PUBLIC_INTERFACE
@app.delete("/api/notes/{note_id}", status_code=204, tags=["Notes"], summary="Delete a note")
def delete_note(note_id: int, db: Session = Depends(auth.get_db),
                current_user: models.User = Depends(auth.get_current_user)):
    """Delete a note if owned by user."""
    note = db.query(models.Note).filter(models.Note.id == note_id, models.Note.owner_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
    return

# OpenAPI doc note about auth for quick start
@app.get("/api/openapi_auth_help", tags=["Docs"], summary="How to authenticate", description="Details for authenticating with JWT")
def openapi_auth_help():
    """
    Usage:
    - Register a user at /api/auth/register (POST, JSON body)
    - Login at /api/auth/login (POST, form-encoded, returns access token)
    - Use header `Authorization: Bearer <access_token>` for all protected endpoints
    """
    return {
        "steps": [
            "POST /api/auth/register with JSON {username, email, password}",
            "POST /api/auth/login with form fields {username, password}, get JWT token",
            "Include 'Authorization: Bearer <token>' header in API calls"
        ]
    }
