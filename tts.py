import http.client
import urllib.parse
import json
from generate_questions import generate_questions

def processGETRequest(appKey, token, text, audioSaveFile, format, sampleRate) :
    host = 'nls-gateway-ap-southeast-1.aliyuncs.com'
    url = 'https://' + host + '/stream/v1/tts'
    # Set the request parameters in the URL.
    url = url + '?appkey=' + appKey
    url = url + '&token=' + token
    url = url + '&text=' + text
    url = url + '&format=' + format
    url = url + '&sample_rate=' + str(sampleRate)
    url = url + '&voice=' + 'luca'
    print(url)
    conn = http.client.HTTPSConnection(host)
    conn.request(method='GET', url=url)
    # Process the response from the server. 
    response = conn.getresponse()
    print('Response status and response reason:')
    print(response.status ,response.reason)
    contentType = response.getheader('Content-Type')
    print(contentType)
    body = response.read()
    if 'audio/mpeg' == contentType :
        with open(audioSaveFile, mode='wb') as f:
            f.write(body)
        print('The GET request succeed!')
    else :
        print('The GET request failed: ' + str(body))
    conn.close()


def processPOSTRequest(appKey, token, text, audioSaveFile, format, sampleRate) :
    host = 'nls-gateway-ap-southeast-1.aliyuncs.com'
    url = 'https://' + host + '/stream/v1/tts'
    # Set the HTTPS headers. 
    httpHeaders = {
        'Content-Type': 'application/json'
        }
    # Set the HTTPS body. 
    body = {'appkey': appKey, 'token': token, 'text': text, 'format': format, 'sample_rate': sampleRate}
    body = json.dumps(body)
    print('The POST request body content: ' + body)
    conn = http.client.HTTPSConnection(host)
    conn.request(method='POST', url=url, body=body, headers=httpHeaders)
    # Process the response from the server. 
    response = conn.getresponse()
    print('Response status and response reason:')
    print(response.status ,response.reason)
    contentType = response.getheader('Content-Type')
    print(contentType)
    body = response.read()
    if 'audio/mpeg' == contentType :
        with open(audioSaveFile, mode='wb') as f:
            f.write(body)
        print('The POST request succeed!')
    else :
        print('The POST request failed: ' + str(body))
    conn.close()

def tts(app_key, token, text):
    # Encode the URL based on the RFC 3986 standard. 
    textUrlencode = text
    textUrlencode = urllib.parse.quote_plus(textUrlencode)
    textUrlencode = textUrlencode.replace("+", "%20")
    textUrlencode = textUrlencode.replace("*", "%2A")
    textUrlencode = textUrlencode.replace("%7E", "~")
    print('text: ' + textUrlencode)
    audioSaveFile = 'syAudio.wav'
    format = 'wav'
    sampleRate = 16000
    # GET request
    processGETRequest(app_key, token, textUrlencode, audioSaveFile, format, sampleRate)