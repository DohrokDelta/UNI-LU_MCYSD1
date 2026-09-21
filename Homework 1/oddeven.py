# Write a Python script that counts the number of letters in a string (use at least three fixed strings for testing),
# and returns "Yes" if it is odd and "No" if it is even.

def check_word_length(word):
    #Check if odd (Yes) or even (No)
    return "Yes" if len(word) % 2 == 1 else "No"

def run_tests():
    #Three fixed strings for testing mode
    test_words = ["Hello", "Python", "Homework"]
    print("Running test with hard-coded strings")
    for word in test_words:
        result = check_word_length(word)
        print(f" '{word}' ({len(word)} letters): {result}")

if __name__ == "__main__":
    import sys
    #Test command for user
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
    #Regular process for user (check word length)
    elif len(sys.argv) > 1:
        word = sys.argv[1]
        result = check_word_length(word)
        print(result)
    else:
        print ("Instructions:\n")
        print ("Check word: python oddeven.py <word>\n")
        print ("Run tests: python oddeven.py --test\n")
