from flask import Flask, render_template, url_for, flash, redirect, request
from form import EventForm, AccountForm, LoginForm, AccountInfoForm, EventForm2, ChangePasswordForm, GuestForm, SearchForm, DeleteAccountForm
from flask_bcrypt import Bcrypt
from PIL import Image
import sqlite3
import os
import string
import random
import time
from form import user

app=Flask(__name__)

app.config['SECRET_KEY']='14b8g7cfsfsgsdgdff6bdb8v7'

bcrypt=Bcrypt(app)

@app.route('/')
@app.route('/home', methods=['GET', 'POST'])
def home_page():
    searchform=SearchForm()
    data=[]
    events=sql_query("SELECT * FROM Events;")
    
    for event in events:
        ev=[]
        players=[]
        list=sql_query("SELECT playerid FROM PartIn WHERE eventid=?;",(event[0],))
        ev.append(event)
        for i in list:
            player=sql_query("SELECT * FROM Players WHERE number=?;",(i[0],))
            if player:
                players.append(player[0])
        ev.append(players)
        data.append(ev)
        
    if searchform.is_submitted():
        data=search_for_events(searchform)
        
    
    return render_template("mainpage.html", title="Front page", data=data, user=user, searchform=searchform)

@app.route('/home/<int:id>')
def add2event(id):
    if user.number:
        if sql_query("SELECT * FROM PartIn WHERE playerid=? AND eventid=?",(user.number,id)):
            flash('You are already attending that event','warning')
        else:
            sql_query("INSERT INTO PartIn values(?,?)",(user.number, id),commit=True)
            sql_query("UPDATE Events SET num=num+1 WHERE id=?",(id,),commit=True)
        return redirect(url_for('account'))
        
    else:
        return redirect(url_for('guestlogin',id=id))
    

@app.route('/create_event', methods=['GET', 'POST'])
def create_event():
    searchform=SearchForm()
    form=EventForm()
    if user.number:
        form=EventForm2()
    
    if form.validate_on_submit():
        number=user.number
        if not user.number:
            number=form.number.data
            
        last_id=sql_query("INSERT INTO Events VALUES(?,?,?,?,?,?,?,?,?,?)",(None,form.header.data,form.sport.data,form.place.data,form.city.data,form.time.data,form.description.data,form.limit.data,1,number), commit=True, get_id=True)
        sql_query("INSERT INTO PartIn VALUES(?,?)",(number, last_id), commit=True)
        
        if user.number==None:
            ans=sql_query("SELECT * FROM PLayers WHERE number=?",(form.number.data,))
            if ans:
                return redirect(url_for('login'))
            else:
                user.number=form.number.data
                return redirect(url_for('create_account'))
            
        return redirect(url_for('home_page'))
    
    if searchform.is_submitted():
        data=search_for_events(searchform)
        return home_page()
    
    return render_template("create_event.html", title='Create an event', form=form, user=user, searchform=searchform)


@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    searchform=SearchForm()
    form=AccountForm()
    
    if form.validate_on_submit():
        kuva='default.png'
        if form.sex.data=='Female':
            kuva='default2.png'
        if form.photo.data:
            picture_file=save_picture(form.photo.data)
            kuva=picture_file
        hashed=None
        if form.password.data:
            hashed=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            sql_query("INSERT INTO Players VALUES(?,?,?,?,?,?,?)",(form.age.data,form.sex.data,form.name.data,form.bio.data, hashed, form.number.data, kuva),commit=True)
            user.login(form.number.data)
            flash('Account created, logged in!', 'primary')
        
        return redirect(url_for('home_page'))
    
    elif request.method=='GET' and user.number:
        form.number.data=user.number
        
    if searchform.is_submitted():
        data=search_for_events(searchform)
        return home_page()
    
    return render_template("create_account.html", title='Create an account', form=form, user=user, searchform=searchform)

@app.route('/account', methods=['GET','POST'])
def account():
    searchform=SearchForm()
    if(user.number==None):
            flash('You have to be logged in to enter that page', 'danger')
            return redirect('login')
    image_source="static/profile_pics/" + user.photo
    events=sql_query("SELECT * FROM Events INNER JOIN PartIn ON Events.id==PartIn.eventid AND PartIn.playerid=?;",(user.number,))
    data=[]
    for event in events:
        ev=[]
        players=[]
        list=sql_query("SELECT playerid FROM PartIn WHERE eventid=?;",(event[0],))
        ev.append(event)
        for i in list:
            player=sql_query("SELECT * FROM Players WHERE number=?;",(i[0],))
            if player:
                players.append(player[0])
        ev.append(players)
        data.append(ev)
    
    if searchform.is_submitted():
        data=search_for_events(searchform)
        return home_page()
    
    return render_template("account.html", title='Account',user=user, image_source=image_source, data=data, searchform=searchform)

