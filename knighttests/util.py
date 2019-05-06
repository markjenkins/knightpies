from tempfile import NamedTemporaryFile

def get_closed_named_temp_file():
    return_file = NamedTemporaryFile(delete=False)
    return_file.close()
    return return_file.name
