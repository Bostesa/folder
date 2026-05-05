
your_project_folder/
│
├── app.py                 # main entry point
├── utils.py               # shared database and decorator tools
│
├── blueprints/            # router (functionality) files
│   ├── auth.py
│   ├── dashboard.py
│   └── directory.py
│
└── templates/             # HTML files (Jinja2 templates)
    ├── layout.html
    ├── login.html
    ├── dashboard.html
    ├── customers.html
    ├── vehicles.html
    ├── sales.html
    ├── services.html
    ├── loans.html
    ├── accounting.html
    ├── reports.html
    ├── admin_users.html
    ├── admin_divisions.html
    ├── admin_departments.html
    └── ...

Notes:
- Python must be in the path
- Easiest environment is installing miniconda
    - it comes with latest python
- installation of flask and mysql-connector is required
    >> pip install Flask mysql-connector-python
- run the server (app.py)
- access the webpages in browser using:
    - http://127.0.0.1:8000/
    - http://localhost:8000/
- login uses the `User` and `Role` tables from CarCompanyDB
- import ../dropDDL.sql, ../createDDL.sql, and ../loadAll.sql before running the app
- the database information is in utils.py
    - the info can be modified accordingly