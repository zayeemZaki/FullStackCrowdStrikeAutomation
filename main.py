from flask import Flask, render_template, g
from website import create_app

app = create_app()

@app.before_request
def before_request():
    ip_address = '#.#.#.#'
    g.ip_address = ip_address
    g.port = '####'

if __name__ == '__main__':
    ip_address = '#.#.#.#'
    port = ####
    app.run(host=ip_address, port=port, debug=True)
