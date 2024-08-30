def extract_important_info(text: str, is_closed: bool):
    important_line_names_to_numbers_mapper = {
        "id": 0,
        "country": 1,
        "registery_date": 2,
        "balance": 6,
        "deposits_count": 7,
        "deposits_sum": 8,
        "withdrawal_count": 11,
        "withdrawal_sum": 12,
        "turnover_clear": 16,
        "vol_share": 19,
    }
    if is_closed:
        important_line_names_to_numbers_mapper = {
            "id": 0,
            "country": 1,
            "registery_date": 2,
            "balance": 7,
            "deposits_count": 8,
            "deposits_sum": 9,
            "withdrawal_count": 12,
            "withdrawal_sum": 13,
            "turnover_clear": 17,
            "vol_share": 20,
        }
    all_lines = text.split("\n")
    important_lines = []

    for line_number in important_line_names_to_numbers_mapper.values():
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

    return important_lines
