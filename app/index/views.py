@index.route('/', methods=['GET'])
@index.route('/index', methods=['GET'])
def index():
    return render_template('index.html')

@index.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')


@index.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('contact.html')


@index.route('/terms', methods=['GET', 'POST'])
def terms():
    return render_template('terms.html')
