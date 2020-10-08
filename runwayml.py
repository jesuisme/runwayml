import json
from requests import get, post
from base64 import b64encode, b64decode
from time import time
from urllib.request import urlopen, Request


def get_model_information():
    get_request = get('https://munit-395cdb2f.hosted-models.runwayml.cloud/v1/info',
                      headers={
                          "Accept": "application/json",
                          "Content-Type": "application/json",
                          "Authorization": "Bearer bT6zM+OwNRxd9LmC6h+G5w=="
                      })

    model_information = get_request.json()
    print(model_information)


def query_model_with_requests(image_data):
    print('Querying the model with requests...')
    encoded_data = b64encode(image_data)
    utf8encode = str(encoded_data).encode("utf-8")
    print(type(utf8encode))

    model_input = {'image': utf8encode, 'style': 42}

    query_start = time()
    print('Starting model query...')
    post_request = post('https://munit-395cdb2f.hosted-models.runwayml.cloud/v1/query',
                        headers={
                            "Accept": "application/json",
                            "Content-Type": "application/json",
                            "Authorization": "Bearer bT6zM+OwNRxd9LmC6h+G5w=="
                        },
                        # data=json.dumps(model_input).encode('utf8'))
                        data=model_input)

    query_duration = time() - query_start
    print('Done!! Elapsed time: {0}'.format(query_duration))
    print(post_request.json())
    model_output = post_request.json()

    result = b64decode(model_output['image'])

    return result


def query_model_with_urllib(image_data):
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
            "Authorization": "Bearer bT6zM+OwNRxd9LmC6h+G5w==",
        },
        data=json.dumps(inputs).encode("utf8")
    )

    query_start = time()

    with urlopen(req) as url:
        result = json.loads(url.read().decode("utf8"))

    query_duration = time() - query_start
    print('Done!! Elapsed time: {0}'.format(query_duration))

    return b64decode(result["image"])


if __name__ == '__main__':
    with open('huey.jpg', 'rb') as fp:
        input_data = fp.read()

    get_model_information()
    image = query_model_with_requests(input_data)
    # image = query_model_with_urllib(input_data)

    with open('output_image.jpg', 'wb') as output:
        output.write(image)
