from datetime import datetime

thai_months = [
    "", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
]

thai_numbers = {
    "0": "๐", "1": "๑", "2": "๒", "3": "๓", "4": "๔",
    "5": "๕", "6": "๖", "7": "๗", "8": "๘", "9": "๙"
}

def to_thai_numerals(number):
    return "".join(thai_numbers[digit] for digit in str(number))

def format_thai_date(dt):
    if not isinstance(dt, datetime):
        return dt
    buddhist_year = dt.year + 543
    month_name = thai_months[dt.month]
    return f"{dt.day} {month_name} {buddhist_year}"

def format_thai_date_with_thai_numerals(dt):
    if not isinstance(dt, datetime):
        return dt
    buddhist_year = dt.year + 543
    month_name = thai_months[dt.month]
    day_thai = to_thai_numerals(dt.day)
    year_thai = to_thai_numerals(buddhist_year)
    return f"{day_thai} {month_name} {year_thai}"

def format_eng_date(dt):
    return dt.strftime("%B %-d, %Y")
