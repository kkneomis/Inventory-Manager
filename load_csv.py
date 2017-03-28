import os
import csv

def get_inserts(file):
    '''
    Compile all insert statements for a given document
    '''

    queries = ""

    # get the commodities
    line = get_commodity(file)
    # we don't want .csv extension
    # print "INSERT INTO commodity(com_id, com_name) VALUES ('%s', '%s');" % (line[0], line[1].split('.')[0])
    queries += "INSERT INTO commodity(com_id, com_name) VALUES ('%s', '%s');\n" % (line[0], (" ").join(line[1:]).replace(".csv", ""))

    # get the CFG inserts
    for cfg in get_cfg(file):
        id = get_commodity(file)[0]
        # print "INSERT INTO cfg(cfg_name, com_id) VALUES ('%s', '%s');" % (cfg, id)
        queries += "INSERT INTO cfg(cfg_name, com_id) VALUES ('%s', '%s');\n" % (cfg, id)

    # get the weeks
    # TODO find a way to only get the new weeks
    #for week in get_weeks(file):
        # print "INSERT INTO week(week_id) VALUES ('%s');" % (week)
     #   queries += "INSERT INTO week(week_id) VALUES ('%s');\n" % (week)

    for line in get_forecast(file):
        # print "INSERT INTO forecast(forecast_id, cfg_name, version_name, forecast_type) VALUES ('%s','%s', '%s', '%s');" % (line[0]+"_"+line[1],line[0], line[1], line[2])
        queries += "INSERT INTO forecast(forecast_id, cfg_name, version_name, forecast_type) VALUES ('%s','%s', '%s', '%s');\n" % (
        line[0] + "_" + line[1], line[0], line[1], line[2])

    # get entries
    for line in get_entries(file):
        weeks = get_weeks(file)
        for i in range(4, len(line)):
            forecaste_id = line[0] + "_" + line[2]
            if "#" in line[i]:
                value = 0
            else:
                value = line[i]
            # print "INSERT INTO entry(forecast_id, week_id, entry_value) VALUES ('%s', '%s',  %s);" % (forecaste_id, weeks[i-4], value)
            queries += "INSERT INTO entry(forecast_id, week_id, entry_value) VALUES ('%s', '%s',  %s);\n" % (
            forecaste_id, weeks[i - 4], value)

    return queries


def get_cfg(file):
    '''
    print the list of CFGs
    '''
    cfg_list = []
    with open(file, 'rU') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        next(spamreader, None)
        for row in spamreader:
            cfg_list.append(row[0])

    return list(set(cfg_list))



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
            forecast.append(row[0])
            forecast.append(row[2])
            if 'Sales' in row[3]:
                forecast.append('actual')
            else:
                forecast.append('predicted')
            forecasts.append(forecast)
    return forecasts


def get_entries(file):
    '''
    get the entry values
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
    expects file to be named comid_Commodity Name
    '''
    file = os.path.basename(file)
    return str(file).split('_')