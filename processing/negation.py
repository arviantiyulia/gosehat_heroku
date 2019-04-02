def remove_negation(input):
    print("input negation = ", input)
    input_negation = []
    for i in range(len(input)):
        input_before = input[i-1]
        input_after = input[i]

        if input_before == "tidak":
            input.remove(input_after)
            input.remove(input_before)

    print("input_new", input)
    return input