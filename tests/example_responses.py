def example_get_put_object():
    """
    Example response when putting a tag onto a
    object in s3.
    :return: response
    """
    return {
        "Expiration": "string",
        "ETag": "string",
        "ChecksumCRC32": "string",
        "ChecksumCRC32C": "string",
        "ChecksumSHA1": "string",
        "ChecksumSHA256": "string",
        "ServerSideEncryption": "AES256",
        "VersionId": "string",
        "SSECustomerAlgorithm": "string",
        "SSECustomerKeyMD5": "string",
        "SSEKMSKeyId": "string",
        "SSEKMSEncryptionContext": "string",
        "BucketKeyEnabled": True,
        "RequestCharged": "requester",
    }


def example_s3_event():
    """
    Example S3 event received to the lambda.
    :return: response
    """
    return {
        "Records": [
            {
                "eventVersion": "2.1",
                "eventSource": "aws:s3",
                "awsRegion": "eu-west-2",
                "eventTime": "2023-12-01T21:48:58.339Z",
                "eventName": "ObjectCreated:Put",
                "userIdentity": {"principalId": "AWS:ABCDEFGHIJKLMNOPKQRST"},
                "requestParameters": {"sourceIPAddress": "127.0.0.1"},
                "responseElements": {
                    "x-amz-request-id": "BY65CG6WZD6HBVX2",
                    "x-amz-id-2": "c2La85nMEE2WBGPHBXDc5a8fd28kEpGt/QsP8n/xmbLv0ZAJeqsK/XmNcCCS+phWuVz8KP3/gn3Ql3/z7RPyC3n176rqpzvZ",
                },
                "s3": {
                    "s3SchemaVersion": "1.0",
                    "configurationId": "huh",
                    "bucket": {
                        "name": "test-noverycool-2139",
                        "ownerIdentity": {"principalId": "ABCDEFGHIJKLMN"},
                        "arn": "arn:aws:s3:::test-noverycool-2139",
                    },
                    "object": {
                        "key": "data/example-bank-file.csv",
                        "size": 515246,
                        "eTag": "0e29c0d99c654bbe83c42097c97743ed",
                        "sequencer": "00656A54CA3D69362D",
                    },
                },
            }
        ]
    }
