# Todo API

A RESTful API built with Flask for managing todos. The API provides endpoints to create, read, update, and delete todos.

## Features

- Create new todos with title, description, and due date
- List all todos
- Get single todo by ID
- Update existing todos
- Delete todos
- SQLite database for data storage
- Unit tests with pytest
- Docker support
- GitHub Actions CI/CD pipeline

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   flask run
   ```

## API Endpoints

- `GET /todos` - List all todos
- `GET /todos/<id>` - Get a specific todo
- `POST /todos` - Create a new todo
- `PUT /todos/<id>` - Update a todo
- `DELETE /todos/<id>` - Delete a todo

### Example Request Body (POST/PUT)

```json
{
    "title": "Complete project",
    "description": "Finish the todo API project",
    "due_date": "2024-03-01T12:00:00"
}
```

## Running Tests

```bash
pytest
```

For test coverage:
```bash
pytest --cov=app tests/
```

## Docker

Build the image:
```bash
docker build -t todo-api .
```

Run the container:
```bash
docker run -p 5000:5000 todo-api
```

## CI/CD

The project includes a GitHub Actions workflow that:
1. Runs tests on every push and pull request
2. Builds a Docker image on merges to main branch

## License

MIT 