from flask import Flask
from flask import render_template
from flask import request, session, redirect, url_for, escape, send_from_directory, make_response

from user import userList, getUserType
from bill import billList
from unit import unitList
from contract import contractList
from datetime import datetime as dt
from datetime import date
import pymysql,json,time

from flask_session import Session  #serverside sessions

app = Flask(__name__,static_url_path='')

SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

@app.errorhandler(404)
def not_found(error):
    # if user attempts to visit an invalid url, render an error page and direct to main menu
    return render_template("404.html"), 404

@app.route('/login',methods = ['GET','POST'])
def login():
    '''
    -check login
    -set session
    -redirect to menu
    -check session on login pages
    '''
    print('-------------------------')
    if request.form.get('email') is not None and request.form.get('password') is not None:
        # if the form has been filled out, try login
        u = userList()
        if u.tryLogin(request.form.get('email'),request.form.get('password')):
            # if login is successful, set session and redirect to home
            session['UserID'] = u.data[0]['UserID']
            session['Username'] = u.data[0]['Username']
            session['active'] = time.time()
            session['access'] = u.data[0]['Type']
            return redirect(url_for('home'))
        else:
            # if unsuccessful, display login page again
            return render_template('login.html', title='Login', msg='Incorrect login.')
    else:
        # if the login form has not been filled out, display login page
        if 'msg' not in session.keys() or session['msg'] is None:
            m = 'Type your email and password to continue.'
        else:
            m = session['msg']
            session['msg'] = None
        return render_template('login.html', title='Login', msg=m)
    
@app.route('/logout',methods = ['GET','POST'])
def logout():
    # clear all session variables and go to login page
    session.clear()
    return render_template('login.html', title='Login', msg='Logged out.')

@app.route('/')
def home():
    # check to make sure user is logged in, redirect to login if not
    if checkSession() == False:
        session['msg'] = "Please login to continue."
        return redirect('login')
    else: # determine user type and redirect to proper home page
        if session['access'] == 'admin':
            return redirect(url_for('adminmain'))
        elif session['access'] == 'landlord':
            return redirect(url_for('landlordmain'))
        elif session['access'] == 'tenant':
            return redirect(url_for('tenantmain'))
        else:
            return redirect(url_for('login'))
    

@app.route('/a')
def adminmain():
    # if user is admin, render admin home page
    if checkAccess('admin') == True:
        return render_template('adminmain.html', title='Main Menu', msg=session.get('msg'))
    else: 
        return redirect(url_for('home'))
    
    
@app.route('/l')
def landlordmain():
    #if user is landlord, render landlord home page
    if checkAccess('landlord') == True:
        return render_template('landmain.html', title='Main Menu', msg=session.get('msg'))
    else:
        return redirect(url_for('home'))

@app.route('/t')
def tenantmain():
    # if user is tenant, render tenant home page
    if checkAccess('tenant') == True:
        return render_template('tenantmain.html', title='Main Menu', msg=session.get('msg'))
    else:
        return redirect(url_for('home'))

@app.route('/a/tenants')
def tenants():
    # if user is admin, display list of all tenants
    if checkAccess('admin') == True:
        u = userList()
        u.getByField('type', 'tenant')
        return render_template('users.html', title='Tenants', users=u.data)
    else:
        return redirect(url_for('home'))
    
@app.route('/a/landlords')
def landlords():
    # if user is admin, display list of all landlords
    if checkAccess('admin') == True:
        u = userList()
        u.getByField('type', 'landlord')
        return render_template('users.html', title='Landlords', users=u.data)
    else:
        return redirect(url_for('home'))
    
@app.route('/a/contracts')
def acontracts():
    # if user is admin, display list of all contracts
    if checkAccess('admin') == True:
        c = contractList()
        c.getAll()
        return render_template('contracts.html', title='Contracts', contracts=c.data)
    else:
        return redirect(url_for('home'))
    
