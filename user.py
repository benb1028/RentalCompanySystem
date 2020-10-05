from datetime import date, timedelta
import pymysql
from baseObject import baseObject
import re
from contract import contractList

class userList(baseObject):
    # list object for User table
    def __init__(self):
        self.setupObject('Users')
        
    def verifyNew(self,n=0):
        # check data for errors, append any errors to errorList
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
        
        
    def tryLogin(self,email,pw):    
        # attempt to login with email and password
        sql = 'SELECT * FROM `' + self.tn + '` WHERE `email` = %s AND `password` = %s;'
        tokens = (email,pw)
        self.connect()
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        self.log(sql,tokens)
        cur.execute(sql,tokens)
        self.data = []
        for row in cur:
            self.data.append(row)
        if len(self.data) == 1: # return true if there is exactly one match
            return True
        else:
            return False
    
    def getTenants(self, username):
        # get a list of tenants that have a contract with username
        if getUserType(username) == 'landlord':
            c = contractList()
            c.getByField('LUserName', username)
            tenantUsernames = [contract['TUserName'] for contract in c.data]
            self.getManyByField('Username', tenantUsernames)
            
            
    def passMatch(self, Password2, n=0):
        # compare password in data with different password
        if self.data[n]['Password'] == Password2:
            return True
        else:
            return False
        
    def hasDuplicates(self, field, n=0):
        # find if there is another entry with the same value at field
        u = userList()
        u.getByField(field, self.data[n][field])
        if len(u.data) > 0:
            return True
        else:
            return False
    
def hasNum(string):
    # true if there is at least one number
    return any(char.isdigit() for char in string)

def hasChar(string):
    # true if there is at least ione character
    return any(char.isalpha() for char in string)
    
def verifyPassword(pw):
    # check password against defined criteria
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
    # check DOB to confirm age above minAge
    bday = date.fromisoformat(DOB)
    year = timedelta(days=365)
    minAgeDelta = year * minAge
    if bday + minAgeDelta > date.today():
        return False
    else:
        return True
    
def verifyPhone(num):
    # check that a phone number has exactly 10 digits
    if len(num) != 10:
        return False
    if not num.isdigit():
        return False
    else:
        return True
    
def verifyEmail(email):
    # check email to see if it matches general pattern
    # regex obtained from https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if re.search(regex, email):
        return True
    else:
        return False
    
def getUserType(username):
    # return the type of user with username
    u = userList()
    u.getByField('Username', username)
    if len(u.data) == 1:
        return u.data[0]['Type']
    else:
        return None