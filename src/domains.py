from enum import Enum

class Domain(Enum):
    '''
    The definitive enumeration for all domains in use by the program.
    Use this enumeration rather than raw strings.
    '''
    
    CAR = "cars"
    JOB = "csjobs"
    FURNITURE = "furniture"
    HOUSING = "housing"
    JEWELRY = "jewelry"
    MOTORCYCLE = "motorcycles"