@app.route('/account/change-info',methods=['GET', 'POST'])
def change_accountinfo():
    searchform=SearchForm()
    
    if(user.number==None):
        flash('You have to be logged in to enter that page', 'danger')
        return redirect('login')
    form=AccountInfoForm()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(user.password, form.password.data):
            picture_file=user.photo
            if form.photo.data:
                picture_file=save_picture(form.photo.data)
                user.photo=picture_file
                
            ree=sql_query("UPDATE Players SET name=?, age=?, sex=?, photo=?, bio=? WHERE number=?;",(form.name.data, form.age.data, form.sex.data, picture_file, form.bio.data, user.number), commit=True)
            user.login(user.number)
            return redirect(url_for('account'))
            
        else:
            flash('Wrong password','danger')
    
    elif request.method=='GET':
        form.name.data=user.name
        form.age.data=user.age
        form.sex.data=user.sex
        form.bio.data=user.bio
        
    if searchform.is_submitted():
        data=search_for_events(searchform)
        return home_page()
        
    return render_template("account_info.html", title='Account info',user=user, form=form, searchform=searchform)

@app.route('/account/change-password',methods=['GET', 'POST'])
def change_password():
    searchform=SearchForm()
    
    if(user.number==None):
        flash('You have to be logged in to enter that page', 'danger')
        return redirect('login')
    
    form=ChangePasswordForm()
    if form.validate_on_submit():
        if user.password==None or bcrypt.check_password_hash(user.password, form.old.data):
            new_hashed=bcrypt.generate_password_hash(form.new.data).decode('utf-8')
            ree=sql_query("UPDATE Players SET password=? WHERE number=?;",(new_hashed,user.number), commit=True)
            if ree==None:
                flash('Something went wrong', 'danger')
            else:
                flash('Password changed', 'success')
                return redirect(url_for('account'))
        else:
            flash('Old password wrong', 'danger')
    
    if searchform.is_submitted():
        data=search_for_events(searchform)
        return home_page()
            
    return render_template('change_password.html', title='Change password', user=user, form=form, searchform=searchform)

@app.route('/exitevent<int:id>', methods=['GET','POST'])
def exit_event(id):
    if(user.number==None):
        flash('You have to be logged in to enter that page', 'danger')
        return redirect('login')
    sql_query("UPDATE Events SET num=num-1 WHERE id=?",(id,),commit=True)
    sql_query('DELETE FROM PartIn WHERE playerid=? AND eventid=?',(user.number, id),commit=True)
    ans=sql_query("SELECT playerid FROM PartIn WHERE eventid=?",(id,))
    if len(ans)==0:
        sql_query("DELETE FROM Events WHERE id=?",(id,), commit=True)
    
    return redirect(url_for('account'))

@app.route('/logout')
def logout():
    user.logout()
    flash('You have logged out!', 'primary')
    return redirect(url_for('home_page'))

@app.route('/login', methods=['GET', 'POST'])
@app.route('/login<int:id>', methods=['GET', 'POST'])
def login(id=0):
    searchform=SearchForm()
    form=LoginForm()
    
    if form.validate_on_submit():
        if verify_login(form.number.data,form.password.data):
            flash('You have logged in!', 'primary')
            
            if sql_query("SELECT * FROM PartIn WHERE playerid=? AND eventid=?",(user.number,id)):
                flash('You are already attending that event','warning')
            elif id!=0:
                sql_query("INSERT INTO PartIn values(?,?)",(user.number, id),commit=True)
                sql_query("UPDATE Events SET num=num+1 WHERE id=?",(id,),commit=True)
            
            return redirect(url_for('account'))
        else:
            flash('Wrong password or number!', 'danger')
    
    if searchform.is_submitted():
        data=search_for_events(searchform)
        return home_page()
    
    return render_template("loginpage.html", title='Login page', user=user, form=form, searchform=searchform)

