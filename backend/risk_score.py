def calculate_risk(pii):

    score = 0

    if pii["aadhaar"]:
        score += 5
    if pii["pan"]:
        score += 4
    if pii["phone"]:
        score += 3
    if pii["email"]:
        score += 2

    if score >= 6:
        return "HIGH"
    elif score >= 3:
        return "MEDIUM"
    else:
        return "LOW"