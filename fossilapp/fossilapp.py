#from flask import Flask, request
# import from flask
from flask import Flask, request, redirect, url_for, flash, \
                render_template, session, make_response
                           
# for authomatic
from authomatic.adapters import WerkzeugAdapter
from authomatic import Authomatic

# from config.py 導入 CONFIG and CALLBACK_URL
from config import CONFIG
from config import CALLBACK_URL

# for generating secret_key
import os
import time

# for mako template engine
# for mako template 系統
from mako.template import Template
from mako.lookup import TemplateLookup

# for login_required
from functools import wraps

# all setup in config.py
import config

# Instantiate Authomatic.
# generate secret string randomly
secret = os.urandom(24).hex()
authomatic = Authomatic(CONFIG, secret, report_errors=False)

# 確定程式檔案所在目錄, 在 Windows 有最後的反斜線
_curdir = os.path.join(os.getcwd(), os.path.dirname(__file__))
template_root_dir = _curdir + "/templates"

app = Flask(__name__)

# 使用 session 必須要設定 secret_key
# In order to use sessions you have to set a secret key
# set the secret key.  keep this really secret:
secret_key = os.urandom(24).hex()
app.secret_key = secret_key

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'login' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('index'))

    return wrap
@app.route('/')
# root of the system can not set "login_required" decorator
# 開始改用 Make 作為 Template
def index():
    template_lookup = TemplateLookup(directories=[template_root_dir])
    indexTemplate = template_lookup.get_template("index.html")
    return indexTemplate.render()
@app.route("/menu")
@login_required
def menu():
    menuList = ["form"]
    template_lookup = TemplateLookup(directories=[template_root_dir])
    menuTemplate = template_lookup.get_template("menu.html")
    return menuTemplate.render(menuList=menuList)
@app.route('/login/<provider_name>/', methods=['GET', 'POST'])
def login(provider_name):
    
    # We need response object for the WerkzeugAdapter.
    response = make_response()
    
    # Log the user in, pass it the adapter and the provider name.
    result = authomatic.login(WerkzeugAdapter(request, response), provider_name)
    
    # If there is no LoginResult object, the login procedure is still pending.
    if result:
        if result.user:
            # We need to update the user to get more info.
            result.user.update()
        
        # use session to save login user's email (試著將 @ 換為 _at_)
        #session['loginEmail'] = result.user.email.replace('@', '_at_')
        '''
        loginUser = result.user.email.split("@")[0]
        session["user"] = loginUser
        session["login"] = True
        template_lookup =
        '''
        # only get the string before @
        loginUser = result.user.email.split("@")[0]
        loginDomain = result.user.email.split("@")[1]
        
        # only kmoler can login
        #kmoler = ["scrum2"]
        #if loginUser in kmoler:
        
        # only @gm.nfu.edu.tw can login
        if loginDomain == "gm.nfu.edu.tw":
            session["user"] = loginUser
            session["login"] = True
            template_lookup = TemplateLookup(directories=[template_root_dir])
            loginTemplate = template_lookup.get_template("login.html")
    
            return loginTemplate.render(result=result, CALLBACK_URL=CALLBACK_URL)
        else:
            return "Sorry, you are not allowed to login."

    # Don't forget to return the response.
    return response
@app.route('/logout')
def logout():
    session.pop('login' , None)
    session.pop('user', None)
    flash('Logged out!')
    return redirect(url_for('index'))
@app.route("/hello")
@login_required
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"

@app.route('/form')
@login_required
def form():
    """Create form routine"""
    
    # get user student number from session
    loginUser = session.get('user')
    
    output = "<html><body><h1>Create Fossil SCM Repository</h1><form method='post' action='genAccount'>"
    output += "Please set the password for your Fossil SCM repository: "
    output += loginUser + "<br \><br \>"
    output += "Password:<input type='password' name='password'><br \><br \> "
    output += "Retype Password:<input type='password' name='password2'><br \><br \> "
    output += "<input type='submit' value='Create Repository'></form></section></div></body></html>"
    
    return output
    
    