@app.route('/guestlogin<int:id>', methods=['GET','POST'])
def guestlogin(id=0):
    searchform=SearchForm()
    form=GuestForm()
    
    if form.validate_on_submit():
        user.new(form.number.data,form.name.data,form.age.data,form.sex.data)
        sql_query("INSERT INTO Players VALUES(?,?,?,?,?,?,?)",(user.age,user.sex,user.name,'None', None, user.number, user.photo),commit=True)
        sql_query("INSERT INTO PartIn values(?,?)",(user.number, id),commit=True)
        sql_query("UPDATE Events SET num=num+1 WHERE id=?",(id,),commit=True)
        
        flash('You can now modify your info and make a password','warning')
        return redirect(url_for('account'))
    
    if searchform.is_submitted():
        data=search_for_events(searchform)
        return home_page()
    
    return render_template('guestlogin.html', title='Guest login', user=user, form=form, id=id, searchform=searchform)

@app.route('/delete_account', methods=['GET', 'POST'])
def deleteaccount():
    if(user.number==None):
        flash('You have to be logged in to enter that page', 'danger')
        return redirect('login')
    form=DeleteAccountForm()
    searchform=SearchForm()
    
    if form.validate_on_submit():
        if bcrypt.check_password_hash(user.password, form.password.data):
            sql_query("DELETE FROM Players WHERE number=?",(user.number,),commit=True)
            flash('Account deleted', 'warning')
            logout()
            return redirect(url_for('home_page'))
        
        else:
            flash('Password is wrong!', 'danger')
    
    return render_template('deleteaccount.html', title='Delete account', user=user, form=form, searchform=searchform)

def sql_query(q, args=None, commit=False, get_id=False):
    if args is None:
        args = []
    for attempt in range(10):
        try:
            con = sqlite3.connect("HobbiesDatabase3.db")
            cur = con.cursor()
            cur.execute(q, args)
            ans = cur.fetchall()
            if commit:
                con.commit()
            if get_id:
                ans=cur.lastrowid
            cur.close()
            con.close()
            del cur
            del con
            return ans
        except sqlite3.IntegrityError:
            return 2
        except sqlite3.OperationalError:
            time.sleep(1)
        
    return None

def save_picture(form_picture):
    _, f_ext = os.path.splitext(form_picture.filename)
    nimi=''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(20))
    picture_fn = nimi + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125, 125)
    kuva= Image.open(form_picture)
    kuva.thumbnail(output_size)
    kuva.save(picture_path)
    #pieni kuva
    picture_path = os.path.join(app.root_path, 'static/small_pics', picture_fn)
    pic= Image.open(form_picture)
    pic.thumbnail((62,62))
    pic.save(picture_path)

    return picture_fn

def verify_login(number, password):
    matches=sql_query("SELECT * FROM Players WHERE number=?",(number,))
    if matches:
        match=matches[0]
        user_password=match[4]
        if bcrypt.check_password_hash(user_password, password):
            user.login(number)
            return True
    
    return False

def search_for_events(searchform):
    field=searchform.searchfield.data
    num=searchform.num.data
    sport=searchform.sport.data
    start=searchform.start.data
    end=searchform.end.data
    place=searchform.place.data
    s1=searchform.search.data
    s2=searchform.search2.data
    
    primary=[]
    
    if field and s1:
        field='%'+field+'%'
        primary=sql_query("SELECT * FROM Events WHERE Header LIKE ? OR Description LIKE ?", (field,field))
    data=[]
    events=[]
    all=sql_query("SELECT * FROM Events;")
    for event in all:
        aika=event[5]
        if event not in primary and s2:
            events.append(event)
            if place!='None' and event[4]!=place:
                events.remove(event)
            elif num and int(num)>=int(event[7])-int(event[8]):
                events.remove(event)
            elif sport and event[2] not in sport:
                events.remove(event)
            elif start!='None' and int(aika[:2])<int(start):
                events.remove(event)
            elif end!='None' and int(aika[:2])>int(end):
                events.remove(event)

    events=events+primary
    for event in events:
        ev=[]
        players=[]
        list=sql_query("SELECT playerid FROM PartIn WHERE eventid=?;",(event[0],))
        ev.append(event)
        for i in list:
            player=sql_query("SELECT * FROM Players WHERE number=?;",(i[0],))
            if player:
                players.append(player[0])
        ev.append(players)
        data.append(ev)
    
    return data
  
verify_login(666, 'joo')

if __name__=="__main__":
    app.run(debug=True)