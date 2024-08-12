from website import create_app

app = create_app()

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='192.168.12.158', port=8000, debug=True)

