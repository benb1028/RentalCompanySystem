
import pymysql
from baseObject import baseObject


class unitList(baseObject):
    #this is the assignment
    def __init__(self):
        self.setupObject('Units')
        
    def verifyNew(self,n=0):
        self.errorList = []
        
        u = buildingList()
        u.getByField('UID',self.data[n]['UID'])
        if len(u.data) > 0:
            self.errorList.append("Unit ID already exists.")
        
        
        if len(self.data[n]['BID']) == 0:
            self.errorList.append("Building ID cannot be blank.")
        if len(self.data[n]['MonthlyCost']) == 0:
            self.errorList.append("Cost cannot be blank.")
        if len(self.data[n]['MaxOccupancy']) == 0:
            self.errorList.append("Max occupancy cannot be blank.")

        if len(self.errorList) > 0:
            return False
        else:
            return True
    def verifyChange(self,n=0):
        self.errorList = []
        
        u = unitList()
        u.getByField('UID',self.data[n]['UID'])
        #print(u.data)
        if len(u.data) > 0:
            print(self.data[n])
            print(u.data[0])
            if str(self.data[n]['UID']) != str(b.data[0]['UID']):
                self.errorList.append("Unit ID already exists.")
        
        if len(self.errorList) > 0:
            return False
        else:
            return True

    
    
    