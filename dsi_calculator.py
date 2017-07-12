import os
import math
import statistics
import sqlite3
import load_csv as lc
import numpy as np
import json
from scipy.stats import norm
import requests
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

    return render_template('index.html', sales=[])


@app.route('/upload')
def upload_file():
    '''
    Upload a csv file
    Expects a file with waterfall forecast data
    '''
    files = make_tree(app.config['UPLOAD_FOLDER'])
    return render_template('upload.html', files=files)


@app.route('/data')
def show_data():
    '''
    Show commodities and CFGs present in the database
    '''
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

        if "cost" in filename:
            # how to handle cost data files
            sql = lc.get_costs(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            # how to handle forecast files
            sql = lc.get_forecast_inserts(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        try:
            # create sql file and execute sql entries
            sql_filename = filename.split('.')[0] + '.sql'
            with open(os.path.join(app.config['SQL_FOLDER'], sql_filename), 'w') as file:
                file.write(str(sql))

            print "Executing sql..."
            init_db('sql/'+sql_filename, by_line=True)
            flash("Your data has been imported.")
        except:
            print "Failed to import sql from csv"
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
    """
    This route is expecting a parameter containing the name
    of a file. Then it will locate that file on the upload
    directory and show it on the browser, so if the user uploads
    an image, that image is going to be show after the upload
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


def make_tree(path):
    """list the files which are in directories and subdirectories."""
    try:
        lst = os.listdir(path)
    except OSError:
        pass  # ignore errors
    else:
        return lst

    return []


@app.route('/cfg')
def cfg(cfg_id="FP_S2240T_R_CFG_LAX_Site", lead_time="35", service_level="95", forecast="700"):
    """
    Take in a cfg and output inventory level and dsi
    """

    # getting new parameters from the url
    # the come as tuples
    if request.args.get('cfg_id'):
        cfg_id = request.args.get('cfg_id')
        lead_time = request.args.get('lead_time'),
        service_level = request.args.get('service_level'),
        forecast = request.args.get('forecast')

    # get the list of cfgs so that we can choose
    db = get_db()
    cur = db.execute('SELECT * FROM cfg')
    cfgs = cur.fetchall()
    # get the corresponding cfg
    cur = db.execute('SELECT * FROM cfg where cfg_id=?', [cfg_id])
    current_cfg = cur.fetchall()

    commodity = current_cfg[0]['com_id']
    # perform the calculations
    stat_values = get_cfg_stats(cfg_id, int(lead_time[0]), service_level[0], int(forecast))
    graph_data = ds.actual_sales(cfg_id)

    # we want to visualize our recommendation
    # this allows us to graph the recommended inventory level
    for item in graph_data:
        item['rec_inventory'] = int(stat_values['inventory'])

    return render_template('cfg.html', cfgs=cfgs, stat_values=stat_values, graph_data=graph_data)


def get_cfg_stats(cfg_id, lead_time, service_level, forecast):
    """
    Take in a cfg and some parameters
    This is where the math for the formula is done
    Return a dictionary including inventory and dsi
    """
    # first we get the data we need from the database
    db = get_db()
    cur = db.execute('SELECT entry.entry_value FROM entry, forecast \
                          WHERE forecast.forecast_id = entry.forecast_id  \
                          AND forecast.cfg_id == (?) \
                          AND forecast.forecast_type == "actual";', [cfg_id])
    entries = cur.fetchall()
    # here we are doing the actual calculations
    cfg_values = get_list_dict_values(entries, 'entry_value')

    stat_values = {'cfg_id': cfg_id,
                   'service_level': float(service_level) / 100,
                   'lead_time': int(lead_time),
                   'forecast': int(forecast)}

    try:
        stat_values['stv_dev'] =  statistics.pstdev(cfg_values)/5
        stat_values['avg_demand'] = (sum(cfg_values)/len(cfg_values))/5
        stat_values['total_demand'] = sum(cfg_values)/5
        stat_values['safety_stock'] =  ((stat_values['stv_dev']  \
                                       * norm.ppf(stat_values['service_level']) \
                                       * (math.sqrt(stat_values['lead_time'])+1))  \
                                       + (stat_values['avg_demand']*(stat_values['lead_time']+1)))/5
        stat_values['inventory'] = stat_values['safety_stock'] + stat_values['forecast']
        stat_values['reorder'] = (stat_values['avg_demand'] * (stat_values['lead_time']+5) \
                                 + norm.ppf(stat_values['service_level']) * stat_values['stv_dev'] \
                                 * (math.sqrt(stat_values['lead_time']) + 5))/5
        stat_values['dsi'] = stat_values['inventory']/stat_values['forecast']
    except:
        # if the math fails, we'll set everything so 0 to avoid an errors
        stat_values['stv_dev'] = 0
        stat_values['avg_demand'] = 0
        stat_values['total_demand'] = 0
        stat_values['safety_stock'] = 0
        stat_values['inventory'] = 0
        stat_values['reorder'] = 0
        stat_values['dsi'] = 0
        print "Something went wrong in executing our formula"

    return stat_values




@app.route('/cfg_vars', methods=['POST'])
def cfg_vars():
    """
    get methods from cfg form
    this is called when the form on the cfg page is called
    """
    cfg_id =  request.form['cfg_id']
    lead_time = request.form['lead_time']
    service_level = request.form['service_level']
    forecast = request.form['forecast']

    return redirect(url_for('cfg',
                            cfg_id = cfg_id,
                            lead_time = lead_time,
                            service_level = service_level,
                            forecast = forecast
                            ))


def get_list_dict_values(entries, key):
    """
    input is a list of key pair values
    :return: list of values
    turn output of a sql query into a normal list
    """
    cfg_values = []
    for entry in entries:
        cfg_values.append(entry[key])
    return cfg_values


def get_service_level(cfg, commodity):
    """
    both inputs should be strings
    return service of a cfg based on percentage of cost
    eg. top 85%:high, next 15%: medium, bottom 15%:low
    """
    db = get_db()
    cur = db.execute('select cfg_cost from cfg where com_id=?', [commodity])
    all_commodity_costs = get_list_dict_values(cur.fetchall(), 'cfg_cost')
    cur = db.execute('select cfg_cost from cfg where cfg_id=?', [cfg])
    cfg_cost = cur.fetchall()[0]['cfg_cost']

    a = np.array(all_commodity_costs)
    if cfg_cost > np.percentile(a, 20):
        return 83
    elif cfg_cost > np.percentile(a, 5):
        return 95
    else:
        return 99



@app.route('/commodity/<com_id>')
def commodity(com_id=''):
    db = get_db()
    cur= db.execute('select * from commodity')
    commodities = cur.fetchall()
    cur = db.execute('select * from commodity where com_id = (?)', [com_id])
    commodity = cur.fetchall()

    # this should instead be the logic for grouping DSI
    cur = db.execute('select * from cfg where com_id = ?', [commodity[0]['com_id']])
    cfgs= cur.fetchall()

    dsi_dict = {}

    # creating key value pairs of cfg:dsi for categorization on the front end
    for cfg in cfgs:
        service_level = get_service_level(cfg['cfg_id'], commodity[0]['com_id'])
        cfg['service_level'] = service_level
        result =  get_cfg_stats(cfg['cfg_id'], cfg['lead_time'], service_level, cfg['forecast'])
        dsi_dict[cfg['cfg_id']] = [result['dsi'],cfg]

    #print json.dumps(dsi_dict, sort_keys=True, indent = 4, separators = (',', ': '))
    return render_template('commodity.html', commodity=commodity, \
                           commodities=commodities, \
                           dsi_dict = dsi_dict)


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


def init_db(file='tables.sql', by_line=False):
    """reset the database"""
    db = get_db()
    with app.open_resource(file, mode='r') as f:
        if by_line:
            for line in f.readlines():
                try:
                    db.cursor().executescript(line)
                    db.commit()
                except Exception as e:
                    print e
                    print "There was an error executing the line: %s" % line
        else:
            db.cursor().executescript(f.read())
            db.commit()




@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print 'Initialized the database.'


@app.route('/initdb_from_page', methods=['POST'])
def initdb_from_page():
    """Initializes the database from the GUI."""
    init_db()
    return redirect(url_for('upload_file'))

if __name__ == '__main__':
    app.run()
