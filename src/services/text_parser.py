def clean_text(text:str)->str:
    text = text.strip()
    # removing leading/trailing spaces
    text = text.replace("\t"," ")
    # tabs w spaces
    text = text.replace('\r',"")
    #  remove carriage returns
    while "\n\n" in text:
        text = text.replace("\n\n",'\n')
        # remove multiple blank lines
    while "  " in text:
        text = text.replace("  ",' ')
        # remove multiple spaces
    return text