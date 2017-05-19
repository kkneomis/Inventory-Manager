import os
import csv

def get_forecast_inserts(file):
    '''
    Compile all insert statements for a Forecast csv
    '''

    #string that will hold all out sql statements
    queries = ""

    # get the commodities
    line = get_commodity(file)
    # we don't want .csv extension
    queries += "INSERT INTO commodity(com_id, com_name) VALUES ('%s', '%s');\n" % (line[0], (" ").join(line[1:]).replace(".csv", ""))

    # get the CFG inserts
    for cfg in get_cfg(file):
        id = get_commodity(file)[0]
        queries +="INSERT INTO cfg(cfg_id, cfg_name, com_id, cfg_cost, expedite_cost, holding_cost, lead_time, forecast) VALUES ('%s', '%s', '%s', 50, 50,50,5,100);\n" % (cfg[0], cfg[1], id)

    ## get the weeks
    ## TODO find a way to only get the new weeks
    #for week in get_weeks(file):
        # print "INSERT INTO week(week_id) VALUES ('%s');" % (week)
        # queries += "INSERT INTO week(week_id) VALUES ('%s');\n" % (week)

    for line in get_forecast(file):
        queries += "INSERT INTO forecast(forecast_id, forecast_site, cfg_id, version_name, forecast_type) VALUES ('%s', '%s','%s', '%s', '%s');\n" % (
        line[0]  + "_" + line[2], line[1], line[0], line[2], line[3])

    # get entries
    for line in get_entries(file):
        weeks = get_weeks(file)
        for i in range(4, len(line)):
            forecast_id = line[0] + "_" + line[1] + "_" + line[2]
            if "#" in line[i]:
                value = 0
            else:
                value = line[i]
            # print "INSERT INTO entry(forecast_id, week_id, entry_value) VALUES ('%s', '%s',  %s);" % (forecaste_id, weeks[i-4], value)
            queries += "INSERT INTO entry(forecast_id, week_id, entry_value) VALUES ('%s', '%s',  %s);\n" % (
            forecast_id, weeks[i - 4], value)

    return queries



def get_costs(file):
    with open(file, 'rU') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)
        queries = ""
        for row in reader:
            queries += "Update cfg set cfg_cost=%s, expedite_cost=%s, holding_cost=%s, lead_time=%s, forecast=%s\
  where cfg_id='%s';\n" % (row[2], row[3], row[4], row[5], row[6], row[0] + "_" + row[1])
    return queries


def get_cfg(file):
    '''
    return the list of CFGs
    '''
    cfg_list = []
    with open(file, 'rU') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        next(spamreader, None)
        for row in spamreader:
            cfg = "%s_%s" % (row[0], row[1])
            cfg_list.append([cfg,row[0]])  #name_site, name

    return [list(i) for i in set(tuple(i) for i in cfg_list)] #returning a unique list of lists



def get_weeks(file):
    '''
    get the weeks in the file
    '''
    weeks=[]
    with open(file, 'rU') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        return reader.next()[4:]


def get_forecast(file):
    '''
    get the forecast lines
    '''
    forecasts=[]
    with open(file, 'rU') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)
        for row in reader:
            forecast=[]
            forecast.append("%s_%s" % (row[0], row[1])) #cfg_name
            forecast.append(row[1]) #site
            forecast.append(row[2]) #version
            # measure
            if 'Sales' in row[3]:
                forecast.append('actual')
            else:
                forecast.append('predicted')
            forecasts.append(forecast)
    return forecasts


def get_entries(file):
    '''
    get the entry values from csv
    '''
    entries = []
    with open(file, 'rU') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)
        for row in reader:
            entries.append(row)

    return entries

def get_commodity(file):
    '''
    get commodity info
    important!!!!!
    expects file to be named commodityId_CommodityName
    '''
    file = os.path.basename(file)
    return str(file).split('_')