
import pymysql
from baseObject import baseObject
from user import userList


class transactionList(baseObject):
    #this is the assignment
    def __init__(self):
        self.setupObject('Transactions')
        
    def verifyNew(self,n=0):
        self.errorList = []
        
        t = transactionList()
        t.getByField('TID',self.data[n]['TID'])
        if len(t.data) > 0:
            self.errorList.append("Transaction ID already exists.")
        
        
        if self.data[n]['Amnt'] <= 0:
            self.errorList.append("Amount must be greater than 0.")
        if self.data[n]['Type'] != 0 and self.data[n]['Type'] != 1:
            self.errorList.append("Type must be 1 or 2.")
        u1 = userList()
        u1.getById(self.data[n]['FromUser'])
        if len(u1.data['UserID']) == 0:
            self.errorList.append("Sending user does not exist.")
        u2 = userList()
        u2.getById(self.data[n]['ToUser'])
        if len(u2.data['UserID']) == 0:
            self.errorList.append("Receiving user does not exist.")
        #Add if statements for validation of other fields
  
        if len(self.errorList) > 0:
            return False
        else:
            return True
        
        
    def verifyChange(self,n=0):
        self.errorList = []
        
        t = transactionList()
        t.getByField('TID',self.data[n]['TID'])
        #print(t.data)
        if len(t.data) > 0:
            print(self.data[n])
            print(t.data[0])
            if str(self.data[n]['TID']) != str(t.data[0]['TID']):
                self.errorList.append("Transaction ID already exists.")
        
        if len(self.errorList) > 0:
            return False
        else:
            return True

    
    
    
