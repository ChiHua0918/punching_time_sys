import module.connectDB as db

def employees():
    command = f"SELECT * FROM employee WHERE 1=1;"
    db.cursor.execute(command)
    result = db.cursor.fetchall()
    return result

def insertEmployee(employeeNumber):
    command =  f"INSERT INTO employee (employee_number) VALUES ('{employeeNumber}');"
    try:
        db.cursor.execute(command)
        db.connection.commit()
        return True
    except Exception as e:
        print("Error in insertEmployee:", e)
        return False