@app.route('/form2')
@login_required
def form2():
    """Create form routine to replace existed repository"""
    
    # get user student number from session
    loginUser = session.get('user')
    
    output = "<html><body><h1>Recreate Fossil SCM Repository</h1><form method='post' action='genAccount'>"
    output += "Notice!! Your previous repository will be replaced! Please set the password for your new Fossil SCM repository: "
    output += loginUser + "<br \><br \>"
    output += "<input type='hidden' name='replaced' value='yes'>"
    output += "Password:<input type='password' name='password'><br \><br \> "
    output += "Retype Password:<input type='password' name='password2'><br \><br \> "
    output += "<input type='submit' value='Create Repository'></form></section></div></body></html>"
    
    return output
@app.route('/genAccount', methods=['POST'])
@login_required
def genAccount():

    """Generate Fossil SCM account
    """
    # get user input account and password
    #account = request.form["account"]
    # get user student number from session
    loginUser = session.get('user')
    account = loginUser
    password = request.form["password"]
    password2 = request.form["password2"]
    try:
        replaced = request.form["replaced"]
    except:
        replaced = "No"
    
    # Check if two password matched
    if password != password2:
        warning = "Passwords  do not match!<br \>"
        warning += "Please go back and retype!"
        return warning
    
    # To avoid shell command injection, accept only numbers for Account
    '''
    # get user account from session
    if account.isdigit():
        pass
    else:
        return "Accept only numbers for Account!"
    '''
    
    # To avoid shell command injection, no special characters allowed for Password
    for i in range(len(password)):
        if password[i] in ["&", "|", ";", "$",">", "<", "`", "\\","!"]:
            return "No special characters allowed for Password!"
    
    # repository location path
    #path = "/home/yen/repository/u/"
    #path = "C:/pj2022/multi_repo/"
    path = config.repo_path
    
    output = ""
    
    # copy fossil repository from template.fossil
    command1 = "copy " + path + config.template_repo + ".fossil "  + path + account + ".fossil"
    output += command1 + "<br />"
    
    # add account as the repository user which need to force user use student number as account
    command2 = config.fossil_command + " user new " + account + " " + account + "@gm.nfu.edu.tw " + password + " -R " + path + account + ".fossil"
    output += command2 + "<br />"
    
    # set account to be administrator which capability is "s" (setup)
    command3 = config.fossil_command + " user capabilities " + account + " s"  + " -R " + path + account + ".fossil"
    output += command3 + "<br />"
    
    # change the origin "cd" account capabilities to none which is a vacant string " "
    command4 = config.fossil_command + " user capabilities " + config.template_account + " \" \" " + " -R " + path + account + ".fossil"
    output += command4 + "<br />"
    output += "<br\><br \>"
    
    # change directory to user repository path
    os.system("cd " + path)
    
    # execute command1
    # check if repository exist
    if replaced != "yes":
        if os.path.exists(path + account + ".fossil"):
            return "Error! 倉儲已經存在! <br /><br /> 假如要取代先前的倉儲, 請前往<a href='/form2'>建立新倉儲</a><br />"
    try:
        os.system(command1)
        output += "command1 completed <br />"
    except:
        return "Error! can not create repository! <br />"
        
    
    # wait for 0.1 second
    time.sleep(0.1)
    
    # execute command2
    try:
        os.system(command2)
        output += "command2 completed <br />"
    except:
        output += "command2 failed<br \>"
    
    # wait for 0.1 second
    time.sleep(0.1)
    
    # execute command3
    try:
        os.system(command3)
        output += "command3 completed <br />"
    except:
        output += "command3 failed <br \>"
    
    # wait for 0.1 second
    time.sleep(0.1)
    
    # execute command4
    try:
        os.system(command4)
        output += "command4 completed <br />"
    except:
        output += "command4 failed<br \>"
    
    # return command for debug
    #return output

    return "Repository: " + account + " created!<br /><br \>" + \
    "Link to repository: <a href='https://" + config.domain_name + ":" + config.fossil_port + "/" +account + "'>" + \
    account + "</a>"

    '''
    return "account:" + account+"<br />" \
    + "password:" + password
    '''
if __name__ == "__main__":
    app.run(host='0.0.0.0')