from os import listdir
from os.path import isfile, isdir, getsize, join


def get_dir_size(path: str) -> int:
    if isfile(path):
        return getsize(path)
    else:
        size = 0
        for file_name in listdir(path):
            p = join(path, file_name)
            if isfile(p):
                size += getsize(p)
            elif isdir(p):
                size += get_dir_size(p)
            else:
                pass    # Skip everything else
        return size

getsize('/tmp/.X11-unix')
print(get_dir_size('/home/corvis/Documents'))

# Questions -> Exceptions what are the cases?
# IsFile -> What if it's not a file and not dir (links, block devices, sockets)?
# Recursion depth