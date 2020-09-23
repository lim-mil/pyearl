from pyearl import Pyearl


app = Pyearl()


@app.route('/index', methods=['GET'])
def index(request):
    return "hhhhh"


app.run()
