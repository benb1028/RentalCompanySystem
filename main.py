from flask import Flask
from flask import render_template
from flask import request, session, redirect, url_for, escape, send_from_directory, make_response

from user import userList
from bill import billList
from unit import unitList
from transaction import transactionList
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
    # if user attempts to visit an invalid url, render an error page and diresct to main menu
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
    session.clear()
    return render_template('login.html', title='Login', msg='Logged out.')

@app.route('/')
def home():
    if checkSession() == False:
        session['msg'] = "Please login to continue."
        return redirect('login')
    else:
        if session['access'] == 'admin':
            return redirect(url_for('adminmain'))
        elif session['access'] == 'landlord':
            return redirect(url_for('landlordmain'))
        elif session['access'] == 'tenant':
            return redirect(url_for('tenantmain'))
        else:
            return redirect(url_for('login'))
    #return render_template('test.html', title='Test2', msg='Welcome!')

@app.route('/a')
def adminmain():
    if checkAccess('admin') == True:
        return render_template('adminmain.html', title='Main Menu', msg=session.get('msg'))
    else:
        return redirect(url_for('login'))
    
    
@app.route('/l/<string:username>')
def landlordmain(username):
    if checkAccess('landlord') == True:
        return render_template('landmain.html', title='Main Menu', msg=session.get('msg'))
    else:
        return redirect(url_for('login'))

@app.route('/t/<string:username>')
def tenantmain(username):
    if checkSession() == True and checkAccess('tenant') == True:
        return render_template('tenantmain.html', title='Main Menu', msg=session.get('msg'))
    else:
        return redirect(url_for('login'))

@app.route('/a/tenants')
def tenants():
    if checkAccess('admin') == True:
        u = userList()
        u.getByField('type', 'tenant')
        return render_template('users.html', title='Tenants', users=u.data)
    else:
        return redirect(url_for('login'))
    
@app.route('/a/landlords')
def landlords():
    if checkAccess('admin') == True:
        u = userList()
        u.getByField('type', 'landlord')
        return render_template('users.html', title='Landlords', users=u.data)
    else:
        return redirect(url_for('login'))
    
@app.route('/a/contracts')
def acontracts():
    if checkAccess('admin') == True:
        c = contractList()
        c.getAll()
        return render_template('contracts.html', title='Contracts', contracts=c.data)
    else:
        return redirect(url_for('home'))
    
@app.route('/<string:username>/contracts')
def contracts(username):
    uType = session.get('access')
    if uType == 'admin':
        viewedUserType = getUserType(username)
        if viewedUserType == 'tenent':
            c = contractList()
            c.getByField('TUserName', username)
        elif viewedUserType == 'landlord':
            c = contractList()
            c.getByField('LUserName', username)
        return render_template('contracts.html', title='Contracts', contracts=c.data)
    elif uType == 'tenent' and checkUser(username) == True:
        c = contractList()
        c.getByField('TUserName', username)
        return render_template('contracts.html', title='Contracts', contracts=c.data)
    elif uType == 'landlord' and checkUser(username) == True:
        c = contractList()
        c.getByField('LUserName', username)
        return render_template('contracts.html', title='Contracts', contracts=c.data)
    else:
        return redirect(url_for('home'))
    
@app.route('/a/newunit', methods=['POST','GET'])
def newunit():
    if checkAccess('admin') == True:
        l = userList()
        l.getByField('Type', 'Landlord')
        if request.form.get('Address1') is None:
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
        else:
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
            u.add()
            if u.verifyNew():
                u.insert()
                return render_template('savedunit.html', title='Success')
            else:
                return render_template('newunit.html', title='Unit Not Saved', unit=u.data[0], landlords=l.data)
    else:
        session['msg'] = 'Access Denied. Redirected to home.'
        return redirect(url_for('home'))
    
@app.route('/a/units')
def aunits():
    if checkAccess('admin') == True:
        u = unitList()
        u.getAll()
        return render_template('units.html', title='Units', units=u.data)
    else:
        return redirect(url_for('home'))

@app.route('/a/bills')
def abills():
    if checkAccess('admin') == True:
        b = billList()
        b.getAll()
        return render_template('bills.html', bills=b.data)
    else:
        return redirect(url_for('home'))
    
