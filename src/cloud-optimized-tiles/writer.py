import os
import io
import pathlib

def main():
    script_dir = os.path.dirname(__file__)
    ext = os.path.join(script_dir, r'data/county.pbf')
    file_path3 = os.path.join(script_dir, r'data/tiles/vector-tile-example/')
    p = pathlib.Path(file_path3)
    s = [[int(item.parts[-3]), int(item.parts[-2]), int(item.parts[-1].split('.')[0]), item.stat().st_size, item ] for item in list(p.glob('**/*.pbf'))]
    
    with open(ext, "wb") as binary_file:
        for i in s:
            binary_file.write(i[4].read_bytes())
        f_size = 0
        for i in s:
            binary_file.write(i[0].to_bytes(1, byteorder='big', signed=True))
            binary_file.write(i[1].to_bytes(4, byteorder='big', signed=True))
            binary_file.write(i[2].to_bytes(4, byteorder='big', signed=True))
            binary_file.write(f_size.to_bytes(4, byteorder='big', signed=True))
            binary_file.write(i[3].to_bytes(4, byteorder='big', signed=True))
            f_size += i[3]


if __name__ == '__main__':
    main()