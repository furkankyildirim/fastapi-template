from dotenv import load_dotenv

load_dotenv()


class BusinessLogicConfig:

    @staticmethod
    def get_register_email_template() -> str:
        """Get the register email template.

        Returns:
            str: Register email template.
        """
        template = f'''
Subject: Confirm Your Registration

Welcome, {{name}}!

Thank you for registering. Please use the link below to activate your account:

Activate Account Link: {{link}}

This code is valid for the next 10 minutes and can only be used once.  
If you did not initiate this request, please ignore this email.

Thank you,
FastAPI Template Team
        '''
        return template

    @staticmethod
    def get_reset_password_email_template() -> str:
        """Get the reset password email template.

        Returns:
            str: Reset password email template.
        """
        template = f'''
Subject: Reset Your Password

Hello, {{name}}.

We received a request to reset the password for your account.  
Please use the link to proceed with the reset:

Reset Password Link: {{link}}

This code will expire in 10 minutes.  
If you did not request a password reset, please ignore this email or contact support.

Thank you,
FastAPI Template Team
        '''
        return template
