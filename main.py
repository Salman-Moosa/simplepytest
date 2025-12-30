import os

def check_number(number):
    """
    Check if a number is positive, negative, or zero.
    """
    if number > 0:
        return f"{number} is POSITIVE"
    elif number < 0:
        return f"{number} is NEGATIVE"
    else:
        return f"{number} is ZERO"

def main():

    number_str = os.getenv('TEST_NUMBER')
    if number_str is None:
        try:
            number_str = input("Enter a number: ")
        except EOFError:
            print("ERROR: No input provided and TEST_NUMBER not set")
            return

    try:
        number = float(number_str)
        result = check_number(number)
        print(result)
    except ValueError:
        print("ERROR: Please enter a valid number")

if __name__ == "__main__":
    main()