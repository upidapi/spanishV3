import json
import requests


def get_line_bounding_box(line):
    min_x1, min_y1, max_x2, max_y2 = [1_000_000, 1_000_000, 0, 0]
    words = line["Words"]
    for word in words:
        # converts width/height to coordinates
        x, y, width, height = word["Left"], word["Top"], word["Width"], word["Height"]
        x1, y1, x2, y2 = x, y, x + width, y + height

        # gets the min/max chords of chords to get the bounding box
        min_x1 = min(min_x1, x1)
        min_y1 = min(min_y1, y1)
        max_x2 = max(max_x2, x2)
        max_y2 = max(max_y2, y2)

    # converts coordinate to width/height
    x1, y1, x2, y2 = min_x1, min_y1, max_x2, max_y2
    width = abs(x1 - x2)
    height = abs(y1 - y2)
    x = min(x1, x2)
    y = min(y1, y2)

    return x, y, width, height


def get_data_from_image(filename, language='eng'):
    """
    OCR.space API requests with local file.

    :param filename: Your file path & name.
    :param language: Language code to be used in OCR.
                    List of available language codes can be found on https://ocr.space/OCRAPI
                    Defaults to 'en'.
    :return: Result in JSON format.
    """

    api_key = "K85003833988957"

    payload = {'isOverlayRequired': True,
               'apikey': api_key,
               'language': language,
               'scale': True
               }

    with open(filename, 'rb') as f:
        r = requests.post('https://api.ocr.space/parse/image',
                          files={filename: f},
                          data=payload,
                          )

    # decode
    return_data = r.content.decode()
    # from json-str to python-array
    return_data = json.loads(return_data)
    return return_data


def clean_up_data(dirty_data):
    """
    converts the raw return New into a better format

    :param dirty_data: the raw json New
    :return: a cleaner version of the New
    """
    clean_data = []

    # New format
    # [
    #     {
    #         'text': 'the lines text',
    #
    #         'x': 'x position (int)',
    #         'y': 'y position (int)',
    #         'width': 'width (int)',
    #         'height': 'height (int)'
    #     },
    #
    #     ...
    # ]

    for line in dirty_data["ParsedResults"][0]["TextOverlay"]["Lines"]:
        line_pos = get_line_bounding_box(line)

        line_data = {
            'text': line['LineText'],

            'x': line_pos[0],
            'y': line_pos[1],
            'width': line_pos[2],
            'height': line_pos[3]
        }

        clean_data.append(line_data)

    return clean_data


def get_existence(item, lis):
    for word in lis:
        # full match
        if item['x'] == word['x'] and \
                item['y'] == word['y'] and \
                item['width'] == word['width'] and \
                item['height'] == word['height']:
            return None

    for word in lis:
        # start match
        if item['x'] == word['x'] and \
                item['y'] == word['y'] and \
                item['height'] == word['height']:
            # sets the word to the longest
            if item['width'] < word['width']:
                return word

            # if you can't set it now prevent it from appending it
            return None

        # end match
        elif item['x'] + item['width'] == word['x'] + word['width'] and \
                item['y'] == word['y'] and \
                item['height'] == word['height']:
            # sets the word to the longest
            if item['width'] < word['width']:
                return word

            # if you can't set it now prevent it from appending it
            return None

    return 'NaN'


def get_missing_words(lan1, lan2):
    for i, word in enumerate(lan1):
        ret = get_existence(word, lan2)
        if ret is not None:
            if ret == 'NaN':
                lan2.append(word)
            else:
                lan1[i] = ret

    for i, word in enumerate(lan2):
        ret = get_existence(word, lan1)
        if ret is not None:
            if ret == 'NaN':
                lan1.append(word)
            else:
                lan2[i] = ret

    return lan1, lan2


def new_image(select_image, lan):
    from PIL import Image

    files = [r'..\Data\DataFiles\lan1_data.json', r'..\Data\DataFiles\lan2_data.json']

    # crops it due to the 1k x 1k limit from the api
    image = Image.open(select_image)
    image.thumbnail((1000, 1000))

    image.save(r'..\Data\DataFiles\selected_image.jpg')

    # gets the New and cleans up the New format
    clean_data = []
    for i in range(2):
        json_data = get_data_from_image(r'..\Data\DataFiles\selected_image.jpg', language=lan[i])
        clean_data.append(clean_up_data(json_data))

    # add some missing words
    fixed_data = get_missing_words(*clean_data)

    # saves the New
    for i in range(2):
        fixed_data[i].sort(key=lambda x: x['y'])

        # converts python-array to json-document with indent 4
        json_object = json.dumps(fixed_data[i], indent=4)
        with open(files[i], "w") as outfile:
            outfile.write(json_object)
