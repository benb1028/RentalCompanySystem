from flask import Flask
from flask import render_template
from flask import request, session, redirect, url_for, escape, send_from_directory, make_response

from user import userList
from building import buildingList
from unit import unitList
from transaction import transactionList
from relationship import relationList

import pymysql,json,time

from flask_session import Session  #serverside sessions

app = Flask(__name__,static_url_path='')

SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

@app.route('/set')
def set():
    session['time'] = time.time()
    return 'set'
    
@app.route('/get')
def get():
    return str(session['time'])
    
@app.route('/select')
def select():
    return render_template('select.html', title='Select Test')

@app.route('/selectData')
def selectData():    
    u = userList()
    if request.args.get('term') is not None:
        u.getLikeField('email',request.args.get('term'))
    data = {'results':[],'pagination':{"more": 'false'}}
    
    
    for row in u.data:
        res = {}
        res['id'] = row['id']
        res['text'] = str(row['email']) + ' ' +   str(row['lname'])
        data['results'].append(res)
    
    return json.dumps(data)
    #required schema for select2 AJAX dropdown:
    '''{
          "results": [
            {
              "id": 1,
              "text": "Option 1"
            },
            {
              "id": 2,
              "text": "Option 2"
            }
          ],
          "pagination": {
            "more": true
          }
        }'''
 
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
        u = userList()
        if u.tryLogin(request.form.get('email'),request.form.get('password')):
            print('login ok')
            session['user'] = u.data[0]
            session['active'] = time.time()
            if session['user']['type'] == 'admin':
                return redirect('/a')
            elif session['user']['type'] == 'landlord':
                return redirect('/l')
            elif session['user']['type'] == 'tenant':
                return redirect('/t')
            else:
                return redirect('/main')
        else:
            print('login failed')
            return render_template('login.html', title='Login', msg='Incorrect login.')
    else:
        if 'msg' not in session.keys() or session['msg'] is None:
            m = 'Type your email and password to continue.'
        else:
            m = session['msg']
            session['msg'] = None
        return render_template('login.html', title='Login', msg=m)
    
@app.route('/logout',methods = ['GET','POST'])
def logout():
    del session['user'] 
    del session['active'] 
    return render_template('login.html', title='Login', msg='Logged out.')

@app.route('/')
def home():
    if checkSession() == False:
        return redirect('login')
    else:
        if session['user']['type'] == 'admin':
            return redirect('/a')
        elif session['user']['type'] == 'landlord':
            return redirect('/l')
        elif session['user']['type'] == 'tenant':
            return redirect('/t')
        else:
            return redirect('/login')
    #return render_template('test.html', title='Test2', msg='Welcome!')

@app.route('/a')
def adminmain():
    if checkSession() == True and checkAccess('admin') == True:
        return render_template('adminmain.html', title='Main Menu', msg=m)
    else:
        return redirect('/login')
    
@app.route('/l')
def landlordmain():
    if checkSession() == True and checkAccess('landlord') == True:
        return render_template('landmain.html', title='Main Menu', msg=m)
    else:
        return redirect('/login')

@app.route('/t')
def tenantmain():
    if checkSession() == True and checkAccess('tenant') == True:
        return render_template('tenantmain.html', title='Main Menu', msg=m)
    else:
        return redirect('/login')

@app.route('/a/tenants')
def tenants():
    if checkAccess('admin') == True:
        u = userList()
        u.getByField('type', 'tenant')
        return render_template('tenents.html', title='Tenants', users=u.data)
    else:
        return redirect('/login')
    
@app.route('/a/landlords')
def landlords():
    if checkAccess('admin') == True:
        u = userList()
        u.getByField('type', 'landlord')
        return render_template('landlords.html', title='Landlords', users=u.data)
    else:
        return redirect('/login')
    
@app.route('/l/tenants')
def tenantsbyll():
    if checkAccess('landlord') == True:
        u = userList()
        u.getByField('type', 'tenant')
        
    
@app.route('/index')
def index():
    user = {'username': 'Tyler'}
    
    
    items = [
        {'name':'Apple','price':2.34},
        {'name':'Orange','price':4.88},
        {'name':'Grape','price':2.44}
    ]
    return render_template('index.html', title='Home', user=user, items=items)

@app.route('/users')
def users():
    if checkSession() == False: 
        return redirect('login')
    u = userList()
    u.getAll()
    
    print(u.data)
    #return ''
    return render_template('users.html', title='User List',  users=u.data)
    
@app.route('/user')
def user():
    if checkSession() == False: 
        return redirect('login')
    u = userList()
    if request.args.get(u.pk) is None:
        return render_template('error.html', msg='No user id given.')  

    u.getById(request.args.get(u.pk))
    if len(u.data) <= 0:
        return render_template('error.html', msg='User not found.')  
    
    print(u.data)
    return render_template('user.html', title='User ',  user=u.data[0])

@app.route('/newuser', methods = ['GET', 'POST'])
def newuser():
    if checkSession() == False: 
        return redirect('login')
    if request.form.get('fname') is None:
        u = userList()
        u.set('fname','')
        u.set('lname','')
        u.set('email','')
        u.set('password','')
        u.set('type','')
        u.add()
        return render_template('newuser.html', title='New User',  user=u.data[0]) 
    else:
        u = userList()
        u.set('fname',request.form.get('fname'))
        u.set('lname',request.form.get('lname'))
        u.set('email',request.form.get('email'))
        u.set('password',request.form.get('password'))
        u.set('type',request.form.get('type'))
        u.add()
        if u.verifyNew():
            u.insert()
            print(u.data)
            return render_template('saveduser.html', title='User Saved',  user=u.data[0])
        else:
            return render_template('newuser.html', title='User Not Saved',  user=u.data[0], msg=u.errorList)
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
    
@app.route('/deleteuser',methods = ['GET', 'POST'])
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
    userinfo = 'Hello, ' + session['user']['fname']
    return render_template('main.html', title='Main menu',msg = userinfo)  

def checkSession():
    if 'active' in session.keys():
        timeSinceAct = time.time() - session['active']
        print(timeSinceAct)
        if timeSinceAct > 500:
            session['msg'] = 'Your session has timed out.'
            return False
        else:
            session['active'] = time.time()
            return True
    else:
        return False

def checkAccess(minAccess):
    if checkSession == True:
        uType = session['user']['type']
        if uType == 'admin':
            return True
        elif uType == 'landlord':
            if minAccess == 'landlord' or minAccess == 'tenant':
                return True
        elif uType == minAccess:
            return True
        else:
            return False
    else:
        return False
    
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