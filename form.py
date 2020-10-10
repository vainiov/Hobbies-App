#-*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, FileField, TextAreaField, SelectField, SelectMultipleField, RadioField, widgets
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_wtf.file import FileAllowed
import sqlite3

class user():
    def __init__(self):
        self.age=None
        self.sex=None
        self.name=None
        self.bio=None 
        self.password=None
        self.number=None
        self.photo=None
    def login(self,number):
        #also as update
        ans=sql_query("SELECT * FROM Players WHERE number=?",(number,))
        ree=ans[0]
        self.age=ree[0]
        self.sex=ree[1]
        self.name=ree[2]
        self.bio=ree[3] 
        self.password=ree[4]
        self.number=number
        self.photo=ree[6]
    def logout(self):
        self.age=None
        self.sex=None
        self.name=None
        self.bio=None 
        self.password=None
        self.number=None
        self.photo=None
    def new(self,number,name,age,sex):
        self.age=age
        self.sex=sex
        self.name=name
        self.number=number
        self.photo='default.png'
        if self.sex=='Female':
            self.photo='default2.png'
        
        
user=user()

class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class SearchForm(FlaskForm):
    stime=[(None, 'Starts...')]
    etime=[(None, 'Ends...')]
    for i in range(24):
        stime.append((i, "{:d}:00".format(i)))
        etime.append((i, "{:d}:00".format(i)))
        
    searchfield=StringField()
    num=RadioField('Open positions', choices=[(1,1),(2,2),(3,3),(4,'more')])
    sport=MultiCheckboxField('Sport', choices=[('Football', 'Football'), ('Ice hockey', 'Ice hockey'), ('Basketball', 'Basketball'),('Tennis', 'Tennis'),('Baseball', 'Baseball'),('Other', 'Other')])
    start=SelectField(choices=stime)
    end=SelectField(choices=etime)
    place=SelectField('Place', choices=[(None, 'Place'),('Helsinki','Helsinki'),('Espoo','Espoo'),('Vantaa','Vantaa'),('Tampere','Tampere')])
    search=SubmitField('Search')
    search2=SubmitField('Search')

class EventForm(FlaskForm):
    header=StringField('Header', validators=[DataRequired()])
    sport=SelectField('Sport', choices=[('0','Choose your sport...'),('Football', 'Football'), ('Ice Hockey', 'Ice hockey'), ('Basketball', 'Basketball'),('Tennis', 'Tennis'),('Baseball', 'Baseball'),('Other', 'Other')])
    place=StringField('Place', validators=[DataRequired()])
    city=SelectField('City', choices=[('Helsinki','Helsinki'),('Espoo','Espoo'),('Vantaa','Vantaa'),('Tampere','Tampere')])
    time=StringField('Time', validators=[DataRequired()])
    description=TextAreaField('Short description of your crew and your skills', validators=[DataRequired()])
    limit=IntegerField('Max players', validators=[DataRequired()])
    number=StringField('Phone number', validators=[DataRequired()])
    submit=SubmitField('Create an event')
    
class EventForm2(FlaskForm):
    header=StringField('Header', validators=[DataRequired()])
    sport=SelectField('Sport', choices=[('0','Choose your sport...'),('Football', 'Football'), ('Ice hockey', 'Ice hockey'), ('Basketball', 'Basketball'),('Tennis', 'Tennis'),('Baseball', 'Baseball'),('Other', 'Other')])
    place=StringField('Place', validators=[DataRequired()])
    city=SelectField('City', choices=[('Helsinki','Helsinki'),('Espoo','Espoo'),('Vantaa','Vantaa'),('Tampere','Tampere')])
    time=StringField('Time', validators=[DataRequired()])
    description=TextAreaField('Short description of your crew and your skills', validators=[DataRequired()])
    limit=IntegerField('Max players', validators=[DataRequired()])
    submit=SubmitField('Create an event')

class AccountForm(FlaskForm):
    name=StringField('Name', validators=[DataRequired()])
    age=IntegerField('Age', validators=[DataRequired()])
    sex=SelectField('Gender', choices=[('0','Gender'),('Male', 'Male'), ('Female', 'Female')])
    bio=TextAreaField('Short description of your skills', validators=[DataRequired()])
    number=StringField('Phone number')
    photo=FileField('Photograph', validators=[FileAllowed(['jpg','png'])])
    password=PasswordField('Password')
    password2=PasswordField('Confirm password', validators=[EqualTo('password')])
    submit=SubmitField('Create an account')
    
    def validate_number(self, number):
        if sql_query("SELECT * FROM Players WHERE number=?",(number.data,)):
            raise ValidationError('That number has already an account!')

class LoginForm(FlaskForm):
    number=IntegerField('Phone number',validators=[DataRequired()])
    password=PasswordField('Password',validators=[DataRequired()])
    submit=SubmitField('Login')

class AccountInfoForm(FlaskForm):
    name=StringField('Name', validators=[DataRequired()])
    age=IntegerField('Age', validators=[DataRequired()])
    sex=SelectField('Gender', choices=[('0','Gender'),('Male', 'Male'), ('Female', 'Female')])
    bio=TextAreaField('Short description of your skills', validators=[DataRequired()])
    photo=FileField('Upload a new profile picture', validators=[FileAllowed(['jpg','png'],'Images only')])
    password=PasswordField('Password')
    submit=SubmitField('Save changes')
    
class GuestForm(FlaskForm):
    number=IntegerField('Phone number', validators=[DataRequired()])
    name=StringField('Name', validators=[DataRequired()])
    age=IntegerField('Age', validators=[DataRequired()])
    sex=SelectField('Gender', choices=[('0','Gender'),('Male', 'Male'), ('Female', 'Female')])
    submit=SubmitField('Join as a guest')
    
    def validate_number(self, number):
        if sql_query("SELECT * FROM Players WHERE number=?",(number.data,)):
            raise ValidationError('That number has already an account!')
    
class ChangePasswordForm(FlaskForm):
    old=PasswordField('Old password')
    new=PasswordField('New password',validators=[DataRequired()])
    conf=PasswordField('Confirm new password',validators=[DataRequired(), EqualTo('new')])
    submit=SubmitField('Change password')
    
class DeleteAccountForm(FlaskForm):
    password=PasswordField('Enter password',validators=[DataRequired()])
    submit=SubmitField('Delete account')


def sql_query(q, args=None, commit=False):
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
                cur.close()
                con.close()
                del cur
                del con
                return ans
            except sqlite3.IntegrityError:
                return 2
            except sqlite3.OperationalError:
                time.sleep(3)
            
        return None


