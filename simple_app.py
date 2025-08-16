from flask import Flask, render_template

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate')
def translate():
    return render_template('translate.html')

@app.route('/learn')
def learn():
    # Mock video data for the learn page
    videos = ['hello', 'how_are_you', 'forget', 'remember', 'i_want', 'my_name_is', 'thank_you', 'same_to_you', 'you']
    return render_template('learn.html', videos=videos)

if __name__ == '__main__':
    app.run(debug=True, port=5000)