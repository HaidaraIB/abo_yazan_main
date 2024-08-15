def extract_important_info(text: str, is_closed:bool):
    important_line_numbers = [0, 1, 2, 4, 6, 7, 8, 11, 16, 19]
    if is_closed:
        important_line_numbers = [0, 1, 2, 4, 7, 8, 9, 12, 17, 20]
    all_lines = text.split("\n")
    important_lines = []
    
    for line_number in important_line_numbers:
        try:
            important_lines.append(all_lines[line_number].split("#")[1].strip())
        except IndexError:
            try:
                important_lines.append(all_lines[line_number].split("$")[1].strip())
            except IndexError:
                try:
                    important_lines.append(all_lines[line_number].split(":")[1].strip())
                except:
                    pass

    important_lines[2] = important_lines[2][:-1]
    important_lines[-1] = f"{(float(important_lines[-1]) * 0.4):.2f}"

    return "/".join(important_lines)
