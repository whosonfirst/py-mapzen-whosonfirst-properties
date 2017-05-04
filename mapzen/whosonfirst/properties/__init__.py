def is_current(f):

    props = f["properties"]

    if props.has_key("mz:is_current") and int(props.get("mz:is_current")) == 0:
        return False

    if is_deprecated(f):
        return False

    if is_superseded(f):
        return False

    if is_cessated(f):
        return False

    return True

def is_deprecated(f):
    return has_edtf(f, "edtf:deprecated")

def is_superseded(f):
    
    if has_edtf(f, "edtf:superseded"):
        return True

    props = f["properties"]
    sp = props.get("wof:superseded", [])

    if len(sp) > 0:
        return True

    return False

def is_cessated(f):
    return has_edtf(f, "edtf:superseded")

def has_edtf(f, k):

    props = f["properties"]
    dt = props.get(k, None)

    if not dt:
        return False

    if dt in ("", "uuuu"):
        return False

    return True