@app.route('/<string:username>/bills')
def bills(username):
    uType = session.get('access')
    if uType == 'admin':
        viewedUserType = getUserType(username)
        if viewedUserType == 'tenent':
            b = billList()
            b.getByField('TUserName', username)
        elif viewedUserType == 'landlord':
            b = billList()
            b.getByField('LUserName', username)
        return render_template('bills.html', title='Bills', bills=b.data)
    elif uType == 'tenent' and checkUser(username) == True:
        b = billList()
        b.getByField('TUserName', username)
        return render_template('bills.html', title='Bills', bills=b.data)
    elif uType == 'landlord' and checkUser(username) == True:
        b = billList()
        b.getByField('LUserName', username)
        return render_template('bills.html', title='Bills', bills=b.data)
    else:
        return redirect(url_for('home'))
    
@app.route('/l/<string:username>/tenants')
def tenantsbyll(username):
    if checkAccess('landlord') == True:
        u = userList()
        u.getByField('type', 'tenant')
        u = u.sortByManager(session.get('userid'))
        if len(u.data) > 0:
            return render_template('users.html', title='Tenants', users=u.data)
        else:
            return redirect(url_for('landlordmain'))

@app.route('/a/users')
def allusers():
    if checkSession() == False: 
        return redirect('login')
    u = userList()
    u.getAll()
    
    print(u.data)
    #return ''
    return render_template('users.html', title='User List',  users=u.data)
    
@app.route('/user/<string:username>')
def user(username):
    if checkUser(username) == False and checkAccess('landlord') == False:
        session['msg'] = "You are not authorized to view this page."
        return redirect(url_for('home'))
    u = userList()
    u.getByField('Username', username)
    if len(u.data) <= 0:
        return render_template('error.html', msg='User not found.')  
    
    print(u.data)
    return render_template('user.html', title='User ',  user=u.data[0])

@app.route('/a/newuser', methods = ['GET', 'POST'])
def newuser():
    if checkSession() == False: 
        return redirect('login')
    if request.form.get('Username') is None:
        u = userList()
        u.set('Username','')
        u.set('Email', '')
        u.set('Password','')
        u.set('FirstName','')
        u.set('LastName','')
        u.set('Type','tenent')
        u.set('Birthday', date.today().isoformat())
        u.set('Phone', '')
        u.set('Balance', 0.0)
        u.set('Active', 0)
        u.add()
        return render_template('newuser.html', title='New User',  user=u.data[0], today=date.today().isoformat()) 
    else:
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
            u.insert()
            print(u.data)
            return render_template('saveduser.html', title='User Saved',  user=u.data[0])
        else:
            return render_template('newuser.html', title='User Not Saved',  user=u.data[0], msg=u.errorList, today=date.today().isoformat())

@app.route('/edituser/<string:username>', methods = ['GET', 'POST'])
def edituser(username):
    if checkUser(username) == False:
        return redirect(url_for('home'))
    #else:
        


@app.route('/saveuser', methods = ['GET', 'POST'])
def saveuser():
    if checkSession() == False: 
        return redirect('login')
    u = userList()
    u.set('id',request.form.get('id'))
    u.set('fname',request.form.get('fname'))
    u.set('lname',request.form.get('lname'))
    u.set('email',request.form.get('email'))
    u.set('password',request.form.get('password'))
    u.set('subscribed',request.form.get('type'))
    u.add()
    if u.verifyChange():
        u.update()
        #print(u.data)
        #return ''
        return render_template('saveduser.html', title='User Saved',  user=u.data[0])
    else:
        return render_template('user.html', title='User Not Saved',  user=u.data[0],msg=u.errorList)
    
@app.route('/a/deleteuser',methods = ['GET', 'POST'])
def deleteuser():
    if checkSession() == False: 
        return redirect('login')
    print("User id:",request.form.get('id')) 
    #return ''
    u = userList()
    u.deleteById(request.form.get('id'))
    return render_template('confirmaction.html', title='User Deleted',  msg='User deleted.')
    '''
    <form action="/deletecustomer" method="POST">
			<input type="submit" value="Delete this customer" />
			<input type="hidden" name="id" value="{{ customer.id }}" />
		</form>
    '''

@app.route('/main')
def main():
    if checkSession() == False: 
        return redirect('login')
    userinfo = 'Hello, ' + session['Username']
    return render_template('main.html', title='Main menu',msg = userinfo)  

def checkSession():
    lastAct = session.get('active')
    print(lastAct)
    if lastAct is not None:
        timeSinceAct = time.time() - lastAct
        print(timeSinceAct)
        if timeSinceAct > 5000:
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
    curUser = session['Username']
    if userName == curUser:
        return True
    else:
        return False
    
