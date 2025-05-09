
def error_msg(function, text):
# Print error message and exit!
    msg_str = "  [!|%s] "%(function)
    msg_str += text
    print(msg_str)
    exit()

def info_msg(function, text):
# Print information message, as a warning
    msg_str = "  [%s] "%(function)
    msg_str += text
    print(msg_str)

def check_list_has_one_element(list_of_elements, function, default_value = "",
                               show_example = "", is_error = False):
# Print error or info message if a list doesn't have a single element!
    msg = ""
    if (not list_of_elements):
        msg = "Missing element."
        if default_value:
            msg += " Using %s as default!"%(default_value)
            show_example = False
            is_error = False
    elif len(list_of_elements) > 1:
        msg = "Use one element only."
        is_error = True
        msg += " You introduced %s."%(list_of_elements)

    if msg:
        if show_example:
            msg += " (Ex. %s.)"%(show_example)
        if is_error:
            error_msg(function, msg)
        else:
            info_msg(function, msg)
