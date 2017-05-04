import requests
import json
import logging
import types

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

class aliases:

    def __init__ (self):

        # IMPORTANT: see the way we're fetching these property and alias specs over the network at runtime?
        # that is a decision born of expediency still this is largely still code that is only practical for
        # internal use. that said it suggests an overall pattern that we should merge with the existing practice
        # of baking specs directly in to code - like we do for placetypes or source. for example:
        #
        # https://github.com/whosonfirst/py-mapzen-whosonfirst-sources/blob/master/utils/mk-spec.py
        #
        # that said, we are not doing this yet. we should. but we don't. this is what we do instead.
        # (20170504/thisisaaronland)

        self.property_aliases_json = 'https://raw.githubusercontent.com/whosonfirst/whosonfirst-properties/master/aliases/property_aliases.json'
        property_rsp = requests.get(self.property_aliases_json)

        property_aliases = json.loads(property_rsp.content)
        self.property_aliases = property_aliases

        self.source_aliases_json = 'https://raw.githubusercontent.com/whosonfirst/whosonfirst-properties/master/aliases/source_data_aliases.json'
        source_rsp = requests.get(self.source_aliases_json)

        source_aliases = json.loads(source_rsp.content)
        self.source_aliases = source_aliases

    def resolve(self, k):

        if self.property_aliases.get(k, None):
            a = self.property_aliases[k]
        elif self.source_aliases.get(k, None):
            a = self.source_aliases[k]
        else:
            raise Exception, "Unknown key %s" % k

        return a

    def prep (self, props_raw):

        props = {}

        for k, v in props_raw.items():

            a = self.resolve(k)

            logging.debug("process %s (%s) = %s" % (k, a, v))

            if a.startswith("name:"):

                if v == None or v == "":
                    v = []
                else:

                    tmp = []

                    for t in v.split(","):
                        tmp.append(t.strip())

                    v = tmp
                    
                if len(v) == 0:
                    continue

            elif a.startswith("wof:supersede"):

                if v == None or v == "":
                    v = []
                elif type(v) == types.IntType:
                    v = [ v ]
                else:
                    v = map(int, v.split(","))

            elif a == "wof:controlled":

                if not v:
                    v = []

                elif type(v) == types.ListType:
                    pass	# grrrrnnnnn....

                else:
                    v = v.split(",")

            elif a == "wof:id":

                v = int(v)

            elif v == None:
                continue

            else:
                pass

            if a in ("mz:is_landuse_aoi", "mz:max_zoom", "mz:min_zoom", "mz:is_funky"):

                if v == '':

                    logging.warning("%s is an empty string" % a)

                    if a == "mz:is_funky":
                        v = 0
                    else:
                        raise Exception, "%s is an empty string" % a

                v = int(v)

            props[a] = v

        if not props.get("wof:repo", None):
            props["wof:repo"] = "whosonfirst-data"

        return props
