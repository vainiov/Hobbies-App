from flask import Flask, render_template, url_for, flash, redirect, request

app=Flask(__name__)

@app.route('/')
@app.route('/home')
def home_page():
    return render_template("mainpage.html")






if __name__=="__main__":
    app.run(debug=True)