import fossilapp

uwsgi = False

application = fossilapp.app



if __name__ == "__main__":
    
    if uwsgi:
        application = fossilapp.app
    else:
        fossilapp.app.run(ssl_context = 'adhoc', host='120.0.0.1', port=9443)
        
