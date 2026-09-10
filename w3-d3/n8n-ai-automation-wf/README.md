# n8n - ETL Automation (AI-Automation)

## 📌 Overview

This project demonstrates an **AI-powered ETL (Extract, Transform, Load) automation workflow built using n8n**.

The workflow processes student enrollment data uploaded through an n8n form. It extracts records from the uploaded file, processes records individually, uses an LLM to clean and validate the data, converts the AI-generated JSON into structured n8n JSON, applies business rules, and generates categorized Excel output files.

The workflow combines:

* 🤖 AI-powered data cleaning
* 🔄 Batch/item processing
* 💻 JavaScript transformation
* 🎯 Rule-based data validation
* 🔀 Conditional routing
* 📊 Excel file generation

---

# 🏗️ Architecture

```text
                    ┌──────────────────────┐
                    │  Student Upload Form │
                    │  n8n Form Trigger    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Extract from File   │
                    │  PDF / Excel / CSV   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Loop Over Items    │
                    │ Process Each Record  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Basic LLM Chain    │
                    │ AI Clean & Validate  │
                    └──────────┬───────────┘
                               │
                         OpenAI Model
                        GPT-4.1-mini
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Code in JavaScript   │
                    │ Parse JSON String    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Business Rule Flow  │
                    │ City / Email / Fee   │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
       Chennai Students   Valid Emails    Invalid Emails
              │                │                │
              ▼                ▼                ▼
          Excel File       Excel File       Excel File
```

---

# 🔄 Workflow Flow

The high-level workflow is:

```text
Upload
   ↓
Extract
   ↓
Loop Over Items
   ↓
Basic LLM Chain
   ↓
Code in JavaScript
   ↓
Business Rule Validation
   ↓
Conditional Routing
   ↓
Generate Excel Files
```

The workflow processes student records individually and applies AI transformation before downstream JavaScript parsing and conditional routing.

---

# 🧩 n8n Workflow Components

## 1. On Form Submission

The workflow starts with an **n8n Form Trigger**.

The form allows users to upload a file containing student enrollment data.

### Form Details

```text
Form Title:
Submit Fee Ack Form

Form Description:
Student Fee Ack Submission Form

Field:
Upload File Here
```

Supported input data can then be passed to the file extraction stage.

---

## 2. Extract from File

The **Extract from File** node reads data from the uploaded file.

The configured binary property is:

```text
Upload_File_Here
```

The purpose of this step is to convert the uploaded file into records that can be processed by the n8n workflow.

---

## 3. Loop Over Items

The **Loop Over Items** node processes the extracted student records.

This enables the workflow to process records individually.

For example:

```text
Student 1
    ↓
AI Processing
    ↓
JSON Conversion
    ↓
Continue

Student 2
    ↓
AI Processing
    ↓
JSON Conversion
    ↓
Continue

...

Student 50
    ↓
AI Processing
    ↓
JSON Conversion
```

This approach makes the workflow suitable for processing multiple rows from the uploaded source.

---

# 🤖 4. Basic LLM Chain

The **Basic LLM Chain** is responsible for cleaning and validating student enrollment records.

Each student record is passed to the LLM with transformation rules.

The AI is instructed to return:

```text
ONLY a JSON object
```

No explanation or Markdown should be returned.

## AI Processing Rules

### Name

Convert the name to:

```text
Title Case
```

Example:

```text
manoj k
```

Becomes:

```text
Manoj K
```

---

### Email Validation

If the email is invalid based on the defined validation rule, set:

```text
INVALID_EMAIL
```

Example:

```json
{
  "Email": "INVALID_EMAIL"
}
```

---

### Phone Validation

If the phone number:

* Contains fewer than 10 digits, or
* Is empty

Set:

```text
MISSING
```

---

### Course Validation

Allowed courses are:

```text
Python
Machine Learning
Data Science
```

---

### Fee Paid Conversion

The workflow converts values as follows:

```text
yes / YES  → true
no / NO    → false
```

Example:

```json
{
  "Fee_Paid": true
}
```

---

### City Transformation

City values are converted to:

```text
Title Case
```

If the value is empty:

```text
UNKNOWN
```

Example:

```text
CHENNAI
```

Becomes:

```text
Chennai
```

---

### Enrollment Date

The target format is:

```text
YYYY-MM-DD
```

Example:

```text
23-05-2025
```

Becomes:

```text
2025-05-23
```

