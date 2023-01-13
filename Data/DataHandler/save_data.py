from Data import FileBrowser
import json


def save_data(data):
    file = FileBrowser.ask_for_file()

    if file:
        # converts python-array to json-document with indent 4
        json_object = json.dumps(data, indent=4)
        with open(file, "w") as outfile:
            outfile.write(json_object)
    else:
        return False
