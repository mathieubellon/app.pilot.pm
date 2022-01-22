import hashlib
import json
import hmac
from base64 import b64encode
from datetime import datetime, timedelta

from botocore.exceptions import ClientError
import boto3
from boto3.s3.transfer import TransferConfig
from django.conf import settings

from pilot.utils.alpha import to_alpha


bucket_name = settings.AWS_STORAGE_BUCKET_NAME

# Client API
s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
)
# Resource API
s3_resource = boto3.resource(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
)


# def get_s3_signature_v3(s3_path, content_type, file_name=None):
#     from pilot.assets.utils import get_uploaded_file_attributes
#
#     if not file_name:
#         file_name = s3_path.split('/')[-1]
#     file_attributes = get_uploaded_file_attributes(file_name)
#     title = to_alpha(file_attributes['title'], to_lower=False)
#     normalized_file_name = "{}.{}".format(title, file_attributes['extension'])
#
#     expires_in = datetime.now() + timedelta(hours=24)
#     expires = expires_in.strftime('%Y-%m-%dT%H:%M:%S.000Z')
#
#     policy_object = json.dumps({
#         "expiration": expires,
#         "conditions": [
#             {"acl": "public-read"},
#             {"bucket": bucket_name},
#             {"key": s3_path},
#             {"success_action_status": "201"},
#             {"Content-Type": content_type},
#             {"Content-Disposition": 'attachment;filename="{file_name}"'.format(file_name=normalized_file_name)}
#         ]
#     })
#
#     policy = b64encode(policy_object.replace('\n', '').replace('\r', ''))
#     signature = hmac.new(
#         settings.AWS_SECRET_ACCESS_KEY.encode(),
#         policy,
#         hashlib.sha1
#     ).digest()
#     signature_b64 = b64encode(signature)
#
#     return {
#         "policy": policy,
#         "signature": signature_b64,
#         "key": s3_path,
#         "AWSAccessKeyId": settings.AWS_ACCESS_KEY_ID,
#         "success_action_status": "201",
#         "acl": "public-read",
#         "Content-Type": content_type,
#         "Content-Disposition": 'attachment;filename="{file_name}"'.format(file_name=normalized_file_name)
#     }


def get_s3_signature_v4(s3_path, content_type, file_name=None):
    from pilot.assets.utils import get_uploaded_file_attributes

    # The return object
    s3_signature_object = {}
    conditions = []

    def add_condition(name, value):
        conditions.append({name: value})
        s3_signature_object[name] = value

    if not file_name:
        file_name = s3_path.split('/')[-1]
    file_attributes = get_uploaded_file_attributes(file_name)
    title = to_alpha(file_attributes['title'], to_lower=False)
    file_extension = file_attributes['extension']
    normalized_file_name = "{}.{}".format(title, file_extension)

    region = settings.AWS_REGION
    algorithm = "AWS4-HMAC-SHA256"
    service = "s3"
    now = datetime.utcnow()
    date = now.strftime('%Y%m%dT%H%M%SZ')
    short_date = now.strftime('%Y%m%d')
    request_type = "aws4_request"
    expires = "86400" # 24 Hours
    success_action_status = "201"
    acl = 'public-read'

    # step1 : generate scope
    scope = [
        settings.AWS_ACCESS_KEY_ID,
        short_date,
        region,
        service,
        request_type
    ]
    credentials = '/'.join(scope)

    # step 2 : make a base64 encoded policy
    add_condition("acl", acl)
    add_condition("bucket", bucket_name)
    add_condition("key", s3_path)
    add_condition("success_action_status", success_action_status)
    add_condition("Content-Type", content_type)
    add_condition("Content-Disposition", 'attachment;filename="{file_name}"'.format(file_name=normalized_file_name))
    add_condition("x-amz-credential", credentials)
    add_condition("x-amz-algorithm", algorithm)
    add_condition("x-amz-date", date)
    add_condition("x-amz-expires", expires)

    policy = {
        'expiration': (now + timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%S.000Z'),
        'conditions': conditions
    }
    # b64 objects are bytes
    base_64_policy = b64encode(json.dumps(policy).encode())

    # Key derivation functions. See:
    # http://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html#signature-v4-examples-python
    def sign(key, msg):
        return hmac.new(key, msg.encode(), hashlib.sha256).digest()

    def get_signature_key(key, date_stamp, regionName, serviceName):
        k_date = sign(('AWS4' + key).encode(), date_stamp)
        k_region = sign(k_date, regionName)
        k_service = sign(k_region, serviceName)
        k_signing = sign(k_service, 'aws4_request')
        return k_signing

    # ************* TASK 3: CALCULATE THE SIGNATURE *************
    # Create the signing key using the function defined above.
    signing_key = get_signature_key(settings.AWS_SECRET_ACCESS_KEY, short_date, region, service)

    # Sign the string_to_sign using the signing_key
    signature = hmac.new(signing_key, base_64_policy, hashlib.sha256).hexdigest()

    s3_signature_object.update({
        'policy': base_64_policy.decode(),  # Convert the base64 bytes to a string
        'X-amz-signature': signature
    })
    return s3_signature_object


def s3_file_exists(key):
    try:
        s3_resource.Object(bucket_name, key).load()
        return True
    except ClientError as e:
        if e.response['Error']['Code'] != 404:
            return False
        else:
            raise


def download_s3_file(key):
    return s3_client.get_object(
        Bucket=bucket_name,
        Key=key,
    )['Body']


def upload_s3_file(key, file, file_name):
    s3_client.put_object(
        ACL='public-read',
        Bucket=bucket_name,
        Body=file,
        ContentDisposition='attachment;filename="{name}"'.format(name=file_name),
        Key=key,
    )


def upload_s3_file_multipart(key, file, file_name):
    """
    Transfer a big file to S3 with 8Mo chunks and up to 10 threads
    """
    config = TransferConfig(
        multipart_threshold=1024 * 1024 * 8,
        max_concurrency=10,
        multipart_chunksize=1024 * 1024 * 8,
        use_threads=True
    )
    s3_client.upload_fileobj(
        Fileobj=file,
        Bucket=bucket_name,
        Key=key,
        ExtraArgs={
            'ACL': 'public-read',
            'ContentDisposition': 'attachment;filename="{name}"'.format(name=file_name),
        },
        Config=config
    )


def update_s3_filename(key, new_name):
    s3_file = s3_resource.Object(bucket_name, key)
    s3_file.copy_from(
        ACL='public-read',
        CopySource={'Bucket': bucket_name, 'Key': key},
        ContentDisposition='attachment;filename="{name}"'.format(name=new_name),
        MetadataDirective='REPLACE'
    )


def delete_s3_file(key):
    """
    Delete S3 file
    """
    s3_client.delete_object(
        Bucket=bucket_name,
        Key=key
    )


def trash_s3_file(path):
    """
    Move S3 file to a trash folder
    """
    bucket_list_result_set = s3_client.list_objects(
        Bucket=bucket_name,
        Prefix=path,
    )

    for key in bucket_list_result_set.get('Contents', []):
        s3_client.copy_object(
            ACL='public-read',
            Bucket=bucket_name,
            CopySource={'Bucket': bucket_name, 'Key': key['Key']},
            Key='trash/{0}'.format(key['Key'])
        )
        s3_client.delete_object(
            Bucket=bucket_name,
            Key=key['Key']
        )


def delete_s3_folder(folder):
    """
    Delete S3 file
    """
    bucket = s3_resource.Bucket(bucket_name)
    bucket.objects.filter(Prefix=folder).delete()
