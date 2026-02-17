from formsapp.constants import (
    QUESTION_TYPE,
    STRING_TO_REMOVE,
    STRING_TO_REPLACE,
    GROUP_BY_TYPE,
)
import re
import unicodedata
import string


def parse_data(formsapp_data: dict) -> dict:
    form_questions = formsapp_data["form"]["questions"]

    # 1) Construimos mapa de preguntas (id -> {type, name, parent?})
    questions: dict = {}
    for question in form_questions:
        qtype = question.get("questionType")
        if qtype not in QUESTION_TYPE:
            continue

        qid = question.get("_id")
        qtext = question.get("question", "")

        if qtext in string.ascii_uppercase:
            parsed_type = "macroinvertebrate"
        else:
            parsed_type = qtype

        questions[qid] = {
            "type": parsed_type,
            "name": clean_text(qtext),
        }

        parent_id = question.get("parentId")
        if parent_id:
            parent = parent_name(parent_id, form_questions)
            if parent:
                questions[qid]["parent"] = parent

    # 2) Parse de respuestas
    answers = formsapp_data["answer"]["answers"]
    data: dict = {}

    for answer in answers:
        qid = answer.get("q")
        if not qid or qid not in questions:
            continue

        qinfo = questions[qid]
        key_name = snake(qinfo["name"])

        parent_prefix = ""
        if "parent" in qinfo:
            parent_prefix = f"{snake(qinfo['parent'])}/"

        key = f"{parent_prefix}{key_name}"
        qtype = qinfo["type"]

        value_key, value = get_answer_value(answer)
        if value_key is None:
            continue

        # TEXT / DATE / NUMBER / EMAIL (valores simples)
        if qtype in GROUP_BY_TYPE["text"]:
            data[key] = value

        # IMAGE / FILEUPLOAD (urls)
        elif qtype in GROUP_BY_TYPE["image"]:
            urls = value or []
            # Guardamos downloadUrl si existe, si no previewUrl
            parsed_urls = []
            for u in urls:
                if isinstance(u, dict):
                    parsed_urls.append(u.get("downloadUrl")
                                       or u.get("previewUrl"))
                elif isinstance(u, str):
                    parsed_urls.append(u)
            data[key] = [u for u in parsed_urls if u]

        # MACROINVERTEBRATE (preguntas A, B, C... con multiplechoice)
        elif qtype in GROUP_BY_TYPE["macroinvertebrate"]:
            items = value or []
            if items:
                key_macro = f"{parent_prefix}{key_name.upper()}"
                data[key_macro] = " ".join(
                    (m.get("t", "") or "").lower()
                    for m in items
                    if isinstance(m, dict) and m.get("t")
                )

        # SELECT (choice)
        elif qtype in GROUP_BY_TYPE["select"]:
            items = value or []
            # singlechoice, dropdown, yesno normalmente vienen como lista de 1
            if len(items) == 1 and isinstance(items[0], dict):
                data[key] = items[0].get("t")
            elif len(items) > 1:
                data[key] = [i.get("t") for i in items if isinstance(
                    i, dict) and i.get("t")]
            else:
                # lista vacía
                data[key] = []

        # GRID
        elif qtype in GROUP_BY_TYPE["grid"]:
            grid = value or []
            data.update(set_grid(key_name, grid))

        # LOCATION (si luego decides habilitar address en GROUP_BY_TYPE)
        # elif qtype in GROUP_BY_TYPE.get("location", []):
        #     data[key] = set_location(value or {})

    return data


def get_answer_value(answer: dict):
    """
    Detecta el valor real de la respuesta según el payload de Forms.app.
    Prioridades según tu ejemplo:
      - t: texto (email/shorttext/longtext/maskedtext)
      - n: number
      - d: date
      - c: choice (singlechoice/multiplechoice/dropdown/yesno)
      - g: grid
      - urls: imageupload
      - fallback: more.urls
    """
    if "t" in answer:
        return "t", answer.get("t")
    if "n" in answer:
        return "n", answer.get("n")
    if "d" in answer:
        return "d", answer.get("d")
    if "c" in answer:
        return "c", answer.get("c")
    if "g" in answer:
        return "g", answer.get("g")
    if "urls" in answer:
        return "urls", answer.get("urls")

    more = answer.get("more") or {}
    if isinstance(more, dict) and "urls" in more:
        return "urls", more.get("urls")

    return None, None


def parent_name(parent_id: str, form_questions: list) -> str:
    for fq in form_questions:
        if fq.get("_id") == parent_id:
            return clean_text(fq.get("question", ""))
    return ""


def clean_text(text: str) -> str:
    for i in STRING_TO_REMOVE:
        text = text.replace(i, "")

    for key, value in STRING_TO_REPLACE.items():
        text = text.replace(key, value)

    # Quita texto entre paréntesis
    text = re.sub(r"\([^)]*\)", "", text, flags=re.MULTILINE)

    # Normaliza espacios
    text = re.sub(r"\s+", " ", text).strip()

    return text


def snake(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode(
        "ascii", "ignore").decode("utf-8", "ignore")
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")


def set_location(location: dict) -> str:
    value = ""
    if "a1" in location and location["a1"]:
        value += location["a1"]
    if "a2" in location and location["a2"]:
        value += f", {location['a2']}"
    if "p" in location and location["p"]:
        value += f", {location['p']}"
    if "c" in location and location["c"]:
        value += f" {location['c']}"
    if "s" in location and location["s"]:
        value += f", {location['s']}"
    return value.strip()


def set_grid(name: str, grid: list) -> dict:
    values = {}

    if not grid:
        return values

    if len(grid) == 1:
        row = grid[0] or {}
        for cell in row.get("c", []):
            key_name = f"{name}/{snake(cell.get('cn', ''))}"
            values[key_name] = cell.get("n")
        return values

    # > 1 fila
    grid_list = []
    for row in grid:
        temp = {}
        for cell in (row or {}).get("c", []):
            key_name = f"{name}/{snake(cell.get('cn', ''))}"
            temp[key_name] = cell.get("n")
        grid_list.append(temp)

    values[name] = grid_list
    return values
