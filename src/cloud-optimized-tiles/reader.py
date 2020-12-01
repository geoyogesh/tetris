import os
import io
import pathlib

def main():
    script_dir = os.path.dirname(__file__)
    ext = os.path.join(script_dir, r'data/county.pbf')
    total_bytes = os.path.getsize(ext)
    print ('total bytes:' ,total_bytes)
    with open(ext, "rb") as binary_file:
        binary_file.seek(total_bytes-8)
        last_tile_begin_binary = binary_file.read(4)
        last_tile_begin = int.from_bytes(last_tile_begin_binary, byteorder='big')
        print(last_tile_begin, last_tile_begin_binary)
        last_tile_size_binary = binary_file.read(4)
        last_tile_size = int.from_bytes(last_tile_size_binary, byteorder='big')
        print(last_tile_size, last_tile_size_binary)

        # read complete catalog
        catalog_begin_offset = last_tile_begin + last_tile_size
        print ('catalog_begin_offset', catalog_begin_offset)
        binary_file.seek(catalog_begin_offset)
        tile_tuples = []
        while (True):
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
        first_tile = tiles['0-0-0']
        binary_file.seek(first_tile[0])
        file_binary = binary_file.read(first_tile[1])
        with open(os.path.join(script_dir, r'data/0.pbf'), "wb") as binary_file:
            binary_file.write(file_binary)

if __name__ == '__main__':
    main()