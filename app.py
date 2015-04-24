#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request, send_from_directory

import logging
from logging import Formatter, FileHandler

import arxiverfunc
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/', methods=['POST', 'GET'])
def home():
    idname = request.args.get('id')
    if idname:
        data = arxiverfunc.arxiverprocess(idname)
#        data = {'fig1': 'temp/1306.3227_f6.jpg',
#                'fig2': 'hello',
#                'fig3': 'bye'}
        print(data)
        return render_template('pages/home.html', adata=data)
    return render_template('pages/home.html')

@app.route('/temp/<path:path>')
def files(path):
    print(path)
    return send_from_directory('./temp/', path)


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
