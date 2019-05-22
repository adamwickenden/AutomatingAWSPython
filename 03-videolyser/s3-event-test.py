# coding: utf-8
event = {'Records': [{'eventVersion': '2.1', 'eventSource': 'aws:s3', 'awsRegion': 'us-east-1', 'eventTime': '2019-05-22T10:43:17.300Z', 'eventName': 'ObjectCreated:CompleteMultipartUpload', 'userIdentity': {'principalId': 'AWS:AIDAXSHPGOTWCUKEUUKJZ'}, 'requestParameters': {'sourceIPAddress': '81.107.194.68'}, 'responseElements': {'x-amz-request-id': 'EB4C59B868CA1112', 'x-amz-id-2': 'Idhwz7d8/WJMnlXtaUVjf78dYQyf4OtY26FpVC0vMvOdQuJC3TGKFmfddaJG/VtnTfewqpf0gdw='}, 's3': {'s3SchemaVersion': '1.0', 'configurationId': '55aaec1a-2e64-4e27-b434-4457a7094220', 'bucket': {'name': 'aws-auto-videolyser1234', 'ownerIdentity': {'principalId': 'A17Z5HA5AJ9R91'}, 'arn': 'arn:aws:s3:::aws-auto-videolyser1234'}, 'object': {'key': 'Pexels+Videos+1466210.mp4', 'size': 10687399, 'eTag': '5c4faa5961cc2989095699f89d501c66-2', 'sequencer': '005CE527A1575FF854'}}}]}
event
event['Records'][0]['s3']['object']['key']
import urllib
urllib.parse_unquote_plus(event['Records'][0]['s3']['object']['key'])
urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
get_ipython().run_line_magic('save', 's3-event-test.py 1-7')
