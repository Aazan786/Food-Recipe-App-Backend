from django.core.mail import EmailMessage
import os
from django.utils import timezone
from datetime import datetime, timedelta
import random
from authapi.models import User, VerificationCode


class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['subject'],
            body=data['body'],
            from_email=os.environ.get('EMAIL_FROM'),
            to=[data['to_email']]
        )
        email.send()


def generate_verification_code():
    return str(random.randint(100000, 999999))


def generate_verification_code_with_timestamp(user):
    verification_code = generate_verification_code()
    timestamp = timezone.now()
    expiration_time = timestamp + timedelta(minutes=4)  # Code will expire after 4 minutes

    # Check if there is an existing VerificationCode for the user
    existing_code = VerificationCode.objects.filter(user=user).first()

    if existing_code:
        # Update existing VerificationCode
        existing_code.code = verification_code
        existing_code.timestamp = timestamp
        existing_code.expiration_time = expiration_time
        existing_code.used = False
        existing_code.save()
    else:
        # Create a new VerificationCode
        VerificationCode.objects.create(
            user=user,
            code=verification_code,
            timestamp=timestamp,
            expiration_time=expiration_time,
            used=False
        )

    return verification_code, timestamp


def validate_verification_code(verification_code):
    try:
        # Retrieve the verification code from the database
        code_object = VerificationCode.objects.get(code=verification_code)
        print(code_object)

        # Check if the code is used or expired
        if not code_object.used and code_object.expiration_time >= timezone.now():
            # Mark the code as used
            code_object.used = True
            code_object.save()
            return True
    except VerificationCode.DoesNotExist:
        pass

    return False
