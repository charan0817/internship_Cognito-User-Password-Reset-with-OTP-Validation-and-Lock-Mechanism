import boto3
import time

cognito = boto3.client('cognito-idp')
user_pool_id = 'eu-north-1_a5woLUQLI'


def get_user(username):
    response = cognito.admin_get_user(
        UserPoolId=user_pool_id,
        Username=username
    )
    return response


def update_user(user, name, value):
    cognito.admin_update_user_attributes(
        UserPoolId=user_pool_id,
        Username=user,
        UserAttributes=[
            {
                'Name': name,
                'Value': value

            }
        ]
    )


def lambda_handler(event, context):
    username = event.get('username')
    response = get_user(username)
    print(response['UserAttributes'])

    # to get OTP and time when OTP was sent
    otp_time = response['UserAttributes'][10]['Value']
    otp_sent = otp_time.split('~')[0]
    time_sent = otp_time.split('~')[1]
    current_time = time.time()
    time_lapsed = round(current_time - float(time_sent))
    print(f'time_lapsed since otp was sent = {time_lapsed}')
    response = get_user(username)
    attempts_made = int(response['UserAttributes'][4]['Value'].split('~')[0])
    session_lock=response['UserAttributes'][3]['Value']
    lock = session_lock.split('~')[0]
    lock_time = session_lock.split('~')[1]
    # lock_time = time.time()
    if time.time() > lock_time:
        update_user(username,'custom:lock-time',str(f"{'unlocked'}~{0}") )
    # if lock == 'unlocked':
        if str(event.get('otp')) == otp_sent:
            if time_lapsed < 300:
                new_password = event.get('new password')
                try:
                    # to reset the password
                    response = cognito.admin_set_user_password(
                        UserPoolId=user_pool_id,
                        Username=username,
                        Password=new_password,
                        Permanent=True
                    )

                    print(f"Password reset for user {username} is successful.")

                except Exception as e:
                    print(f'Error: {str(e)}')

                try:
                    auth_response = cognito.admin_initiate_auth(
                        UserPoolId=user_pool_id,
                        ClientId='27gseb9rmu29em13e58oufhone',
                        AuthFlow='ADMIN_NO_SRP_AUTH',  # Use 'ADMIN_NO_SRP_AUTH' for password-based authentication
                        AuthParameters={
                            'USERNAME': username,
                            'PASSWORD': new_password  # Use the newly set password
                        }
                    )
                    auth_token = auth_response['AuthenticationResult']
                    return auth_token
                except Exception as e:
                    print(f'Error: {str(e)}')

            else:
                return (f"otp expired")
        else:
            response = get_user(username=username)
            attemtpts_made = int(response['UserAttributes'][4]['Value'].split('~')[0])
            time_of_lastattempt = float(response['UserAttributes'][4]['Value'].split('~')[0])
            time_of_attempt = time.time()
            attempts_made += 1
            value = str(f"{attempts_made}~{time_of_attempt}")
            update_user(user=username, name='custom:attempts-time', value=value)
            print(f"no:off attempts made = {attemtpts_made} time of the last attempt = {time_of_attempt}")
            unlock_time=time_of_attempt + 30
            if attempts_made >= 3:
                value=str(f"{'locked'}~{unlock_time}")
                update_user(username,'custom:lock-time',value)
                update_user(user=username,name='custom:attempts-time',value=str(f"{0}~{time.time()}"))
                return f'you have exceeded the number off attempts, try after 5 mins'
        return f'otp is not matching'

    else:
        return f"you have been blocked, try again after 5 mins"
