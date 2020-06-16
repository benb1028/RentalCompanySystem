
import pymysql
from baseObject import baseObject
from user import userList


class relationList(baseObject):
    #this is the assignment
    def __init__(self):
        self.setupObject('Relationships')
        
    def verifyNew(self,n=0):
        self.errorList = []
        
        r = relationList()
        r.getByField('RID',self.data[n]['RID'])
        if len(t.data) > 0:
            self.errorList.append("Relationship ID already exists.")
        
        
        if self.data[n]['Amnt'] <= 0:
            self.errorList.append("Amount must be greater than 0.")
        if self.data[n]['RType'] != 0 and self.data[n]['RType'] != 1:
            self.errorList.append("Type must be 1 or 2.")
        u1 = userList()
        u1.getById(self.data[n]['UserID'])
        if len(u1.data['UserID']) == 0:
            self.errorList.append("User does not exist.")
        u2 = unitList()
        u2.getById(self.data[n]['UnitID'])
        if len(u2.data['UnitID']) == 0:
            self.errorList.append("Unit does not exist.")
        #Add if statements for validation of other fields
  
        if len(self.errorList) > 0:
            return False
        else:
            return True
        
        
    def verifyChange(self,n=0):
        self.errorList = []
        
        r = relationList()
        r.getByField('RID',self.data[n]['RID'])
        #print(r.data)
        if len(r.data) > 0:
            print(self.data[n])
            print(r.data[0])
            if str(self.data[n]['RID']) != str(r.data[0]['RID']):
                self.errorList.append("Relation ID already exists.")
        
        if len(self.errorList) > 0:
            return False
        else:
            return True

    
    
    

    

