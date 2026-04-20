def increment_order_code(order_code):
    """
    Increment order code like order00001 -> order00002
    :param order_code: Input order code (e.g., order00001)
    :return: Next order code (e.g., order00002)
    """
    # Find where the numeric part starts
    prefix = ""
    numeric_part = ""
    
    for char in order_code:
        if char.isdigit():
            numeric_part += char
        else:
            prefix += char
    
    # Convert to integer, increment, and format with leading zeros
    if numeric_part:
        num = int(numeric_part) + 1
        new_numeric = str(num).zfill(len(numeric_part))
        return prefix + new_numeric
    else:
        return order_code + "1"

# # Example usage
# code = "order00001"
# for i in range(1000):
#     print(code)
#     code = increment_order_code(code)