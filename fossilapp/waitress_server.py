# pip install waitress
from waitress import serve

# under cmsimde import fossilapp
import fossilapp

# run cmsimde dynamic site with production waitress
serve(fossilapp.app, host='127.0.0.1', port=5001, url_scheme='https')