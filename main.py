from flask import Flask, render_template, g
from website import create_app

app = create_app()

@app.before_request
def before_request():
<<<<<<< HEAD
    ip_address = '10.1.80.199'
=======
    ip_address = '#.#.#.#'
>>>>>>> 64118003c07b97454f4f5e4f1de52452b9adb000
    g.ip_address = ip_address
    g.port = '####'

if __name__ == '__main__':
<<<<<<< HEAD
    ip_address = '10.1.80.199'
    port = 8000
=======
    ip_address = '#.#.#.#'
    port = ####
>>>>>>> 64118003c07b97454f4f5e4f1de52452b9adb000
    app.run(host=ip_address, port=port, debug=True)
