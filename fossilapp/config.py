import authomatic
from authomatic.providers import oauth2

CALLBACK_URL = "https://pj5073.cycu.org:9443/menu"

# read client_id and client_secret from safe place other than put into script
# current setting only allow @gm user login
keyFile = open('./../pj5073.cycu_org.txt', 'r')
with open('./../pj5073.cycu_org.txt', 'r') as f:
    key = f.read().splitlines()

CONFIG = {
        'google': {
            'class_': oauth2.Google,
            'consumer_key': key[0],
            'consumer_secret': key[1],
            'scope': oauth2.Google.user_info_scope
        }
    }

domain_name = "pj5073.cycu.org"
default_repo = "default"
template_repo = "template"
template_account = "pj2022"
# for Windows 
repo_path = "c:\\pj2022\\repo\\multi_repo\\"
# for Ubuntu
#repo_path = "/home/wcm2021/multi_repository/"
fossil_command = "c:\\pj2022\\fossil.exe"
fossil_port = "5443"
flask_port = "9443"
uwsgi = True

# derived
default_repo_path = repo_path+default_repo+".fossil"
template_repo_path = repo_path+template_repo+".fossil"
flask_url = "https://"+domain_name+":"+flask_port
flask_menu = "https://"+domain_name+":"+flask_port+"/menu"
login_url = "https://"+domain_name+":"+fossil_port+"/"+default_repo+"/login"
menu_url = "https://"+domain_name+":"+flask_port+"/menu"
CALLBACK_URL = flask_menu