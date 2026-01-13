from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import Utilisateur
import json

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Endpoint de connexion pour Ma Caisse
    Compatible avec le format attendu par le frontend
    """
    try:
        print(f"DEBUG: Login request received")
        print(f"DEBUG: Request method: {request.method}")
        print(f"DEBUG: Request body: {request.body}")
        
        data = json.loads(request.body)
        # Support both email and username fields for compatibility
        email = data.get('email') or data.get('username')
        password = data.get('password')
        
        print(f"DEBUG: Email/Username: {email}, Password provided: {bool(password)}")
        
        if not email or not password:
            return Response({
                'error': 'Email/Username et mot de passe requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier l'utilisateur - support email ou téléphone
        try:
            # Try to find user by email first, then by phone
            user = None
            try:
                user = Utilisateur.objects.get(email=email)
            except Utilisateur.DoesNotExist:
                # If not found by email, try by telephone
                user = Utilisateur.objects.get(telephone=email)
            
            print(f"DEBUG: Found user: {user.email}")
            print(f"DEBUG: User active: {user.is_active if hasattr(user, 'is_active') else 'N/A'}")
            password_valid = user.check_password(password)
            print(f"DEBUG: Password valid: {password_valid}")
            if password_valid:
                # Générer les tokens JWT
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)
                
                # Format de réponse compatible avec le frontend
                user_data = {
                    'id': str(user.id),
                    'username': user.email.split('@')[0],
                    'email': user.email,
                    'first_name': user.nom_complet.split(' ')[0] if user.nom_complet else '',
                    'last_name': ' '.join(user.nom_complet.split(' ')[1:]) if user.nom_complet else '',
                    'phone': user.telephone or '',
                    'role': 'CUSTOMER',
                    'country_of_residence': None,
                    'country_of_origin': None,
                    'is_verified': True,
                    'email_verified': False,
                    'phone_verified': False,
                    'created_at': user.date_inscription.isoformat() if hasattr(user, 'date_inscription') else '',
                    'updated_at': user.date_inscription.isoformat() if hasattr(user, 'date_inscription') else ''
                }
                
                return Response({
                    'access': access_token,
                    'refresh': refresh_token,
                    'tokens': {
                        'access': access_token,
                        'refresh': refresh_token
                    },
                    'user': user_data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Identifiants incorrects'
                }, status=status.HTTP_401_UNAUTHORIZED)
                
        except Utilisateur.DoesNotExist:
            return Response({
                'error': 'Utilisateur non trouvé'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except json.JSONDecodeError:
        return Response({
            'error': 'Format JSON invalide'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': f'Erreur serveur: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def profile_view(request):
    """
    Endpoint pour récupérer le profil utilisateur
    """
    if not request.user.is_authenticated:
        return Response({
            'error': 'Non authentifié'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    user = request.user
    user_data = {
        'id': str(user.id),
        'username': user.email.split('@')[0],
        'email': user.email,
        'first_name': user.nom_complet.split(' ')[0] if user.nom_complet else '',
        'last_name': ' '.join(user.nom_complet.split(' ')[1:]) if user.nom_complet else '',
        'phone': user.telephone or '',
        'role': 'CUSTOMER',
        'country_of_residence': None,
        'country_of_origin': None,
        'is_verified': True,
        'email_verified': False,
        'phone_verified': False,
        'created_at': user.date_creation.isoformat() if hasattr(user, 'date_creation') else '',
        'updated_at': user.date_creation.isoformat() if hasattr(user, 'date_creation') else ''
    }
    
    return Response(user_data, status=status.HTTP_200_OK)
