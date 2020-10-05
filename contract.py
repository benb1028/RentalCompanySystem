from datetime import date
import pymysql
from baseObject import baseObject


class contractList(baseObject):
    # contract list object for Contracts table
    def __init__(self):
        self.setupObject('Contracts')
        
    def verifyNew(self,n=0):
        # check data for errors, append errors to errorList
        self.errorList = []
        if date.fromisoformat(self.data[n]['EndDate']) < date.today():
            self.errorList.append("Contract cannot end on past dates.")
        if date.fromisoformat(self.data[n]['EndDate']) < date.fromisoformat(self.data[n]['StartDate']):
            self.errorList.append("End Date must be after Start Date")
        if self.data[n]['MonthlyCharge'] < 0:
            self.errorList.append("Monthly charge must be at least $0.00")  
        if len(self.errorList) > 0:
            return False
        else:
            return True
        
        

    
    
    

    

