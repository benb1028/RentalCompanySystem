import pymysql,json

class baseObject:
    # base class for tables
    def setupObject(self,tn):
        # initialize object
        self.data = []
        self.tempdata = {}
        self.tn = tn
        self.fnl = []
        self.pk = ''
        self.conn = None
        self.errorList = []
        self.getFields()
    
    def connect(self):
        # connect to pymysql using config options
        import config
        self.conn = pymysql.connect(host=config.DB['host'], port=config.DB['port'], 
        user=config.DB['user'],passwd=config.DB['passwd'], db=config.DB['db'], 
        autocommit=True)
        
    def getFields(self):
        # get primary key and field names for table
        sql = 'DESCRIBE `' + self.tn + '`;'
        self.connect()
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        self.log(sql)
        cur.execute(sql)
        self.fnl = []
        for row in cur:
            self.fnl.append(row['Field'])
            if row['Extra'] == 'auto_increment' and row['Key'] == 'PRI':
                self.pk = row['Field']

    def add(self):
        # add tempdata to data
        self.data.append(self.tempdata)
        
    def set(self,fn,val):
        # temporarily set field to value
        if fn in self.fnl:
            self.tempdata[fn] = val
        else:
            print('Invalid field: ' + str(fn))
            
    def update(self,n,fn,val):
        # change specified value in self.data
        if len(self.data) >= (n + 1) and fn in self.fnl:
            self.data[n][fn] = val
        else:
            print('could not set value at row ' + str(n) + ' col ' + str(fn))
            
    def insert(self,n=0):
        # insert data into the db
        cols = ''
        vals = ''
        tokens = []
        # build sql query and tokens
        for fieldname in self.fnl:
            if fieldname in self.data[n].keys():
                tokens.append(self.data[n][fieldname])
                vals += '%s,'
                cols += '`'+fieldname+'`,'
        vals = vals[:-1]
        cols = cols[:-1]
        sql = 'INSERT INTO `' + self.tn +'` (' +cols + ') VALUES (' + vals+');'
        self.connect()
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        self.log(sql,tokens)
        cur.execute(sql,tokens)
        # get id of last row 
        self.data[n][self.pk] = cur.lastrowid
        
    def delete(self,n=0):
        # delete from data and db
        item = self.data.pop(n)
        self.deleteById(item[self.pk])
        
    def deleteById(self,id):
        # delete from db by id
        sql = 'DELETE FROM `' + self.tn + '` WHERE `'+self.pk+'` = %s;'
        tokens = (id)
        self.connect()
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        print(sql)
        print(tokens)
        self.log(sql,tokens) 
        cur.execute(sql,tokens)
    
    def getById(self,id):
        # get entry from db with id
        sql = 'SELECT * FROM `' + self.tn + '` WHERE `'+self.pk+'` = %s;'
        tokens = (id)
        self.connect()
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        self.log(sql,tokens)
        cur.execute(sql,tokens)
        self.data = []
        for row in cur: # should only be one row, but save all anyway
            self.data.append(row)
            
    def getAll(self,order = None):
        # get all entries in table
        sql = 'SELECT * FROM `' + self.tn + '` '
        if order != None:
            sql += ' ORDER BY `'+order+'`'
        self.connect()
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        #print(sql)
        #print(tokens)
        self.log(sql)
        cur.execute(sql)
        self.data = []
        for row in cur:
            self.data.append(row)   
            
    def update(self,n=0):
        # push row to db, updating existing entry
        tokens = []
        setstring = ''
        # build sql query and tokens
        for fieldname in self.data[n].keys():
            if fieldname != self.pk:
                setstring += ' `'+fieldname+'` = %s,'
                tokens.append(self.data[n][fieldname])
            
        setstring = setstring[:-1]
        sql = 'UPDATE `' + self.tn + '` SET ' + setstring + ' WHERE `' + self.pk + '` = %s' 
        tokens.append(self.data[n][self.pk])
        self.connect()
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        self.log(sql,tokens)
        cur.execute(sql,tokens)
    
    def getByField(self,field,value):
        # get list of rows from db that have a specified value at a specified field
        sql = 'SELECT * FROM `' + self.tn + '` WHERE `'+field+'` = %s;'
        tokens = (value)
        self.connect()
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        print(sql)
        print(tokens)
        self.log(sql,tokens)
        cur.execute(sql,tokens)
        self.data = []
        for row in cur:
            self.data.append(row)
            
    def getManyByField(self,field,values):
        # get list of rows from db that have any of a list of values at field
        self.data = []
        self.connect()
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        for value in values: # build and execute query for each value
            sql = 'SELECT * FROM `' + self.tn + '` WHERE `'+field+'` = %s;'
            tokens = (value)
            print(sql)
            print(tokens)
            self.log(sql,tokens)
            cur.execute(sql,tokens)
            for row in cur:
                self.data.append(row)
            
    def getLikeField(self,field,value):
        # get list of rows from db that have a value like the input
        sql = 'SELECT * FROM `' + self.tn + '` WHERE `'+field+'` LIKE %s;'
        tokens = ('%'+value+'%')
        self.connect()
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        self.log(sql, tokens)
        cur.execute(sql,tokens)
        self.data = []
        for row in cur:
            self.data.append(row)
            
    def log(self,sql,tokens=[]):
        # open a log file, record the time, query, and tokens for each query
        f = open('logs/sql_log.txt','a')
        import datetime
        now = datetime.datetime.now()
        debug_str = str(now) +' - ' +sql + json.dumps(tokens) + '\n'
        f.write(debug_str)
        f.close()
        
