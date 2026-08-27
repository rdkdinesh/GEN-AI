import fastapi


# write a employee management API using fastapi with the following endpoints:
# 1. GET /employees - Get a list of all employees
app = fastapi.FastAPI()

@app.get("/employees")
def get_employees():
    # Placeholder implementation - replace with actual employee data retrieval logic
    return [{"id": 1, "name": "John Doe"}, {"id": 2, "name": "Jane Smith"}]

# 2. POST /employees - Create a new employee
@app.post("/employees")
def create_employee(employee: dict):
    # Placeholder implementation - replace with actual employee creation logic
    return {"id": 3, "name": employee["name"]}

# 3. GET /employees/{employee_id} - Get details of a specific employee
@app.get("/employees/{employee_id}")
def get_employee(employee_id: int):
    # Placeholder implementation - replace with actual employee data retrieval logic
    return {"id": employee_id, "name": f"Employee {employee_id}"}

# 4. PUT /employees/{employee_id} - Update details of a specific employee
@app.put("/employees/{employee_id}")
def update_employee(employee_id: int, employee: dict):
    # Placeholder implementation - replace with actual employee update logic
    return {"id": employee_id, "name": employee["name"]}

# 5. DELETE /employees/{employee_id} - Delete a specific employee
@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int):
    # Placeholder implementation - replace with actual employee deletion logic
    return {"message": f"Employee {employee_id} deleted"}