QUESTION_TYPE = [
    "choice",
    "grid",
    "address",
    "number",
    "imageupload",
    'fileupload',
    "date",
    "text",
    "email",
]
STRING_TO_REMOVE = [
    "[b]",
    "[/b]",
    "[i]",
    "[/i]",
    "¿",
    "?",
    ":",
    ",",
    "Bloque 1. ",
    "Bloque 2. ",
    "Bloque 3. ",
    "Bloque 4. ",
    "Bloque 5. ",
    "Bloque 6. ",
    "Bloque 7. ",
    "Bloque 8. ",
    "Bloque 9. ",
    "Bloque 10. ",
    ".",
]
STRING_TO_REPLACE = {
    "y/o": "y_o"
}
IGNORE_KEYS = ['q', 'f']
GROUP_BY_TYPE = {
    "text": ["text", "date", "number", "email"],
    "image": ["imageupload", "fileupload"],
    "select": ["choice"],
    "macroinvertebrate": ["macroinvertebrate"],
    "location": ["address"],
    "grid": ["grid"]
}
