import re

def formatted_number_with_comma(number):
    return ("{:,}".format(number))

def numbers_within_text(text):
    numbers = re.findall(r'\b\d+\b', text)
    for i in range(len(numbers)):
        numbers[i] = int(numbers[i])
    return numbers

def str_to_int(text, decimal_point = 0):
    text = text.replace(',', '')
    text = text.strip()
    
    number = float(text)
    if decimal_point:
        return round(number, decimal_point)
    else:
        return int(number)