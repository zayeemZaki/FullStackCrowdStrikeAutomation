from website import create_app

app = create_app()

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='10.2.128.33', port=8000, debug=True)

