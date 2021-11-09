# Product-QA
A question answer system that spans across several product categories. Users provide some request query for a product or listing in one of the six categories. In response, the program finds matches to the query and returns results to the user. The program utilizes exact and partial matching techniques to produce as relevant an output as possible.

## Datasets 
Files have been entered into the "Datasets" directory. There are currently 6 categories available: Cars, Data Science Jobs, Furniture, Housing, Jewelry, and Motorcycles.

The data files in this repository are in the public domain.

## Set up
The main.py program in the src directory loads the product question answer program for some given query. However, before it is used, the SQLite database needs to be created. The script load_db.py has been provided to acheive this purpose.
