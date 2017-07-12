drop table if exists commodity;
create table commodity(
    com_id VARCHAR(255) NOT NULL,
    com_name VARCHAR(255) NOT NULL,
    PRIMARY KEY(com_id)
);

drop table if exists cfg;
create table cfg(
    cfg_id VARCHAR(255) PRIMARY KEY,
    cfg_name VARCHAR(255) NOT NULL,
    com_id VARCHAR(255) NOT NULL,
    cfg_cost DECIMAL(10,2) NOT NULL,
    expedite_cost DECIMAL(10,2) NOT NULL,
    holding_cost DECIMAL(10,2) NOT NULL,
    lead_time DECIMAL(10,2) NOT NULL,
    forecast INTEGER NOT NULL,
    FOREIGN KEY (com_id) REFERENCES commodity(com_id)
);

drop table if exists forecast;
create table forecast(
    forecast_id VARCHAR(255) PRIMARY KEY,
    forecast_site VARCHAR(255) NOT NULL,
    cfg_id VARCHAR(255) NOT NULL,
    version_name VARCHAR(255) NOT NULL,
    forecast_type VARCHAR(255) NOT NULL,
    FOREIGN KEY (cfg_id) REFERENCES cfg(cfg_id)
);

drop table if exists week;
create table week(
    week_id VARCHAR(255) PRIMARY KEY
);

drop table if exists entry;
create table entry(
    forecast_id VARCHAR(255) NOT NULL,
    week_id VARCHAR(255) NOT NULL,
    entry_value INTEGER NOT NULL,
    FOREIGN KEY (forecast_id) REFERENCES forecast(forecast_id),
    PRIMARY KEY (forecast_id, week_id)
);


