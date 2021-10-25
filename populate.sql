 DROP TABLE IF EXISTS AZHousing;                                                    
 DROP TABLE IF EXISTS Motorcycles;                                                  
 DROP TABLE IF EXISTS CSJobs;                                                       
 DROP TABLE IF EXISTS Furniture;                                                    
 DROP TABLE IF EXISTS Jewelry;                                                      
 DROP TABLE IF EXISTS MelbHousing;                                                  
 DROP TABLE IF EXISTS Cars; 

CREATE TABLE AZHousing (
    Price VARCHAR(30),
    address VARCHAR(80),
    Local_area VARCHAR(30),
    zipcode VARCHAR(30),
    beds VARCHAR(30),
    baths VARCHAR(30),
    sqft VARCHAR(30),
    url TINYTEXT
);

LOAD DATA INFILE '/Users/student/cs/ng/Product-QA/Datasets/AZHousingData.csv'
INTO TABLE AZHousing
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

CREATE TABLE Motorcycles (
    name VARCHAR(80),
    selling_price VARCHAR(80),
    year VARCHAR(30),
    seller_type VARCHAR(30),
    owner VARCHAR(30),
    km_driven VARCHAR(30),
    ex_showroom_price VARCHAR(30)
);

LOAD DATA INFILE '/Users/student/cs/ng/Product-QA/Datasets/BIKE-DETAILS.csv'
INTO TABLE Motorcycles
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;
-- 
-- CREATE TABLE CSJobs ( 
--     job_id VARCHAR(50),
--     index_value VARCHAR(50),
--     Job_Title VARCHAR(255),
--     Salary_Estimate VARCHAR(60),
--     Job_Description TEXT,
--     Rating VARCHAR(30),
--     Company_Name VARCHAR(60),
--     Location VARCHAR(60),
--     Headquarters VARCHAR(80),
--     Size VARCHAR(50),
--     Founded VARCHAR(30),
--     Type_of_ownership VARCHAR(80),
--     Industry VARCHAR(80),
--     Sector VARCHAR(80),
--     Revenue VARCHAR(50),
--     Competitors VARCHAR(80),
--     Easy_Apply VARCHAR(30)
-- );
-- 
-- LOAD DATA INFILE '/Users/student/cs/ng/Product-QA/Datasets/DataScientist.csv'
-- INTO TABLE CSJobs
-- FIELDS TERMINATED BY ','
-- OPTIONALLY ENCLOSED BY '"'
-- LINES TERMINATED BY 'STOP\n'
-- IGNORE 1 ROWS;
-- 
CREATE TABLE Furniture (
    index_id VARCHAR(30),
    item_id VARCHAR(50),
    name VARCHAR(30),
    category VARCHAR(60),
    price VARCHAR(50),
    old_price VARCHAR(30),
    sellable_online VARCHAR(30),
    links VARCHAR(255),
    other_colors VARCHAR(80),
    short_description TEXT,
    designer TEXT,
    beds VARCHAR(50),
    baths VARCHAR(50),
    sqft VARCHAR(50)
);

LOAD DATA INFILE '/Users/student/cs/ng/Product-QA/Datasets/IKEA_SA_Furniture_Web_Scrapings_sss.csv'
INTO TABLE Furniture
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

CREATE TABLE Jewelry (
    ref VARCHAR(30),
    categorie VARCHAR(60),
    title VARCHAR(125),
    price VARCHAR(50),
    tags TINYTEXT,
    description TEXT,
    image VARCHAR(255)
);

LOAD DATA INFILE '/Users/student/cs/ng/Product-QA/Datasets/cartier_catalog.csv'
INTO TABLE Jewelry
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

CREATE TABLE MelbHousing (
    Suburb VARCHAR(60),
    Address VARCHAR(120),
    Rooms VARCHAR(50),
    Types VARCHAR(30),
    Price VARCHAR(50),
    Method VARCHAR(30),
    Dates VARCHAR(30),
    Distance VARCHAR(30),
    Postcode VARCHAR(30),
    Bedroom2 VARCHAR(30),
    Bathroom VARCHAR(30),
    Car VARCHAR(30),
    Landsize VARCHAR(30),
    BuildingArea VARCHAR(30),
    YearBuilt VARCHAR(30),
    CouncilArea VARCHAR(30),
    Lattitude VARCHAR(30),
    Longtitude VARCHAR(30),
    Regionname VARCHAR(30),
    Propertycount VARCHAR(30)
);

LOAD DATA INFILE '/Users/student/cs/ng/Product-QA/Datasets/melb_data.csv'
INTO TABLE MelbHousing
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

CREATE TABLE Cars (
    id VARCHAR(50),
    region VARCHAR(60),
    price VARCHAR(60),
    year VARCHAR(60),
    manufacturer VARCHAR(60),
    model VARCHAR(255),
    current_condition VARCHAR(60),
    cylinders VARCHAR(60),
    fuel VARCHAR(60),
    odometer VARCHAR(60),
    title_status VARCHAR(60),
    transmission VARCHAR(60),
    drive VARCHAR(60),
    sizes VARCHAR(60),
    types VARCHAR(60),
    paint_color VARCHAR(60),
    state VARCHAR(60)
);

LOAD DATA INFILE '/Users/student/cs/ng/Product-QA/Datasets/vehicles4.csv'
INTO TABLE Cars
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

