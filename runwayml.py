from os import path, getenv
from json import dumps, loads
from base64 import b64encode, b64decode, decodebytes
from time import time
from re import sub, match
from urllib.request import urlopen, Request
from dotenv import load_dotenv
from requests import get, post

env_file_path = './.env'
if path.exists(env_file_path):
    load_dotenv(dotenv_path=env_file_path)
else:
    print("No .env file found. Assuming an environment variable called MODEL_TOKEN exists")

if getenv("MODEL_TOKEN") is not None:
    model_token = getenv("MODEL_TOKEN")
    print("Model token found")
else:
    raise RuntimeError("No .env file found and no environment variable called MODEL_TOKEN exists")


def load_image(filename='huey.jpg'):
    file_types = ['png', 'jpg', 'jpeg']
    name, extension = filename.split('.')

    if str.lower(extension) not in file_types:
        raise RuntimeError('Only JPEG and PNG images can be used. Also, naming pattern must be <name>.<extension> '
                           'with extension png, jpg, or jpeg')

    with open(filename, 'rb') as fp:
        input_data = b64encode(fp.read())

    return input_data


def get_model_information(url, token=model_token):
    get_request = get(url,
                      headers={
                          "Accept": "application/json",
                          "Content-Type": "application/json",
                          "Authorization": "Bearer " + token
                      })

    information = get_request.json()
    return information


def query_model_with_requests(url, image_data, token=model_token):
    print('Querying the model with requests...')
    decoded_data = image_data.decode('utf-8')



    model_input = {'image': decoded_data, 'style': 42}

    query_start = time()
    print('Starting model query...')
    post_request = post(url,
                        headers={
                            "Accept": "application/json",
                            "Content-Type": "application/json",
                            "Authorization": "Bearer " + token
                        },
                        data=dumps(model_input).encode('utf8'))

    query_duration = time() - query_start
    print('Done!! Elapsed time: {0}'.format(query_duration))
    # print(post_request.json())
    model_output = post_request.json()

    result_string = model_output['image']

    # remove the first 23 characters containing the encoding information in the string so we can properly encode
    result = sub('data:image/jpeg;base64,', '', result_string)
    if len(result) == len(result_string):  # The string wasn't found and no replacement was made
        raise RuntimeError('Unable to find image encoding from API')

    return result


def query_model_with_urllib(image_data, token=model_token):
    print('Querying the model with urllib...')
    encoded_data = b64encode(image_data)
    inputs = {
                 "image": encoded_data,
                 "style": 42
    }

    req = Request(
        "https://munit-395cdb2f.hosted-models.runwayml.cloud/v1/query",
        method="POST",
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        data=dumps(inputs).encode("utf8")
    )

    query_start = time()

    with urlopen(req) as url:
        result = loads(url.read().decode("utf8"))

    query_duration = time() - query_start
    print('Done!! Elapsed time: {0}'.format(query_duration))

    return b64decode(result["image"])


if __name__ == '__main__':

    # filename = 'lt.png'
    # file_types = ['png', 'jpg', 'jpeg']
    # name, extension = filename.split('.')
    #
    # if str.lower(extension) not in file_types:
    #     raise RuntimeError('Only JPEG and PNG images can be used. Also, naming pattern must be <name>.<extension> '
    #                        'with extension png, jpg, or jpeg')
    #
    # with open(filename, 'rb') as fp:
    #     input_data = b64encode(fp.read())

    info_url = 'https://munit-395cdb2f.hosted-models.runwayml.cloud/v1/info'
    query_url = 'https://munit-395cdb2f.hosted-models.runwayml.cloud/v1/query'

    input_data = load_image()
    model_information = get_model_information(info_url)
    result = query_model_with_requests(query_url, input_data)

    with open('output_image.jpg', 'wb') as output:
        output.write(decodebytes(result.encode('utf-8')))
