

import pymysql
from baseObject import baseObject


class buildingList(baseObject):
    #this is the assignment
    def __init__(self):
        self.setupObject('Buildings')
        
    def verifyNew(self,n=0):
        self.errorList = []
        
        b = buildingList()
        b.getByField('BID',self.data[n]['BID'])
        if len(b.data) > 0:
            self.errorList.append("Building ID already exists.")
        
        
        if len(self.data[n]['Address']) == 0:
            self.errorList.append("Address cannot be blank.")
        if len(self.data[n]['MonthlyCost']) == 0:
            self.errorList.append("Cost cannot be blank.")
        #Add if statements for validation of other fields
  
        if len(self.errorList) > 0:
            return False
        else:
            return True
    def verifyChange(self,n=0):
        self.errorList = []
        
        b = buildingList()
        b.getByField('BID',self.data[n]['BID'])
        #print(b.data)
        if len(b.data) > 0:
            print(self.data[n])
            print(b.data[0])
            if str(self.data[n]['BID']) != str(b.data[0]['BID']):
                self.errorList.append("Building ID already exists.")
        
        if len(self.errorList) > 0:
            return False
        else:
            return True

    
    
    