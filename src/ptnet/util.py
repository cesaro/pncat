
def size_to_human (size) :
    # bytes
    if size < 1100 :
        return "%d bytes" % size

    # kb
    size = size / 1024.0
    if size < 10 :
        # < 10K
        return "%.1fK" % size
    elif size < 1024 :
        # > 10K
        return "%dK" % size

    # Mb
    size = size / 1024.0
    if size < 100 :
        # < 100M
        return "%.1fM" % size
    elif size < 1024 :
        # > 10M
        return "%dM" % size

    # Gb
    size = size / 1024.0
    return "%.1fG" % size
