import re

def clean_data(data):
    if isinstance(data, str):
        return re.sub(r'[^\x20-\x7E\n]', '', data).replace("\n", "")
    elif isinstance(data, list):
        return [clean_data(item) for item in data]
    elif isinstance(data, dict):
        return {key: clean_data(value) for key, value in data.items()}
    return data