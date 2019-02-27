import pickle

def write_to_file(filename, data):
    '''
    :param filename: name of the file; created in current dir as filename
    :param data: data to be written to file
    :return: True if successful, False if not
    ???file can be opened with: with openFile(filename)
    '''
    try:
        with open('%s' % filename, 'wb') as outfile:
            pickle.dump(data, outfile)
    except Exception as err:
        print(err)
        return False

    return True

def open_file(filename):
    '''
    :param filename: file to be opened
    :return: same data as writeToFile(data)
    '''
    try:
        with open('%s' % filename, 'rb') as infile:
            data = pickle.load(infile)

        return data
    except Exception as err:
        print(err)
        return False