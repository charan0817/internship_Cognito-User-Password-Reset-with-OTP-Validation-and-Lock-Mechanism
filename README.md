This AWS Lambda function facilitates secure password reset for users in an Amazon Cognito user pool. 
The function validates an OTP and implements a lock mechanism to prevent excessive failed attempts. Key functionalities include:
1. User Retrieval: Retrieves user attributes from the Cognito user pool using the admin_get_user API.
2. OTP Validation: Validates the OTP provided in the event payload against the stored OTP.
  i.Checks the time elapsed since the OTP was sent, allowing only a 5-minute validity window.
3. Password Reset: Resets the user's password using the admin_set_user_password API if OTP validation is successful.
4. Authentication Token Generation: Initiates authentication with the new password and returns an authentication token.
5. Lock Mechanism:
  i.Tracks the number of failed OTP attempts.
  ii.Locks the user's account for 30 seconds after three failed attempts, with a retry enabled only after the lock duration.
6. Attribute Management: Updates custom attributes (custom:attempts-time, custom:lock-time) in Cognito to track failed attempts and lock status.
The function ensures security and mitigates brute-force attacks by limiting retries and enforcing time-based locks while providing detailed logs for troubleshooting.
