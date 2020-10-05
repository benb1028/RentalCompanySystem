
import pymysql
from baseObject import baseObject


class unitList(baseObject):
    # object for Units table
    def __init__(self):
        self.setupObject('Units')
        
    def verifyNew(self,n=0):
        # check data for validity, append any errors to errorList
        self.errorList = []
        if self.hasDuplicates('Address1', n) and self.hasDuplicates('Address2', n):
            self.errorList.append("A unit at this address already exists.")
        if len(self.data[n]['Address1']) == 0:
            self.errorList.append("Address Line 1 cannot be blank.")
        if len(self.data[n]['Address2']) == 0:
            self.data[n]['Address2'] = None
        if self.data[n]['MaxOccupancy'] < 1:
            self.errorList.append("Max occupancy must be at least 1.")
        if self.data[n]['Bedrooms'] < 1:
            self.errorList.append("Must have at least one bedroom.")
        if self.data[n]['Bathrooms'] < 1:
            self.errorList.append("Must have at least one bathroom.")
        if self.data[n]['Area'] < 100:
            self.errorList.append("Area must be at least 100.")
        if self.data[n]['StdCost'] < 0:
            self.errorList.append("Monthly Rent must be positive.")
        if len(self.errorList) > 0:
            return False
        else:
            return True
    
    def hasDuplicates(self, field, n=0):
        # check db for entries with the same value at a field
        u = unitList()
        u.getByField(field, self.data[n][field])
        if len(u.data) > 0:
            return True
        else:
            return False
    