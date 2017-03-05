import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, \
    flash
from werkzeug import secure_filename
app = Flask(__name__)


# This is the path to the upload directory
my_dir = os.path.dirname(__file__)
data_path = os.path.join(my_dir, 'uploads/')
app.config['UPLOAD_FOLDER'] = data_path

# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'csv', 'xlsx', 'xls'}


# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    """
    :rtype: object
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/upload')
def upload_file():
    files = make_tree(app.config['UPLOAD_FOLDER'])
    return render_template('upload.html', files=files)


@app.route('/uploader', methods=['POST'])
def process_file():
    # Get the name of the uploaded file
    file = request.files['file']
    # Check if the file is one of the allowed types/extensions
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)
        # Move the file form the temporal folder to
        # the upload folder we setup
        try:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        except:
            print 'File not valid'
            pass

        # Redirect the user to the upload page
        return redirect(url_for('upload_file'))


# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)



#list the files which are in directories and subdirectories.
def make_tree(path):
    try: lst = os.listdir(path)
    except OSError:
        pass #ignore errors
    else:
        return lst

    return []



if __name__ == '__main__':
    app.run()
