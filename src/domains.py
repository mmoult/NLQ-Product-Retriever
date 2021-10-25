from enum import Enum
from src.database import *

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

def getTable(domain:Domain) -> Table:
    if domain == Domain.MOTORCYCLE:
        return motorcycles
    elif domain == Domain.JEWELRY:
        return jewelry
    elif domain == Domain.JOB:
        return jobs
    elif domain == Domain.FURNITURE:
        return furniture
    elif domain == Domain.HOUSING:
        return housing
    elif domain == Domain.CAR:
        return cars
    else:
        return None
