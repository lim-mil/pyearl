from pyearl import Pyearl
from pyearl.template import render


app = Pyearl()


@app.route('/index', methods=['GET'])
def index(request):
    print(dir(request))
    return render('templates/test.html', {'name': 'lim'})


@app.route('/login', methods=['POST'])
def login(request):
    print(dir(request))
    return 'hello'


app.run(port=7331)
