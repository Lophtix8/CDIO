import os

def main():
    tests_to_run = [test for test in os.listdir() if test != "unittests.py" or not test.endswith(".py")]
    for test in tests_to_run:
        os.system(f"python {test}")

if __name__ == "__main__":
    main()
