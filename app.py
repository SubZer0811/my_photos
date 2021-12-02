
from flask import Flask
from flask import request
from flask import render_template
from flask import send_from_directory
import os
import glob
import sys
import binascii
import argparse


app = Flask("MyPhotos")
app.config['IMAGE_EXTS'] = [".png", ".jpg", ".jpeg", ".gif", ".tiff", ".JPG", ".PNG", ".JPEG", ".GIF", ".TIFF"]


def encode(x):
    return binascii.hexlify(x.encode('utf-8')).decode()

def decode(x):
    return binascii.unhexlify(x.encode('utf-8')).decode()


@app.route('/')
def home():
    root_dir = app.config['ROOT_DIR']
    image_paths = []
    for root,dirs,files in os.walk(root_dir):
        for file in files:
            if any(file.endswith(ext) for ext in app.config['IMAGE_EXTS']):
                image_paths.append(encode(os.path.join(root,file)))
    print(image_paths)
    return render_template('index.html', paths=image_paths)


@app.route('/cdn/<path:filepath>')
def download_file(filepath):
    dir,filename = os.path.split(decode(filepath))
    return send_from_directory(dir, filename, as_attachment=False)


if __name__=="__main__":
    
    path=(os.path.join(os.getcwd(), 'images')).replace('\\','/')
    app.config['ROOT_DIR'] = path
    print("path: "+path)
    app.run(debug=True)