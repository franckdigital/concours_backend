from django.core.mail import send_mail
from django.conf import settings

def send_email(subject, message, recipient_list, html_message=None):
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        html_message=html_message,
        fail_silently=False,
    )

def notify_ip_reset(utilisateur):
    # Envoi d’un email réel à l’utilisateur lors de la réinitialisation d’IP
    if utilisateur.email:
        subject = "Votre adresse IP a été réinitialisée"
        message = f"Bonjour {utilisateur.nom_complet},\n\nVotre accès a été réinitialisé par un administrateur. Vous pouvez à nouveau vous connecter depuis un nouvel appareil ou réseau.\n\nL’équipe QCM."
        send_email(subject, message, [utilisateur.email])
    print(f"[ALERTE] IP réinitialisée pour l’utilisateur {utilisateur.nom_complet} (email: {utilisateur.email}, téléphone: {utilisateur.telephone})")
