def getStudentGrade(grade):
    try:
        if 90 <= grade <= 100:
            return "A"
        elif 80 <= grade <= 89:
            return "B"
        elif 70 <= grade <= 79:
            return "C"
        elif 60 <= grade <= 69:
            return "D"
        else:
            return "E"
    except TypeError:
        return "Invalid input: Grade must be a number."


try:
    mark = int(input("Enter the student's mark(0-100): "))
    print("Mark:", mark)
    print("Grade:", getStudentGrade(mark))
except ValueError:
    print("Invalid input: Please enter a valid number.")