import flask
from flask_cors import CORS
import io
import requests
from flask_api import status

app = flask.Flask(__name__)
app.config["DEBUG"] = True
CORS(app)
cors = CORS(app, resources={r"/tiles/*": {"origins": "*"}})
tiles = None

@app.route('/', methods=['GET'])
def home():
    return "<h1>Distant Reading Archive</h1><p>This site is a prototype API for distant reading of science fiction novels.</p>"


def inilitize(layer):
    global tiles

    if tiles:
        return
    
    url = f'http://nginx/{layer}.pbf'
    headers = {"Range": "bytes=-8"}
    r = requests.get(url, headers=headers)
    binary_file = io.BytesIO(r.content)
    last_tile_begin_binary = binary_file.read(4)
    last_tile_begin = int.from_bytes(last_tile_begin_binary, byteorder='big')
    print(last_tile_begin, last_tile_begin_binary)
    last_tile_size_binary = binary_file.read(4)
    last_tile_size = int.from_bytes(last_tile_size_binary, byteorder='big')
    print(last_tile_size, last_tile_size_binary)

    # read complete catalog
    catalog_begin_offset = last_tile_begin + last_tile_size
    print ('catalog_begin_offset', catalog_begin_offset)
    headers = {"Range": f"bytes={catalog_begin_offset}-"}
    r_catalog = requests.get(url, headers=headers)
    total_bytes = len(r_catalog.content)
    binary_file = io.BytesIO(r_catalog.content)
    tile_tuples = []
    while True:
        z = int.from_bytes(binary_file.read(1), byteorder='big')
        x = int.from_bytes(binary_file.read(4), byteorder='big')
        y = int.from_bytes(binary_file.read(4), byteorder='big')
        begin_offset = int.from_bytes(binary_file.read(4), byteorder='big')
        size = int.from_bytes(binary_file.read(4), byteorder='big')
        #print (z, x, y, begin_offset, size)
        tile_tuples.append((f'{z}-{x}-{y}', [begin_offset, size]))
        if binary_file.tell() == total_bytes:
            break
    tiles = dict(tile_tuples)

@app.route('/tiles/<layer>/<z>/<x>/<y>.pbf', methods=['GET'])
def my_view_func(layer, z: int, x: int, y: int):

    inilitize(layer)

    key = f'{z}-{x}-{y}'
    if not tiles or key not in tiles:
        return '', status.HTTP_404_NOT_FOUND
    sp = tiles[key]

    url = f'http://nginx/{layer}.pbf'
    headers = {"Range": f'bytes={sp[0]}-{sp[0] + sp[1] - 1}'}
    r = requests.get(url, headers=headers)
    return flask.Response(r.content, mimetype='application/octet-stream')

if __name__ == '__main__':
      app.run()