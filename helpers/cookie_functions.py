import pickle

def read_cookie(filename='cookie'):
    path  = f'./cookies/{filename}.pkl'
    cookie_file = open(path, 'rb')
    cookies = pickle.load(cookie_file)
    cookie_file.close()

    # print(cookies)
    cookie_str = ''
    csrf_token = ''
    for cookie in cookies:
        name = cookie['name']
        value = cookie['value']
        cookie_str += f'{name}={value}; '
        
        if name == 'csrftoken':
            csrf_token = value

    # print(cookie_str)
    # print(csrf_token)
    return cookie_str, csrf_token
