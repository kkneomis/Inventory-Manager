# Inventory Manager Tool

This inventory management tool is built in python (flask) and sql. 

### Dependencies
Python
Flask
Sqlite3 (or some other relational database)

### Functionality

This tool intakes data in a waterfall format csv (see example files provided). It parses this data into a sql format that can then be queried to determine optimal inventory levels. 

It uses several jquery libraries to visualize the data being calculated. Although operations in this tool are done in raw sql for demonstration purpuses, an ORM such as sqlachemy can be used to ease the manipulation of sql data.