def getUserType(username):
    u = userList()
    u.getByField('Username', username)
    if len(u.data) == 1:
        return u.data[0]['Type']
    else:
        return None
    
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


if __name__ == '__main__':
   app.secret_key = '1234'
   app.run(host='127.0.0.1',debug=True)   
   
   
   
   
   
   
'''
================================================================
START EVENT PAGES:
=================================================================
'''
'''
@app.route('/events')
def events():
    if checkSession() == False: 
        return redirect('login')
    e = eventList()
    e.getAll()
    
    #print(e.data)
    #return ''
    return render_template('event/events.html', title='Event List',  events=e.data)
    
@app.route('/event')
def event():
    if checkSession() == False: 
        return redirect('login')
    e = eventList()
    if request.args.get(e.pk) is None:
        return render_template('error.html', msg='No event id given.')  

    e.getById(request.args.get(e.pk))
    if len(e.data) <= 0:
        return render_template('error.html', msg='Event not found.')  
    
    print(e.data)
    return render_template('event/event.html', title='Event ',  event=e.data[0])  
@app.route('/newevent',methods = ['GET', 'POST'])
def newevent():
    if checkSession() == False: 
        return redirect('login')
    if request.form.get('name') is None:
        e = eventList()
        e.set('name','')
        e.set('start','')
        e.set('end','')
        e.add()
        return render_template('event/newevent.html', title='New Event',  event=e.data[0]) 
    else:
        e = eventList()
        e.set('name',request.form.get('name'))
        e.set('start',request.form.get('start'))
        e.set('end',request.form.get('end'))
        e.add()
        if e.verifyNew():
            e.insert()
            print(e.data)
            return render_template('event/savedevent.html', title='Event Saved',  event=e.data[0])
        else:
            return render_template('event/newevent.html', title='Event Not Saved',  event=e.data[0],msg=e.errorList)
@app.route('/saveevent',methods = ['GET', 'POST'])
def saveevent():
    if checkSession() == False: 
        return redirect('login')
    e = eventList()
    e.set('eid',request.form.get('eid'))
    e.set('name',request.form.get('name'))
    e.set('start',request.form.get('start'))
    e.set('end',request.form.get('end'))
    e.add()
    if e.verifyChange():
        e.update()
        #print(e.data)
        #return ''
        return render_template('event/savedevent.html', title='Event Saved',  event=e.data[0])
    else:
        return render_template('event/event.html', title='Event Not Saved',  event=e.data[0],msg=e.errorList)

'''
'''
================================================================
END EVENT PAGES
=================================================================
'''
'''
================================================================
START REVIEW PAGES:
=================================================================
'''
'''
@app.route('/newreview',methods = ['GET', 'POST'])
def newreview():
    if checkSession() == False: 
        return redirect('login')
    allEvents = eventList()
    allEvents.getAll()
    if request.form.get('review') is None:
        r = reviewList()
        r.set('event_id','')
        r.set('customer_id','')
        r.set('review','')
        r.add()
        return render_template('review/newreview.html', title='New Review',  review=r.data[0],el=allEvents.data) 
    else:
        r = reviewList()
        r.set('event_id',request.form.get('event_id'))
        r.set('customer_id',session['user']['id'])
        r.set('review',request.form.get('review'))
        r.add()
        if r.verifyNew():
            r.insert()
            print(r.data)
            return render_template('review/savedreview.html', title='Review Saved',  review=r.data[0])
        else:
            return render_template('review/newreview.html', title='Review Not Saved',  review=r.data[0],msg=r.errorList,el=allEvents.data)
@app.route('/savereview',methods = ['GET', 'POST'])
def savereview():
    if checkSession() == False: 
        return redirect('login')
    r = reviewList()
    r.set('aid',request.form.get('aid'))
    r.set('event_id',request.form.get('event_id'))
    r.set('customer_id',request.form.get('customer_id'))
    r.set('review',request.form.get('review'))
    r.add()
    r.update()
    #print(e.data)
    #return ''
    return render_template('review/savedreview.html', title='Review Saved',  review=r.data[0])

@app.route('/myreviews')
def myreviews():
    if checkSession() == False: 
        return redirect('login')
    r = reviewList()
    r.getByCustomer(session['user']['id'])
    #print(r.data)
    #return ''
    return render_template('myreviews.html', title='My Reviews',  reviews=r.data)
   
'''
'''
================================================================
END REVIEW PAGES
=================================================================
'''