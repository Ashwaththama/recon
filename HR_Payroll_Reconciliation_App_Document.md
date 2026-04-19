# HR & Payroll Reconciliation App
## Technical Specification & Design Document

---

## 1. Purpose of This Document

This document explains what the HR & Payroll Reconciliation App does, how it is built, and how it works — written for someone with no background in software development. Technical terms are explained in plain language wherever they are used.

---

## 2. What the App Does (Plain English Summary)

Every organisation maintains two separate data systems:

- **HR System** — stores employee master data (names, departments, job grades, etc.)
- **Payroll System** — stores salary and payment data for employees

Over time, these two systems can fall out of sync. An employee might be terminated in HR but still active in Payroll, or a salary change might be updated in one system but not the other. Finding these mismatches manually — row by row across potentially thousands of records — is time-consuming and error-prone.

This app automates that process:

1. You upload your HR data file and your Payroll data file through a web page in your browser.
2. The app compares every record in both files using the Employee ID as the unique identifier.
3. It identifies three types of problems:
   - Employees present in HR but missing from Payroll
   - Employees present in Payroll but missing from HR
   - Employees present in both files but with different values in one or more fields
4. It produces a colour-coded Excel report summarising all discrepancies, which you download with one click.

---

## 3. How the App is Structured — The Two-Part Architecture

The app is split into two separate programs that work together:

```
┌─────────────────────────────────┐        ┌──────────────────────────────────┐
│           FRONTEND              │        │            BACKEND               │
│      (What you see and use)     │◄──────►│     (The engine / brain)         │
│      Runs in your browser       │        │     Runs on your computer        │
└─────────────────────────────────┘        └──────────────────────────────────┘
```

### The Frontend
Think of this as the **shop window** — the visual interface you interact with. It is built using a technology called **React**, which is a popular way to build interactive web pages. It runs entirely inside your web browser (Chrome, Edge, etc.) when you open `http://localhost:5173`.

It handles:
- Displaying the two file upload boxes
- Sending your files to the backend when you click "Run Reconciliation"
- Showing you a loading indicator while processing
- Offering you the completed Excel report as a download

### The Backend
Think of this as the **factory floor** — invisible to you, but doing all the actual work. It is built using **Python** (a programming language widely used for data tasks) and a framework called **FastAPI** (a tool for receiving and responding to requests over the internet). It runs in the background on your computer when you start the app.

It handles:
- Receiving the two uploaded files
- Reading and parsing them into rows and columns
- Performing the reconciliation comparison
- Building the Excel output report
- Sending the report back to your browser for download

---

## 4. How the Two Parts Talk to Each Other

When you click "Run Reconciliation", the following conversation happens between the frontend and backend — measured in milliseconds:

```
Your Browser (Frontend)                    Backend (Python)
        │                                        │
        │  "Here are two files.                  │
        │   Please reconcile them."              │
        │ ─────────────────────────────────────► │
        │                                        │  Reads HR file
        │                                        │  Reads Payroll file
        │                                        │  Compares records
        │                                        │  Builds Excel report
        │  "Here is your Excel file."            │
        │ ◄───────────────────────────────────── │
        │                                        │
   Download button appears
```

This type of communication — where one program sends a request and another responds — is called an **API call** (Application Programming Interface). The files travel as **multipart form data**, which is the same mechanism used when you attach a file to an email.

---

## 5. File Structure — What Each File Does

```
Recon/
├── start.bat                        ← Double-click to launch the whole app
│
├── backend/                         ← The Python engine
│   ├── main.py                      ← Entry point; starts the server and sets up security rules
│   ├── requirements.txt             ← List of Python libraries the app needs
│   ├── routers/
│   │   └── reconcile.py             ← Defines the single API endpoint (receiving point for files)
│   └── services/
│       ├── file_reader.py           ← Reads CSV and Excel files into memory as data tables
│       ├── reconciler.py            ← The core comparison logic — finds all discrepancies
│       └── excel_writer.py          ← Builds the formatted Excel output with colour highlights
│
└── frontend/                        ← The React web interface
    ├── vite.config.js               ← Configuration: routes browser requests to the backend
    ├── package.json                 ← List of JavaScript libraries the app needs
    └── src/
        ├── App.jsx                  ← Main page: manages state (which files chosen, loading, done)
        ├── App.css                  ← Visual styling: colours, fonts, layout
        ├── api/
        │   └── reconcileApi.js      ← Handles sending files to backend and receiving the report
        └── components/
            ├── DropZone.jsx         ← The file upload box (drag-and-drop area)
            ├── FileCard.jsx         ← Shows the name of a selected file with a remove button
            ├── ReconcileButton.jsx  ← The "Run Reconciliation" button
            ├── DownloadButton.jsx   ← The "Download Report" button that appears after processing
            └── StatusBanner.jsx     ← The message strip showing loading / success / error state
```

---

## 6. The Reconciliation Logic — Step by Step

This section explains exactly what the app does with your data once it receives the two files.

### Step 1 — Read and Clean the Files
The app reads both files (whether CSV or Excel format) into memory as structured tables — like spreadsheets held in RAM. It then:
- Trims any extra spaces from column names
- Locates the Employee ID column (it accepts variations like `Employee_ID`, `Emp_ID`, `Employee Id`)
- Converts all Employee IDs to plain text strings so that `E001` and `E001 ` (with a trailing space) are treated identically

### Step 2 — Sort Employees into Groups

```
HR employees:      {E001, E002, E003, E005}
Payroll employees: {E001, E002, E004}

Group A — HR only (missing from Payroll):   {E003, E005}
Group B — Payroll only (missing from HR):   {E004}
Group C — Present in both (to be compared): {E001, E002}
```

### Step 3 — Field-Level Comparison for Common Employees

