from flask import Flask, render_template, g
from website import create_app

app = create_app()

@app.before_request
def before_request():
    ip_address = '10.1.80.199'
    g.ip_address = ip_address
    g.port = '8000'

if __name__ == '__main__':
    ip_address = '10.1.80.199'
    port = 8000
    app.run(host=ip_address, port=port, debug=True)
