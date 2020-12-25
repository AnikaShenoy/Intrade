import http.client
import json
import time
import timeit
import pickle

def get_colors(quantity=5, api_key=None):
    conn = http.client.HTTPSConnection("rebrickable.com")
    key = api_key
    auth_token = {'Authorization': 'key ' + key}
    payload = "{}"
    headers = auth_token
    params = '/api/v3/lego/colors/'  # modify this so that results are limited by the `quantity` argument.

    conn.request("GET", params, payload, headers=headers)
    response = conn.getresponse()

    ################################################################
    #  insert code to handle data returned in the response         #
    # return a list of strings, one string for each color returned #
    ################################################################
    json_data = json.load(response)
    print(json_data)

    colors = set()

    for color in json_data["results"]:
        colors.add(color["name"])

    return list(colors)


# uncomment these next 2 lines to test your implementation
colors = get_colors(quantity=5, api_key='dbe84767665dfba2a18a53310033d177')
print(colors)