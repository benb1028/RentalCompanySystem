from datetime import date, timedelta
import pymysql
from baseObject import baseObject
import re

class userList(baseObject):
    #this is the assignment
    def __init__(self):
        self.setupObject('Users')
        
    def verifyNew(self,n=0):
        self.errorList = []
        
        if self.hasDuplicates('Email', n):
            self.errorList.append("Email address is already registered.")
            
        if self.hasDuplicates('Username', n):
            self.errorList.append("Username already exists.")
            
        if len(self.data[n]['Username']) < 5 or len(self.data[n]['Username']) > 25:
            self.errorList.append("Username must be between 5 and 25 characters long.")
            
        if verifyEmail(self.data[n]['Email']) == False:
            self.errorList.append("Please enter a valid email.")
            
        pwErrors = verifyPassword(self.data[n]['Password'])
        if len(pwErrors) > 0:
            [self.errorList.append(err) for err in pwErrors]
            
        if verifyDOB(self.data[n]['Birthday'], minAge=18) == False:
            self.errorList.append("User must be at least 18 years old.")
        
        if verifyPhone(self.data[n]['Phone']) == False:
            self.errorList.append("Please enter a valid 10 digit phone number.")
        
        if len(self.data[n]['FirstName']) == 0:
            self.errorList.append("First name cannot be blank.")
            
        if len(self.data[n]['LastName']) == 0:
            self.errorList.append("Last name cannot be blank.")
            
        if self.data[n]['Type'] not in ['admin', 'landlord', 'tenant']:
            self.errorList.append("Invalid user type.")
        
  
        if len(self.errorList) > 0:
            return False
        else:
            return True
        
    def verifyChange(self,n=0):
        self.errorList = []
        
        u = userList()
        u.getByField('email',self.data[n]['email'])
        #print(u.data)
        if len(u.data) > 0:
            print(self.data[n])
            print(u.data[0])
            if str(self.data[n]['id']) != str(u.data[0]['id']):
                self.errorList.append("Email address is already registered.")
        
        
        if len(self.data[n]['fname']) == 0:
            self.errorList.append("First name cannot be blank.")
        if len(self.data[n]['lname']) == 0:
            self.errorList.append("Last name cannot be blank.")
        
        if len(self.errorList) > 0:
            return False
        else:
            return True
        
    def tryLogin(self,email,pw):    
        #SELECT * FROM `Users` WHERE `email` = 'b@a.com' AND `password` = '123'
        sql = 'SELECT * FROM `' + self.tn + '` WHERE `email` = %s AND `password` = %s;'
        tokens = (email,pw)
        self.connect()
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        #print(sql)
        #print(tokens)
        cur.execute(sql,tokens)
        self.data = []
        n=0
        for row in cur:
            self.data.append(row)
            n+=1
        if n > 0:
            return True
        else:
            return False
    
    def sortByManager(self, userID):
        u = userList()
        for user in self.data:
            if user['ManagedByUserID'] == userID:
                u.data.append(user)
        if len(u.data) > 0:
            return u
        else:
            return None
        
    def passMatch(self, Password2, n=0):
        if self.data[n]['Password'] == Password2:
            return True
        else:
            return False
        
    def hasDuplicates(self, field, n=0):
        u = userList()
        u.getByField(field, self.data[n][field])
        if len(u.data) > 0:
            return True
        else:
            return False
    
def hasNum(string):
    return any(char.isdigit() for char in string)

def hasChar(string):
    return any(char.isalpha() for char in string)
    
def verifyPassword(pw):
    errorList = []
    if len(pw) < 5:
        errorList.append("Password too short.")
    if len(pw) > 20:
        errorList.append("Password too long.")
    if not hasNum(pw):
        errorList.append("Password must contain at least one numeric digit.")
    if not hasChar(pw):
        errorList.append("Password must contain at least one letter.")
        
    return errorList

def verifyDOB(DOB, minAge):
    bday = date.fromisoformat(DOB)
    year = timedelta(days=365)
    minAgeDelta = year * minAge
    if bday + minAgeDelta > date.today():
        return False
    else:
        return True
    
def verifyPhone(num):
    if len(num) != 10:
        return False
    if not num.isdigit():
        return False
    else:
        return True
    
def verifyEmail(email):
    # regex obtained from https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if re.search(regex, email):
        return True
    else:
        return False