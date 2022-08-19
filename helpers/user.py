import string
import random
import os
from os import listdir
from os.path import isfile, join

from helpers.files import read_txt
from helpers.username import UsernameGenerator

def randomize(option, length):
    # Options:
    #       -p      for letters, numbers and symbols
    #       -l      for letters only
    #       -n      for numbers only
    #       -m      for month selection
    #       -d      for day selection
    #       -y      for year selection
    #       -g      for gender

    if option == '-p':
        string._characters_='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()_+'
    elif option == '-l':
        string._characters_='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    elif option == '-n':
        string._characters_='1234567890'


    if option == '-d':
        _generated_info_=random.randint(1,28)
    elif option == '-m':
        _generated_info_=random.randint(1,12)
    elif option == '-y':
        _generated_info_=random.randint(1950,2000)
    elif option == '-g':
        _generated_info_=random.randint(1,3)
    else:
        _generated_info_=''
        for _counter_ in range(0,length) :
            _generated_info_= _generated_info_ + random.choice(string._characters_)

    return _generated_info_

def generate_user_info():
    ug = UsernameGenerator(8, 12)
    random_user = {}
    
    random_user['f_name'] = randomize('-l',5)
    random_user['l_name'] = randomize('-l',7)
    random_user['username'] = ug.generate()
    random_user['password'] = randomize('-p',16)
    random_user['email'] = str.lower(randomize('-l', 7) + randomize('-n', 3)) + '@gmail.com'
    random_user['month'] = randomize('-m',1)
    random_user['day'] = randomize('-d',1)
    random_user['year'] = randomize('-y',1)
    # gender= randomize('-g',1)
    
    return random_user

def get_acc_info():
    users = read_txt('names.txt')
    data = []
    for user in users:
        user = generate_user_info(user)
        images = [f for f in listdir('images') if isfile(join('images', f))]
        index = random.randint(0,len(images)-1)
        image = os.path.abspath(os.getcwd()) + '\images\\' + images[index]
        user['img'] = image
        data.append(user)
    return data