@app.route('/<string:username>/contracts')
def contracts(username):
    # display all contracts associated with username
    uType = session.get('access')
    if uType == 'admin':
        # if user is admin, find the type of the requested username and display their contracts
        viewedUserType = getUserType(username)
        if viewedUserType == 'tenant':
            c = contractList()
            c.getByField('TUserName', username)
        elif viewedUserType == 'landlord':
            c = contractList()
            c.getByField('LUserName', username)
        return render_template('contracts.html', title='Contracts', contracts=c.data)
    elif uType == 'tenant' and checkUser(username) == True:
        # if user is a tenant and is the requested username, display their contracts
        c = contractList()
        c.getByField('TUserName', username)
        return render_template('contracts.html', title='Contracts', contracts=c.data)
    elif uType == 'landlord' and checkUser(username) == True:
        # if user is a landlord and is the requested username, display their contracts
        c = contractList()
        c.getByField('LUserName', username)
        return render_template('contracts.html', title='Contracts', contracts=c.data)
    else:
        return redirect(url_for('home'))
    
@app.route('/a/newunit', methods=['POST','GET'])
def newunit():
    if checkAccess('admin') == True:
        # get list of landlords to choose from for new unit
        l = userList()
        l.getByField('Type', 'Landlord')
        if request.form.get('Address1') is None: # form unfilled, render form with defaults
            u = unitList()
            u.set('Address1', '')
            u.set('Address2', '')
            u.set('StdRent', 0)
            u.set('MaxOccupancy', 0)
            u.set('Bedrooms', 0)
            u.set('Bathrooms', 0)
            u.set('Area', 0)
            u.set('LandlordID', 0)
            u.set('CurrOccupancy', 0)
            u.add()
            return render_template('newunit.html', title='New Unit', unit=u.data[0], landlords=l.data)
        else: # form filled, get values from form 
            u = unitList()
            u.set('Address1', request.form.get('Address1'))
            u.set('Address2', request.form.get('Address2'))
            u.set('StdRent', float(request.form.get('StdRent')))
            u.set('MaxOccupancy', int(request.form.get('MaxOccupancy')))
            u.set('Bedrooms', int(request.form.get('Bedrooms')))
            u.set('Bathrooms', float(request.form.get('Bathrooms')))
            u.set('Area', float(request.form.get('Area')))
            u.set('LandlordID', int(request.form.get('LandlordID')))
            u.set('CurrOccupancy', 0)
            u.set('HasRoom', 1)
            u.add()
            if u.verifyNew(): # verify values for new unit, insert into table if valid
                u.insert()
                return render_template('savedunit.html', title='Success')
            else: # if invalid, render form again with the entered data
                return render_template('newunit.html', title='Unit Not Saved', unit=u.data[0], landlords=l.data, msg=u.errorList)
    else: # if not admin, redirect home
        session['msg'] = 'Access Denied. Redirected to home.'
        return redirect(url_for('home'))
    
@app.route('/a/units')
def aunits():
    # if admin, display all units
    if checkAccess('admin') == True:
        u = unitList()
        u.getAll()
        return render_template('units.html', title='Units', units=u.data)
    else:
        return redirect(url_for('home'))

@app.route('/a/newcontract', methods=['POST', 'GET'])
def newcontract():
    # allow admin to create a new contract between a tenant and unit/landlord
    if checkAccess('admin') == True:
        # get list of tenants
        t = userList()
        t.getByField('Type', 'tenant')
        # get list of availible units
        u = unitList()
        u.getByField('HasRoom', 1)
        if request.form.get('MonthlyCharge') is None: # form unfilled, render with defaults
            c = contractList()
            c.set('StartDate', date.today().isoformat())
            c.set('EndDate', date.today().isoformat())
            c.set('MonthlyCharge', 0.0)
            c.set('Active', 1)
            c.set('TUserName', '')
            c.set('LUserName', '')
            c.set('TenantID', 0)
            c.set('LandlordID', 0)
            c.set('UID', 0)
            c.add()
            return render_template('newcontract.html', title="New Contract",
                                   contract=c.data[0], tenants=t.data,
                                   units=u.data)
        else: # form filled, get values
            c = contractList()
            u1 = unitList()
            u1.getById(request.form.get('UID'))
            t1 = userList()
            t1.getById(request.form.get('TenantID'))
            l1 = userList()
            l1.getById(u1.data[0]['LandlordID'])
            c.set('StartDate', request.form.get('StartDate'))
            c.set('EndDate', request.form.get('EndDate'))
            c.set('MonthlyCharge', float(request.form.get('MonthlyCharge')))
            c.set('Active', 1)
            c.set('TUserName', t1.data[0]['Username'])
            c.set('LUserName', l1.data[0]['Username'])
            c.set('TenantID', request.form.get('TenantID'))
            c.set('LandlordID', u1.data[0]['LandlordID'])
            c.set('UID', request.form.get('UID'))
            c.add()
            if c.verifyNew(): # check values for new contract, if valid insert into db and redirect to contracts page
                c.insert()
                session['msg'] = 'Contract Saved.'
                return redirect(url_for('acontracts'))
            else: 
                return render_template('newcontract.html', title='Contract Not Saved', 
                                       contract=c.data[0], tenants=t.data, units=u.data)
    else:
        return redirect(url_for('home'))
    
