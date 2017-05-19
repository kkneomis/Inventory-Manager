# Inventory Manager Tool

This inventory management tool is built in python (flask) and sql. 

### Dependencies
1. Python
2. Flask
3. Sqlite3 (or some other relational database)

### Functionality

This tool intakes data in a waterfall format csv (see example files provided). It parses this data into a sql format that can then be queried to determine optimal inventory levels. 

It uses several jquery libraries to visualize the data being calculated. Although operations in this tool are done in raw sql for demonstration purpuses, an ORM such as sqlachemy can be used to ease the manipulation of sql data.

###  Getting Started

    export FLASK_APP=dsi_calculator.py
    flask run

The app will run on your localhost port 5000 unless you specify otherwise in the dsi_calculator.py. You will most likely have to do so on a corporate network.

### Notes

Be sure that your input files are in csv and not in xls format. 

```load_csv.py``` contains many of the functions that convert the inputs from csv to sql.
```data_search.py``` converts sql data to correct json to be visualized in on javascript. 

