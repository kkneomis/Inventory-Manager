drop table if exists commodity;
create table commodity(
    com_id VARCHAR(255) NOT NULL,
    com_name VARCHAR(255) NOT NULL,
    PRIMARY KEY(com_id)
);

drop table if exists cfg;
create table cfg(
    cfg_name VARCHAR(255) PRIMARY KEY,
    com_id VARCHAR(255) NOT NULL,
    FOREIGN KEY (com_id) REFERENCES commodity(com_id)
);

drop table if exists forecast;
create table forecast(
    forecast_id VARCHAR(255) PRIMARY KEY,
    forecast_site VARCHAR(255) NOT NULL,
    cfg_name VARCHAR(255) NOT NULL,
    version_name VARCHAR(255) NOT NULL,
    forecast_type VARCHAR(255) NOT NULL,
    FOREIGN KEY (cfg_name) REFERENCES cfg(cfg_name)
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


INSERT INTO week(week_id) VALUES ('NovW117');
INSERT INTO week(week_id) VALUES ('NovW217');
INSERT INTO week(week_id) VALUES ('NovW317');
INSERT INTO week(week_id) VALUES ('NovW417');
INSERT INTO week(week_id) VALUES ('DecW117');
INSERT INTO week(week_id) VALUES ('DecW217');
INSERT INTO week(week_id) VALUES ('DecW317');
INSERT INTO week(week_id) VALUES ('DecW417');
INSERT INTO week(week_id) VALUES ('DecW517');
INSERT INTO week(week_id) VALUES ('JanW117');
INSERT INTO week(week_id) VALUES ('JanW217');
INSERT INTO week(week_id) VALUES ('JanW317');
INSERT INTO week(week_id) VALUES ('JanW417');
INSERT INTO week(week_id) VALUES ('JanW517');