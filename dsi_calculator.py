import os
import csv
import json
import sqlite3
import load_csv as lc
import data_search as ds
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, \
    flash, g
from werkzeug import secure_filename


app = Flask(__name__)

# This is the path to the upload directory
my_dir = os.path.dirname(__file__)
app.config['UPLOAD_FOLDER'] = os.path.join(my_dir, 'uploads/')
app.config['SQL_FOLDER'] = os.path.join(my_dir, 'sql/')

# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = {'csv'}

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
))


# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    """
    :rtype: object
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def home():
    db = get_db()
    cur = db.execute('SELECT * FROM cfg')
    cfgs = cur.fetchall()

    all_sales_data = []

    for item in cfgs:
        cfg = item['cfg_name']
        all_sales_data.append(ds.actual_sales(cfg))

    print all_sales_data

    return render_template('index.html', sales=all_sales_data)


@app.route('/upload')
def upload_file():
    #myfile = lc.get_inserts(os.path.join(app.config['UPLOAD_FOLDER'], 'hdd_Hard_Drive.csv'))
    #print myfile
    files = make_tree(app.config['UPLOAD_FOLDER'])
    return render_template('upload.html', files=files)


@app.route('/data')
def show_data():
    db = get_db()
    cur = db.execute('SELECT * FROM commodity')
    commodities = cur.fetchall()
    cur = db.execute('SELECT * FROM cfg')
    cfgs = cur.fetchall()
    cur = db.execute('SELECT forecast.forecast_id, week.week_id, entry.entry_value \
                      FROM forecast, week, entry \
                      WHERE forecast.forecast_id = entry.forecast_id \
                      AND week.week_id = entry.week_id')
    entries = cur.fetchall()
    cur = db.execute('Select * from week')
    weeks = cur.fetchall()
    return render_template('data.html', commodities=commodities, cfgs=cfgs, entries=entries, weeks=weeks)


@app.route('/uploader', methods=['POST'])
def process_file():
    # Get the name of the uploaded file
    file = request.files['file']
    # Check if the file is one of the allowed types/extensions
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)
        # Move the file form the temporal folder to
        # the upload folder we setup
        try:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash("Your file was saved!")
        except:
            print 'File not valid.'
            pass

        try:
            sql = lc.get_inserts(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            sql_filename = filename.split('.')[0] + '.sql'
            with open(os.path.join(app.config['SQL_FOLDER'], sql_filename), 'w') as file:
                file.write(str(sql))

            init_db('sql/'+sql_filename)

            flash("Your data has been imported.")
        except:
            print "it did not work"
            flash('Loading sql from csv did not work :(...try again')


        # Redirect the user to the upload page
        return redirect(url_for('upload_file'))
    else:
        flash("Not a valid file format. Only CSV files are allowed.")
        return redirect(url_for('upload_file'))


# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# list the files which are in directories and subdirectories.
def make_tree(path):
    try:
        lst = os.listdir(path)
    except OSError:
        pass  # ignore errors
    else:
        return lst

    return []


@app.route('/commodity/<com_id>')
def commodity(com_id=''):
    db = get_db()
    cur= db.execute('select * from commodity')
    commodities = cur.fetchall()
    cur = db.execute('select * from commodity where com_id = (?)', [com_id])
    commodity = cur.fetchall()
    cur = db.execute('select * from cfg where com_id = ?', [commodity[0]['com_id']])
    cfgs = cur.fetchall()

    #this should instead be the logic for grouping DSI
    cur = db.execute('select * from cfg where length(cfg_name) < 14 and com_id = ?', [commodity[0]['com_id']])
    group1= cur.fetchall()
    cur = db.execute('select * from cfg where length(cfg_name) < 17 and \
                      length(cfg_name) > 14 and com_id = ?', [commodity[0]['com_id']])
    group2 = cur.fetchall()
    cur = db.execute('select * from cfg where length(cfg_name) > 17 and com_id = ?', [commodity[0]['com_id']])
    group3 = cur.fetchall()


    return render_template('commodity.html', commodity=commodity, \
                           commodities=commodities, cfgs=cfgs, \
                           group1=group1, group2=group2, group3=group3)


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


# database config
def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = dict_factory
    rv.text_factory = str
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def init_db(file):
    db = get_db()
    with app.open_resource(file, mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db('tables.sql')

    print 'Initialized the database.'


if __name__ == '__main__':
    app.run()
