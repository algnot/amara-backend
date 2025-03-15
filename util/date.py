from datetime import datetime

thai_months = [
    "", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
]

def format_thai_date(dt):
    if not isinstance(dt, datetime):
        return dt
    buddhist_year = dt.year + 543  # Convert to Buddhist year
    month_name = thai_months[dt.month]  # Get Thai month name
    return f"{dt.day} {month_name} {buddhist_year}"

def format_eng_date(dt):
    return dt.strftime("%B %-d, %Y")
