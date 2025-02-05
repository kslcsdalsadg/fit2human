from garmin_fit_sdk import Decoder, Stream

import datetime
import json
import sys

known_unknown_values = {
    '136': { 'name': 'wrist heart rate',    'units': 'bpm' },
    '137': { 'name': 'stamina potential' },
    '138': { 'name': 'stamina' },
    '143': { 'name': 'body battery' },
    '144': { 'name': 'external heart rate', 'units': 'bpm' },
}

def get_serializable(value):
    if isinstance(value, datetime.datetime): return value.isoformat()
    return value

def get_json(data):
    return json.dumps(data, default = get_serializable, indent = 4)

def get_csv(object):
    def __get_csv(entries):
        def __get_header(entry, keys):
            for key in entry:
                key = str(key)
                if key not in keys: keys.append(key)
            return keys

        if isinstance(entries, dict): entries = [ entries ]
        keys = []
        for entry in entries: keys = __get_header(entry, keys)
        lines = [ "\t".join(keys) ]
        for entry in entries:
            entry_values, any_value = [], False
            for key in keys:
                value = str(get_serializable(entry[key])) if (key in entry) and (entry[key] is not None) else ''
                if value != '': any_value = True
                entry_values.append(value)
            if any_value: lines.append("\t".join(entry_values))
        return lines

    data = []
    for key in object:
        data.append('')
        data.append(key.upper())
        data.append('')
        for line in __get_csv(object[key]): data.append(line)
    return "\n".join(data)

def get_data(messages):
    data = {}
    for key in messages:
        if key == 'record_mesgs':
            key_data = []
            for message in messages[key]:
                entry_data = {}
                for entry_key in message: entry_data[known_unknown_values[str(entry_key)]['name'] if str(entry_key) in known_unknown_values else entry_key] = message[entry_key]
                key_data.append(entry_data)
        elif len(key) == 1:
            key_data = messages[key][0]
        else:
            key_data = []
            for message in messages[key]: key_data.append(message)
        data[key] = key_data
    return data

def main(source, result_type):
    stream = Stream.from_file(source)
    decoder = Decoder(stream)
    messages, errors = decoder.read()
    if errors:
        print(errors)
        return None
    else:
        data = get_data(messages)
        if result_type == 'json': data = get_json(data)
        else: data = get_csv(data)
        return(data)
            
if __name__ == "__main__":
    if len(sys.argv) < 2: print('No input file received')
    else: print(main(sys.argv[1], sys.argv[2].lower() if len(sys.argv) == 3 else None))