For every employee in Group C, the app compares each column that exists in both files. Values are compared as plain text (case-insensitive) so `50000` and `50,000.00` would be treated as different, and `IT` and `it` would be treated as the same.

Example:

| Employee | Column   | HR Value | Payroll Value | Match? |
|----------|----------|----------|---------------|--------|
| E001     | Salary   | 50000    | 50000         | ✓      |
| E001     | Department | HR     | Human Resources | ✗ — Mismatch |
| E002     | Salary   | 60000    | 65000         | ✗ — Mismatch |

### Step 4 — Build the Discrepancy Report

All findings are assembled into the Excel output file described in the next section.

---

## 7. The Excel Output Report — Sheet by Sheet

The downloaded file `reconciliation_report.xlsx` contains four sheets:

### Sheet 1 — Summary
A one-page overview showing counts at a glance:

| Metric | Value |
|---|---|
| Total HR Records | 142 |
| Total Payroll Records | 139 |
| Matched (Common) Records | 136 |
| Missing in Payroll (HR only) | 6 |
| Missing in HR (Payroll only) | 3 |
| Field-Level Mismatches | 14 |
| Total Discrepancies | 23 |

### Sheet 2 — HR Only (Amber/Orange rows)
Lists every employee who appears in the HR file but has no corresponding record in the Payroll file. Each row includes all the HR data for that employee plus a plain-English description:

> *"Employee E003 exists in HR but has no matching record in Payroll."*

**Colour:** Amber (#FFC000) — signals caution; this employee may be receiving no pay despite being on HR records.

### Sheet 3 — Payroll Only (Red rows)
Lists every employee who appears in the Payroll file but has no corresponding record in the HR file. These are potential "ghost employees" — being paid but not recorded in HR.

> *"Employee E004 exists in Payroll but has no matching record in HR."*

**Colour:** Red (#FF4C4C) — signals high risk; payments may be going to someone no longer employed.

### Sheet 4 — Field Mismatches (Yellow rows)
Lists every individual field-level difference found between the two files for common employees. Each row identifies exactly which field is wrong and shows both values side by side:

| Employee_ID | Column_Name | HR_Value | Payroll_Value | Description |
|---|---|---|---|---|
| E002 | Salary | 60000 | 65000 | Employee E002: 'Salary' differs — HR has '60000', Payroll has '65000'. |
| E001 | Department | HR | Human Resources | Employee E001: 'Department' differs — HR has 'HR', Payroll has 'Human Resources'. |

**Colour:** Yellow (#FFFF00) — signals a data inconsistency requiring investigation.

All sheets have:
- **Bold header row** with a grey background
- **Frozen top row** so headers remain visible when scrolling
- **Auto-filter dropdowns** on every column for easy sorting and filtering
- **Auto-sized columns** for readability

---

## 8. Technologies Used — Plain English Glossary

| Technology | What it is | Why it was chosen |
|---|---|---|
| **Python** | A programming language particularly well-suited for data processing | Excellent libraries for reading Excel/CSV files and generating Excel output |
| **FastAPI** | A Python tool for building web APIs (receiving and responding to requests) | Fast, reliable, and generates interactive documentation automatically |
| **pandas** | A Python library for working with tabular data (like Excel in memory) | Industry standard for data comparison and manipulation |
| **openpyxl** | A Python library for reading and writing Excel files | Supports cell colours, formatting, and multiple sheets |
| **React** | A JavaScript library for building interactive web interfaces | Makes it easy to build responsive, component-based UIs |
| **Vite** | A tool that runs the React frontend during development | Fast and lightweight development server |
| **axios** | A JavaScript library for making HTTP requests from the browser | Handles file uploads and binary (Excel) downloads reliably |

---

## 9. Data Flow Diagram — End to End

```
User selects HR file           User selects Payroll file
        │                               │
        └───────────────┬───────────────┘
                        │
              Clicks "Run Reconciliation"
                        │
                        ▼
            reconcileApi.js packages both
            files into a single request
                        │
                        ▼
            POST /api/reconcile
            (sent to backend over HTTP)
                        │
                        ▼
            file_reader.py reads and
            cleans both files into tables
                        │
                        ▼
            reconciler.py compares records:
            ┌─ HR only employees
            ├─ Payroll only employees
            └─ Field-level mismatches
                        │
                        ▼
            excel_writer.py builds a
            formatted 4-sheet workbook
                        │
                        ▼
            Excel file sent back to browser
            as a downloadable binary response
                        │
                        ▼
            Download button appears in UI
                        │
                        ▼
            User clicks Download →
            reconciliation_report.xlsx
            saved to their computer
```

---

## 10. What the App Does NOT Do

It is important to be clear about the scope and limitations:

- **It does not modify your source files.** The HR and Payroll files you upload are read-only; nothing is written back to them.
- **It does not store your data.** Once the report is generated and sent to your browser, the data is cleared from memory. Nothing is saved to a database or disk.
- **It does not fix discrepancies.** The app identifies and reports differences; the decision of what to do with them rests with the user.
- **It does not connect to live HR or Payroll systems.** It works only with files you manually export from those systems and upload.
- **It is case-insensitive but not "fuzzy".** `IT` and `it` are treated as equal, but `IT Department` and `IT` are treated as different.

---

## 11. How to Run the App (Quick Reference)

1. Double-click `start.bat` in the `Recon` folder
2. Wait ~5 seconds for two terminal windows to open
3. Your browser will open automatically at `http://localhost:5173`
4. Upload your HR file and Payroll file
5. Click **Run Reconciliation**
6. Click **Download Reconciliation Report**
7. Open the downloaded Excel file

To stop the app: close both terminal windows.

---

*Document prepared: April 2026*
