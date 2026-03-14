# Travel-Planner

A backend RESTful API system to manage travel projects and places, integrated with the Art Institute of Chicago API. Built for the Python Engineer test assessment.

## Features
- **Project & Place CRUD**: Create, read, update, and delete travel projects and places.
- **External API Integration**: Validates places against the Art Institute of Chicago API (`api.artic.edu`) before adding them to a project.
- **Business Logic**:
  - Maximum of 10 places per project.
  - Duplicate places in the same project are prevented.
  - Projects cannot be deleted if any place is marked as visited.
  - Project `is_completed` status automatically updates when all places are visited.
- **Dockerized**: Easy setup and deployment using Docker.

## Tech Stack
- Python 3.11+
- FastAPI
- SQLite (SQLAlchemy ORM)
- HTTPX (Async HTTP client)

## How to Run

### Option 1: Using Docker (Recommended)
1. Build the Docker image:
   ```bash
   docker build -t travel-planner-api .
   ```
2. Run the container:
   ```bash
   docker run -p 8000:8000 travel-planner-api
   ```

### Option 2: Running Locally
1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

## API Documentation (Swagger UI)
Once the application is running, interactive API documentation is automatically available at:
👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

You can use this interface to test all endpoints.

## Example Request

**Create a new project with places:**
`POST /projects`

```json
{
  "name": "Chicago Trip",
  "description": "Places to visit during the art weekend",
  "start_date": "2026-03-14",
  "places": [
    "129884",
    "111436"
  ]
}
```

Note: The IDs in the places array are real external IDs from the Art Institute of Chicago API to pass the backend validation.