@app.route('/a/bills')
def abills():
    # if admin, display all bills
    if checkAccess('admin') == True:
        b = billList()
        b.getAll()
        return render_template('bills.html', bills=b.data)
    else:
        return redirect(url_for('home'))
    
@app.route('/<string:username>/bills')
def bills(username):
    # display all bills associated with username
    uType = session.get('access')
    if uType == 'admin': # if admin, find user type of given username and display their bills
        viewedUserType = getUserType(username)
        if viewedUserType == 'tenant':
            b = billList()
            b.getByField('TUserName', username)
        elif viewedUserType == 'landlord':
            b = billList()
            b.getByField('LUserName', username)
        return render_template('bills.html', title='Bills', bills=b.data)
    elif uType == 'tenant' and checkUser(username) == True:
        # if user is a tenant and the username matches, display their bills
        b = billList()
        b.getByField('TUserName', username)
        return render_template('bills.html', title='Bills', bills=b.data)
    elif uType == 'landlord' and checkUser(username) == True:
        # if user is a landlord and the username matches, display their bills
        b = billList()
        b.getByField('LUserName', username)
        return render_template('bills.html', title='Bills', bills=b.data)
    else:
        # if user is not an admin and attempting to view someone elses bill, redirect home
        return redirect(url_for('home'))
    
@app.route('/l/<string:username>/tenants')
def tenantsbyll(username):
    # if username is a landlord and the user is either username or admin, show the tenants who have a contract with username
    if getUserType(username) == 'landlord' and (checkUser(username) == True or checkAccess('admin')):
        u = userList()
        u.getTenants(username)
        if len(u.data) > 0:
            return render_template('users.html', title='Tenants', users=u.data)
        else:
            session['msg'] = 'No tenants to show.'
            return redirect(url_for('landlordmain'))
    else:
        return redirect(url_for('home'))
    
@app.route('/l/<string:username>/newbill', methods = ['POST', 'GET'])
def newbill(username):
    # allow landlords to create a new bill for one of their tenants
    if checkUser(username) and getUserType(username) == 'landlord':
        # get list of valid tenants
        t = userList()
        t.getTenants(username)
        if request.form.get('AmntDue') is None: # form unfilled, render with defaults
            b = billList()
            b.set('AmntDue', 0)
            b.set('DateDue', date.today().isoformat())
            b.set('BillerUserID', session.get('UserID'))
            b.add()
            return render_template('newbill.html', title='New Bill',
                                   bill=b.data, tenants=t.data, username=username)
        else: # form filled, get data from forms
            b = billList()
            t1 = userList()
            t1.getById(request.form.get('TenantID'))
            b.set('AmntDue', float(request.form.get('AmntDue')))
            b.set('DateDue', request.form.get('DateDue'))
            b.set('BilledUserID', request.form.get('TenantID'))
            b.set('DateBilled', date.today().isoformat())
            b.set('AmntPaid', 0)
            b.set('DatePaid', None)
            b.set('BillerUserID', session.get('UserID'))
            b.set('TUserName', t1.data[0]['Username'])
            b.set('LUserName', username)
            b.add()
            if b.verifyNew(): # if new data is valid, insert into database and redirect to bills screen
                b.insert()
                session['msg'] = "Bill Added."
                return redirect(url_for('bills', username=username))
            else: # if invalid, try again
                return render_template('newbill.html', title='Bill Not Saved',
                                       bill=b.data, tenants=t.data, username=username)
    else:
        return redirect(url_for('home'))

