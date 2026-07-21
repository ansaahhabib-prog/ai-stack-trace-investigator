def divide_numbers(a, b):
    # This will cause a ZeroDivisionError if b is 0
    return a / b

def process_data(data):
    total = 0
    for item in data:
        # Expected a dictionary but gets a string in one case
        val = item['value']
        total = divide_numbers(total, val)
    return total

if __name__ == "__main__":
    my_data = [{'value': 10}, {'value': 0}, "this is a string"]
    print(process_data(my_data))
