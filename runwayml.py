from os import path, getenv
from json import dumps
from base64 import encodebytes, decodebytes
from time import time
from re import sub
from dotenv import load_dotenv
from requests import get, post

# Load the environment file
env_file_path = './.env'
if path.exists(env_file_path):
    load_dotenv(dotenv_path=env_file_path)
else:
    print("No .env file found. Assuming an environment variable called MODEL_TOKEN exists")

# Check that the access token is present
if getenv("MODEL_TOKEN") is not None:
    model_token = getenv("MODEL_TOKEN")
    print("Model token found")
else:
    raise RuntimeError("No .env file found and no environment variable called MODEL_TOKEN exists")


def load_image(filename='huey.jpg'):
    """
    Load a jpeg or png image for processing
    :param filename: the name of the file
    :type: str
    :return: the image data encoded in base64
    :rtype: bytes
    """
    file_types = ['png', 'jpg', 'jpeg']
    name, extension = filename.split('.')

    if str.lower(extension) not in file_types:
        raise RuntimeError('Only JPEG and PNG images can be used. Also, naming pattern must be <name>.<extension> '
                           'with extension png, jpg, or jpeg')

    with open(filename, 'rb') as fp:
        # encoded_image_data = b64encode(fp.read())
        encoded_image_data = encodebytes(fp.read())

    return encoded_image_data


def get_model_information(url, token=model_token):
    """
    Get information about the API parameters for the model
    :param url: the full API URL for the model info
    :type: str
    :param token: the account access token (must be obtained prior to use and stored in .env file)
    :type: str
    :return: the model information
    :rtype: dict
    """
    get_request = get(url,
                      headers={
                          "Accept": "application/json",
                          "Content-Type": "application/json",
                          "Authorization": "Bearer " + token
                      })

    information = get_request.json()
    return information


def query_model_with_requests(url, image_data, token=model_token):
    """
    Run the model on the image data
    :param url: the full API URL for the model query
    :type: str
    :param image_data: the image to process
    :type: bytes
    :param token: the account access token (must be obtained prior to use and stored in .env file)
    :type: str
    :return: a base64 image string with the artistic style applied
    :rtype: str
    """
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

    model_output = post_request.json()

    result_string = model_output['image']

    # remove the starting characters containing the encoding information so we can properly encode the binary image
    result = sub('data:image/jpeg;base64,', '', result_string)
    if len(result) == len(result_string):  # The substring wasn't found -- this should not happen
        raise RuntimeError('Unable to find image encoding from API query result')

    return result


if __name__ == '__main__':
    info_url = 'https://munit-395cdb2f.hosted-models.runwayml.cloud/v1/info'
    query_url = 'https://munit-395cdb2f.hosted-models.runwayml.cloud/v1/query'

    input_data = load_image()
    model_information = get_model_information(info_url)
    query_result = query_model_with_requests(query_url, input_data)

    with open('output_image.jpg', 'wb') as output:
        output.write(decodebytes(query_result.encode('utf-8')))