---

# 🧠 5. OpenAI Chat Model

The Basic LLM Chain uses an OpenAI Chat Model.

Configured model:

```text
gpt-4.1-mini
```

The model is connected to the Basic LLM Chain as its AI language model.

The AI model is responsible for:

* Data normalization
* Name formatting
* Email validation
* Phone validation
* Course standardization
* Boolean conversion
* City normalization
* Date formatting

---

# 💻 6. Code in JavaScript

After AI processing, the LLM output is received in the `text` field as a JSON string.

Example input:

```json
{
  "text": "{\"Student_ID\":\"STU1001\",\"Name\":\"Manoj K\",\"Email\":\"INVALID_EMAIL\",\"Phone\":\"9876543210\",\"Course\":\"Python\",\"Fee_Paid\":true,\"City\":\"Chennai\",\"Enrolled_Date\":\"2025-05-23\"}"
}
```

The JavaScript Code node converts the JSON string into a clean JSON object.

## JavaScript Code

```javascript
// Get all incoming n8n items
const items = $input.all();

// Convert each item's "text" field from JSON string to JSON object
const output = items.map((item, index) => {

    try {
        // Parse the JSON string
        const student = JSON.parse(item.json.text);

        return {
            json: student
        };

    } catch (error) {

        // Return useful error information if JSON is invalid
        return {
            json: {
                error: true,
                row: index + 1,
                message: "Invalid JSON in text field",
                original_text: item.json.text,
                error_details: error.message
            }
        };
    }
});

return output;
```

## Clean Output Example

```json
{
  "Student_ID": "STU1001",
  "Name": "Manoj K",
  "Email": "INVALID_EMAIL",
  "Phone": "9876543210",
  "Course": "Python",
  "Fee_Paid": true,
  "City": "Chennai",
  "Enrolled_Date": "2025-05-23"
}
```

---

# 🎯 7. Business Rule Processing

After the JSON is cleaned and parsed, the workflow applies conditional business rules.

The workflow checks student data based on:

* City
* Email validity
* Fee payment status

---

## Chennai Check

The workflow checks:

```javascript
$json.City === "Chennai"
```

### True Branch

Students from Chennai are sent to:

```text
Students_In_Chennai
```

### False Branch

Students from other cities are sent to:

```text
Students_Not_In_Chennai
```

---

## Email Validation Check

The workflow checks whether:

```text
Email != INVALID_EMAIL
```

### Valid Email

Records are converted into:

```text
Students_With_Valid_MailId.xlsx
```

### Invalid Email

Records are converted into:

```text
Students_With_InValid_MailId.xlsx
```

---

## Fee Payment Rule

The workflow also contains a combined validation step for student records involving:

* Email validity
* Fee payment status

A qualifying output is generated as:

```text
Students_Chennai_ValidMail_FeeTrue.xlsx
```

---

# 📊 Generated Output Files

The workflow generates Excel files for categorized student records.

| Output                                    | Description                                        |
| ----------------------------------------- | -------------------------------------------------- |
| `Students_City_Chennai.xlsx`              | Students with City = Chennai                       |
| `Students_Not_In_Chennai.xlsx`            | Students with City other than Chennai              |
| `Students_With_Valid_MailId.xlsx`         | Students with valid email                          |
| `Students_With_InValid_MailId.xlsx`       | Students with invalid email                        |
| `Students_Chennai_ValidMail_FeeTrue.xlsx` | Records matching the combined validation condition |

---

# 📂 Sample Student Data

The source file can contain student information such as:

```json
{
  "Student_ID": "STU1001",
  "Name": "manoj k",
  "Email": "manojk@gmail",
  "Phone": "9876543210",
  "Course": "python",
  "Fee_Paid": "yes",
  "City": "Chennai",
  "Enrolled_Date": "23-05-2025"
}
```

After AI transformation:

```json
{
  "Student_ID": "STU1001",
  "Name": "Manoj K",
  "Email": "INVALID_EMAIL",
  "Phone": "9876543210",
  "Course": "Python",
  "Fee_Paid": true,
  "City": "Chennai",
  "Enrolled_Date": "2025-05-23"
}
```

---

# ⚙️ Prerequisites

Before running the workflow, configure:

## 1. n8n

An n8n instance is required to import and execute the workflow.

## 2. OpenAI Credentials

Configure OpenAI credentials in n8n for the Chat Model node.

The workflow uses:

