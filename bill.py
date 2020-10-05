from datetime import date
import pymysql
from baseObject import baseObject


class billList(baseObject):
    # billList object for the Bills table
    def __init__(self):
        self.setupObject('Bills')
        
    def verifyNew(self,n=0):
        # check data for invalid entries, add any errors to errorList
        self.errorList = []
        if date.fromisoformat(self.data[n]['DateDue']) < date.today():
            self.errorList.append("Cannot be due before today.")
        if self.data[n]['AmntDue'] <= 0:
            self.errorList.append("Amount due must be greater than 0.")
        if len(self.errorList) > 0:
            return False
        else:
            return True

    
    
    