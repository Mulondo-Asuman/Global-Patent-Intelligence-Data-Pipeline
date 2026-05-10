# Cloud Assignment Project

This repository contains a patent data analysis and visualization project. Below is an overview of the folder structure and what each component contains.

## Project Structure

```
cloud_assignmnet/
├── requirements.txt                 # Python dependencies for the project
├── Clean-Data-Files/               # Processed and cleaned data files
│   ├── clean_companies.csv         # Cleaned company/assignee data
│   ├── clean_inventors.csv         # Cleaned inventor information
│   ├── clean_patents.csv           # Cleaned patent records
│   └── clean_relationships.csv     # Cleaned patent-inventor relationships
├── Code-files/                     # Source code for data processing and analysis
│   ├── Python-Scripts/             # Python scripts and notebooks
│   │   └── index.ipynb             # Jupyter notebook for data exploration
│   └── SQL-Scripts/                # Database-related Python scripts
│       ├── create_database.py      # Script to create database schema
│       ├── generate_reports.py     # Report generation utilities
│       └── load_data_to_database.py # Data loading script
├── Data-Source/                    # Raw data files from patent database
│   ├── g_application.tsv           # Application data
│   ├── g_assignee_disambiguated.tsv # Disambiguated assignee information
│   ├── g_inventor_disambiguated.tsv # Disambiguated inventor data
│   ├── g_location_disambiguated.tsv # Location data
│   ├── g_patent_abstract.tsv       # Patent abstract text
│   └── g_patent.tsv                # Core patent information
├── Database/                       # Database schema and configuration
│   └── schema.sql                  # SQL schema definition
├── Saved_Files/                    # Generated output files
│   ├── country_trends.csv          # Country-wise patent trends
│   ├── patent_report.json          # JSON report data
│   ├── top_companies.csv           # Top patent-holding companies
│   ├── top_inventors.csv           # Top inventors by patent count
│   └── Visuals/                    # Generated visualizations

```

## Folder Descriptions

### Clean-Data-Files/
Contains processed and cleaned versions of the patent data. These CSV files have been transformed from the raw TSV sources and are ready for analysis or database loading.

### Code-files/
Houses all the source code for the project:
- **Python-Scripts/**: Contains Jupyter notebooks for interactive data exploration
- **SQL-Scripts/**: Python scripts that handle database operations, report generation, and data loading

### Data-Source/
Raw data files obtained from the patent database. These are tab-separated value (TSV) files containing the original patent information before any processing.

### Database/
Contains the database schema definition in SQL format, used to create the database structure for storing patent data.

### patent_site/
A Django web application for visualizing and interacting with the patent data:
- Built using Django framework
- Includes a dashboard app for displaying patent analytics
- Uses SQLite as the database backend
- Contains HTML templates for the web interface

### Saved_Files/
Output directory containing generated reports and visualizations:
- CSV files with aggregated data (trends, top entities)
- JSON reports for programmatic access
- Visuals/ subdirectory for charts and graphs

### scratch/
Temporary workspace for intermediate files and experimentation. Contents may be cleaned up periodically.

## Getting Started

1. Install dependencies: `pip install -r requirements.txt`
2. Set up the database: Run the scripts in `Code-files/SQL-Scripts/`
3. Launch the web application: Navigate to `patent_site/` and run `python manage.py runserver`

## Data Flow

1. Raw data is processed from `Data-Source/` TSV files
2. Cleaned data is stored in `Clean-Data-Files/` CSV files
3. Data is loaded into the database using scripts in `Code-files/SQL-Scripts/`
4. Reports and visualizations are generated and saved in `Saved_Files/`
5. The Django application in `patent_site/` provides a web interface for data exploration


## Online url 
Network URL: http://10.16.2.102:8501