parts = context.standard_html().split('<!--split here-->', 1)
if len(parts) > 1:
    return parts[1]
else:
    return ""

