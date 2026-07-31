def extract_name(text:str)->str:
    lines = text.split("\n")

    for line in lines:
        
        line = line.strip()

        if line:
            return line.title()
    return None