```text
gpt-4.1-mini
```

## 3. Supported Input File

Upload a supported source file containing student data.

The workflow is configured to extract uploaded file data and process the resulting records.

---

# 🚀 How to Run

## Step 1: Import the Workflow

Download or clone this repository.

Open n8n and import:

```text
W3D3-ETL-Automation.json
```

---

## Step 2: Configure OpenAI Credentials

Open the:

```text
OpenAI Chat Model
```

node and configure your OpenAI credentials.

---

## Step 3: Verify File Extraction

Open the:

```text
Extract from File
```

node.

Verify that the binary property matches the uploaded form field:

```text
Upload_File_Here
```

---

## Step 4: Execute the Workflow

Open the form trigger and submit a student data file.

The workflow will:

```text
1. Receive the uploaded file
2. Extract student records
3. Process records through the loop
4. Send each record to the LLM
5. Clean and validate the data
6. Return structured JSON
7. Parse JSON using JavaScript
8. Apply conditional business rules
9. Generate categorized XLSX files
```

---

# 🔍 Error Handling

The JavaScript node includes JSON parsing error handling.

If an item contains invalid JSON, the workflow returns an error object such as:

```json
{
  "error": true,
  "row": 1,
  "message": "Invalid JSON in text field",
  "original_text": "invalid content",
  "error_details": "..."
}
```

This makes malformed AI output or unexpected input easier to identify during workflow execution.

---

# 🛠️ Technology Stack

```text
n8n
│
├── Form Trigger
├── Extract from File
├── Loop Over Items
├── Basic LLM Chain
├── OpenAI Chat Model
├── JavaScript Code Node
├── IF Nodes
└── Convert to File (XLSX)
```

---

# 🧠 Key Architecture Pattern

This project demonstrates a hybrid ETL pattern:

```text
Structured / Semi-Structured Input
            ↓
      File Extraction
            ↓
       Item Processing
            ↓
      AI Data Cleaning
            ↓
   Structured JSON Response
            ↓
   JavaScript Transformation
            ↓
 Deterministic Business Rules
            ↓
      Conditional Routing
            ↓
       Excel Outputs
```

The key design principle is:

> **Use AI for intelligent transformation and normalization, then use deterministic workflow logic for business-rule validation and routing.**

---

# ✨ Key Features

* ✅ Upload student data through an n8n form
* ✅ Extract records from uploaded files
* ✅ Process multiple records through a loop
* ✅ AI-based data cleaning and normalization
* ✅ OpenAI GPT-4.1-mini integration
* ✅ Structured JSON output
* ✅ JavaScript JSON parsing
* ✅ JSON error handling
* ✅ Email validation
* ✅ Phone validation
* ✅ Course normalization
* ✅ Fee status conversion
* ✅ City normalization
* ✅ Date formatting
* ✅ Conditional routing
* ✅ Chennai-based categorization
* ✅ Email-based categorization
* ✅ Fee-based validation
* ✅ Automated XLSX generation

---

# 🔮 Possible Enhancements

Future improvements could include:

* Add a dead-letter/error branch for failed records
* Store processed data in a database
* Add duplicate Student ID detection
* Add schema validation after LLM processing
* Add workflow execution notifications
* Send generated files through email
* Upload output files to cloud storage
* Add audit logging
* Add retry handling for AI/API failures
* Add data quality metrics
* Add workflow monitoring dashboards

---

# 📁 Repository Structure

```text
n8n-etl-ai-automation/
│
├── W3D3-ETL-Automation.json
│
├── README.md
│
└── assets/
    └── workflow-diagram.png
```

---

# 🎯 Use Cases

This architecture can be adapted for:

* Student enrollment processing
* Employee data cleansing
* Customer data validation
* Invoice processing
* CRM data normalization
* CSV/Excel ETL pipelines
* AI-assisted document processing
* Data migration workflows
* Data quality automation
* Enterprise workflow automation

---

# 👨‍💻 Author

**Dinesh Kumar**

**AI | Generative AI | Java Full Stack | AI Automation**

---

# 📄 License

This project is intended for learning, experimentation, and automation use cases. Add an appropriate license file based on your repository requirements.

---

## ⭐ If you find this project useful

Consider giving the repository a ⭐ and sharing it with developers interested in:

```text
AI Automation
n8n
ETL
Generative AI
OpenAI
Workflow Automation
Data Engineering
JavaScript
Enterprise AI
```