@app.route('/a/users')
def allusers():
    # if admin, show all users
    if checkAccess('admin') == True: 
        u = userList()
        u.getAll()
        return render_template('users.html', title='User List',  users=u.data)
    else:
        return redirect(url_for('home'))
    
@app.route('/user/<string:username>')
def user(username):
    # check if user is same as username or if an admin or landlord
    if checkUser(username) == False and checkAccess('landlord') == False:
        session['msg'] = "You are not authorized to view this page."
        return redirect(url_for('home'))
    u = userList()
    u.getByField('Username', username)
    if len(u.data) != 1: # show error if username is not found or duplicates are found
        return render_template('error.html', msg='User not found.')
    else: 
        return render_template('user.html', title=u.data[0]['Username'],  user=u.data[0])

@app.route('/a/newuser', methods = ['GET', 'POST'])
def newuser():
    # allow admin to create a new user
    if checkAccess('admin') == False: 
        return redirect(url_for('home'))
    if request.form.get('Username') is None: # form empty, render blank form
        u = userList()
        u.set('Username','')
        u.set('Email', '')
        u.set('Password','')
        u.set('FirstName','')
        u.set('LastName','')
        u.set('Type','tenant')
        u.set('Birthday', date.today().isoformat())
        u.set('Phone', '')
        u.set('Balance', 0.0)
        u.set('Active', 0)
        u.add()
        return render_template('newuser.html', title='New User',  user=u.data[0], today=date.today().isoformat()) 
    else: # form filled, retrieve values
        u = userList()
        u.set('Username', request.form.get('Username'))
        u.set('Email', request.form.get('Email'))
        u.set('Password', request.form.get('Password'))
        u.set('FirstName', request.form.get('FirstName'))
        u.set('LastName', request.form.get('LastName'))
        u.set('Type', request.form.get('Type'))
        u.set('Birthday', request.form.get('Birthday'))
        u.set('Phone', request.form.get('Phone'))
        u.set('Balance', 0.0)
        u.set('Active', 0)
        u.add()
        if u.verifyNew() and u.passMatch(request.form.get('Password2')):
            # verify new user data and insert if valid
            u.insert()
            return render_template('saveduser.html', title='User Saved',  user=u.data[0])
        else: # if invalid, render form again
            return render_template('newuser.html', title='User Not Saved',  user=u.data[0], msg=u.errorList, today=date.today().isoformat())

    
@app.route('/a/deleteuser',methods = ['GET', 'POST'])
def deleteuser():
    # if admin, get id and delete the user
    if checkAccess('admin') == False: 
        return redirect(url_for('home'))
    print("User id:",request.form.get('id')) 
    #return ''
    u = userList()
    u.deleteById(request.form.get('id'))
    return render_template('confirmaction.html', title='User Deleted',  msg='User deleted.')


def checkSession():
    # get time of last action, clear session if timed out, otherwise update active time 
    lastAct = session.get('active')
    if lastAct is not None:
        timeSinceAct = time.time() - lastAct
        if timeSinceAct > 50000:
            print("timed out.")
            session.clear()
            session['msg'] = 'Your session has timed out.'
            return False
        else:
            session['active'] = time.time()
            return True
    else:
        print('Login required.')
        return False

def checkAccess(minAccess):
    # check the user in session to see if they meet minAccess
    if checkSession() == True:
        uType = session.get('access')
        print(f'User is a/an {uType}, page requires {minAccess} to view.')
        if uType == 'admin':
            print('Access granted.')
            return True
        elif uType == 'landlord':
            if minAccess == 'landlord' or minAccess == 'tenant':
                print('Access granted.')
                return True
        elif uType == minAccess:
            print('Access granted.')
            return True
        else:
            print('Access denied.')
            return False
    else:
        print('Login required.')
        return False
    
def checkUser(userName):
    # return true if username matches that in session
    curUser = session['Username']
    if userName == curUser:
        return True
    else:
        return False
    
if __name__ == '__main__':
   app.secret_key = '1234'
   app.run(host='127.0.0.1',debug=True)   
   