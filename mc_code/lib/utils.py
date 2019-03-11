
def print_ids(ids):
    i = 0
    for id in ids:
        log(hex(id))

def debug(message, debug_mode):
    if debug_mode:
        print(message)


def log(message):
    print(message)
