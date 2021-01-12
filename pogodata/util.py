import requests

def httpget(url):
    return requests.get(url)

def gen_uicon(**args):
    icon = ""
    for key, value in args.items():
        if value > 0:
            icon += key + str(value)
    return icon + ".png"
