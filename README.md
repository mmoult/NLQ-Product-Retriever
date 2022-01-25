# Product-QA
A question answer system that spans across several product categories. Users provide some request query for a product or listing in one of the six categories. In response, the program finds matches to the query and returns results to the user. The program utilizes exact and partial matching techniques to produce as relevant an output as possible.

## Datasets 
Files have been entered into the "Datasets" directory. There are currently 6 categories available: Cars, Data Science Jobs, Furniture, Housing, Jewelry, and Motorcycles.

The data files in this repository are in the public domain.

## Set up
The main.py program in the src directory loads the product question answer program for some given query. However, before it is used, the SQLite database needs to be created. The script `load_db.py` has been provided to acheive this purpose.

## Dependencies
There are some dependencies required to run the main module. These include NLTK, Pandas, spaCy, and Scikit-Learn. You may install via pip by:
```bash
python -m pip install nltk
python -m pip install pandas
python -m pip install spacy
python -m pip install sklearn
```

Furthermore, once NLTK is installed, some corpora need to be downloaded. This can be performed by launching Python and entering:
```python
import nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
```

## Run
Run the `main.py` module, and specify the user query as the first argument to the program. The query will be classified as one of the six categories, be spell corrected, and will be analyzed for relevant product information. Matching or closely related products will be printed in the retrieved list.

### Flags
  Name	|  Effect
--------|-------------------------------:
-v | Print verbose output for the process (defaults to non-verbose).
-l <i>x</i> | Limit the number of products returned to no more than x (defaults to 25 for partial, no limit for exact).
-e | Returns only exact matches to the specifications extracted from the user query, skipping any partial match recommendations (defaults partial on).

