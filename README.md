# analyze-csv-sql

Analyzes a CSV file and automatically generates a SQL Server `CREATE TABLE` statement inferred from the data. It inspects each column's values to detect the most appropriate SQL type and prints both a column summary and the ready-to-use DDL.

## Features

- Infers SQL types: `DATE`, `INT`, `FLOAT`, `VARCHAR(n)` — rounded up to the nearest 50
- Detects nullability based on empty or missing values
- Normalizes column names to safe SQL identifiers (lowercase, no special characters)
- Deduplicates column names automatically if duplicates exist after normalization
- Table name derived from the CSV filename

## Requirements

- Python 3.7 or higher
- [pandas](https://pandas.pydata.org/)

## Installation

```bash
pip install pandas
```

Or with a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate      # Windows
pip install pandas
```

## Usage

```bash
python analyze_csv.py <csv_file>
```

### Arguments

| Argument   | Description                  |
|------------|------------------------------|
| `csv_file` | Path to the CSV file to analyze |

### Example

```bash
python analyze_csv.py employees.csv
```

### Sample output

```
Column: 'EmployeeID' -> [employeeid] | Type: INT | Nullable: No | Max Length: N/A
Column: 'First Name' -> [first_name] | Type: VARCHAR(50) | Nullable: No | Max Length: 12
Column: 'Salary'     -> [salary]     | Type: FLOAT       | Nullable: Yes | Max Length: N/A
Column: 'HireDate'   -> [hiredate]   | Type: DATE        | Nullable: No | Max Length: N/A

-- SQL Server CREATE TABLE:
CREATE TABLE [employees] (
    [employeeid] INT NOT NULL,
    [first_name] VARCHAR(50) NOT NULL,
    [salary] FLOAT NULL,
    [hiredate] DATE NOT NULL
);
```

## Notes

- Date detection expects `MM/DD/YYYY` format.
- `VARCHAR` sizes are rounded up to the nearest multiple of 50 (minimum 50).
- The CSV must be UTF-8 encoded (BOM-aware via `utf-8-sig`).
