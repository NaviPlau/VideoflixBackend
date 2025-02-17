from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from datetime import datetime, timedelta

def send_welcome_email(user_email, user_name, activation_link):
    """
    Sends a welcome email to a user with an activation link.

    Args:
        user_email (str): The user's email address.
        user_name (str): The user's name.
        activation_link (str): The link to activate the user's account.
    """
    context = {
        'user_name': user_name,
        'activation_link': activation_link,
        'STATIC_URL': staticfiles_storage.url(''), 
    }
    html_content = render_to_string('emails/welcome_email.html', context)
    text_content = f"Hello {user_name},\n\nPlease activate your account here: {activation_link}"
    email = EmailMultiAlternatives(
        subject="Activate Your Videoflix Account",
        body=text_content, 
        from_email="noreply@videoflix.paul-ivan.com",
        to=[user_email],
    )
    email.attach_alternative(html_content, "text/html") 
    email.send()
    
    
def send_password_reset_email(user_email, user_name, reset_link):
    """
    Sends a password reset email to a user with a reset link.

    Args:
        user_email (str): The user's email address.
        user_name (str): The user's name.
        reset_link (str): The link to reset the user's password.
    """
    context = {
        'user_name': user_name,
        'reset_link': reset_link,
        'STATIC_URL': staticfiles_storage.url(''),
    }
    html_content = render_to_string('emails/reset_password_email.html', context)
    text_content = f"Hello {user_name},\n\nYou can reset your password here: {reset_link}"

    email = EmailMultiAlternatives(
        subject="Reset Your Videoflix Password",
        body=text_content,
        from_email="noreply@videoflix.paul-ivan.com",
        to=[user_email],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
    