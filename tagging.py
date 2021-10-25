'''
Created on Oct 9, 2021

@author: Matthew Moulton
'''
from src.extract import DataExtractor

if __name__ == '__main__':
    # This program is intended to be used to help in the tagging process
    extractor = DataExtractor()
    extractor.userTag("tagging/queries_2tag.txt")
