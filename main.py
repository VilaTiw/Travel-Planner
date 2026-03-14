from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
import services
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Travel Planner API",
    description="A CRUD application for managing travel projects and places.",
    version="1.0.0"
)


@app.post("/projects", response_model=schemas.ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    if project.places:
        if len(project.places) > 10:
            raise HTTPException(status_code=400, detail="A project can have a maximum of 10 places.")
        if len(project.places) != len(set(project.places)):
            raise HTTPException(status_code=400, detail="Duplicate external IDs are not allowed in the same project.")

        # Validate places via third-party API
        for ext_id in project.places:
            await services.validate_place_exists(ext_id)

    db_project = models.Project(name=project.name, description=project.description, start_date=project.start_date)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    if project.places:
        for ext_id in project.places:
            db_place = models.Place(project_id=db_project.id, external_id=ext_id)
            db.add(db_place)
        db.commit()
        db.refresh(db_project)

    return db_project


@app.get("/projects", response_model=List[schemas.ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    return db.query(models.Project).all()


@app.get("/projects/{project_id}", response_model=schemas.ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.patch("/projects/{project_id}", response_model=schemas.ProjectResponse)
def update_project(project_id: int, project_update: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = project_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)
    return project


@app.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if any(place.is_visited for place in project.places):
        raise HTTPException(status_code=400, detail="Cannot delete project: some places are already marked as visited.")

    db.delete(project)
    db.commit()


@app.post("/projects/{project_id}/places", response_model=schemas.PlaceResponse, status_code=status.HTTP_201_CREATED)
async def add_place_to_project(project_id: int, place: schemas.PlaceCreate, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if len(project.places) >= 10:
        raise HTTPException(status_code=400, detail="Maximum limit of 10 places reached for this project.")

    if any(p.external_id == place.external_id for p in project.places):
        raise HTTPException(status_code=400, detail="This place already exists in the project.")

    await services.validate_place_exists(place.external_id)

    db_place = models.Place(project_id=project_id, external_id=place.external_id, notes=place.notes)
    db.add(db_place)
    db.commit()
    db.refresh(db_place)

    # Reset project completion status if a new unvisited place is added
    if project.is_completed:
        project.is_completed = False
        db.commit()

    return db_place


@app.get("/projects/{project_id}/places", response_model=List[schemas.PlaceResponse])
def list_places(project_id: int, db: Session = Depends(get_db)):
    places = db.query(models.Place).filter(models.Place.project_id == project_id).all()
    return places


@app.patch("/projects/{project_id}/places/{place_id}", response_model=schemas.PlaceResponse)
def update_place(project_id: int, place_id: int, place_update: schemas.PlaceUpdate, db: Session = Depends(get_db)):
    place = db.query(models.Place).filter(models.Place.id == place_id, models.Place.project_id == project_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Place not found in this project")

    if place_update.notes is not None:
        place.notes = place_update.notes
    if place_update.is_visited is not None:
        place.is_visited = place_update.is_visited

    db.commit()
    db.refresh(place)

    # Check project completion logic
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    all_visited = len(project.places) > 0 and all(p.is_visited for p in project.places)

    if project.is_completed != all_visited:
        project.is_completed = all_visited
        db.commit()

    return place