from corsheaders.middleware import CorsMiddleware as BaseCorsMiddleware
from django.conf import settings
import re
from django.utils.cache import patch_vary_headers
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponseForbidden

class CorsMiddleware(BaseCorsMiddleware):
    def process_response(self, request, response):
        # Obtenir l'origine de la requête
        origin = request.META.get('HTTP_ORIGIN')
        
        # Si l'origine n'est pas définie, utiliser l'origine de la requête
        if not origin and 'HTTP_ORIGIN' in request.META:
            origin = request.META['HTTP_ORIGIN']
            
        # Si toujours pas d'origine, utiliser l'origine de la requête
        if not origin and 'HTTP_REFERER' in request.META:
            origin = request.META['HTTP_REFERER']
            
        # Nettoyer l'origine (enlever le chemin)
        if origin:
            origin = origin.split('//')
            if len(origin) > 1:
                origin = f"{origin[0]}//{origin[1].split('/')[0]}"
            else:
                origin = origin[0]
        
        # Si l'origine est toujours vide, utiliser un domaine par défaut en mode debug
        if not origin and settings.DEBUG:
            origin = 'http://localhost:3000'
            
        # Vérifier si l'origine est autorisée
        allowed_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
        is_allowed = any(
            re.match(re.escape(domain).replace('\\*', '.*') + '$', origin) 
            for domain in allowed_origins
        )
        
        # En mode debug, accepter toutes les origines locales
        if not is_allowed and settings.DEBUG and any(origin.startswith(f'http://localhost:') for port in ['3000', '3001', '8000']):
            is_allowed = True
            if origin not in allowed_origins:
                allowed_origins.append(origin)
        
        # Si l'origine n'est toujours pas autorisée, retourner une erreur 403
        if not is_allowed and origin:
            return HttpResponseForbidden("Origine non autorisée")
            
        # Appel à l'implémentation parente pour gérer la logique de base de CORS
        response = super().process_response(request, response)
        
        # Définir l'origine autorisée
        if origin:
            response['Access-Control-Allow-Origin'] = origin
        
        # Toujours définir Vary: Origin pour le cache
        patch_vary_headers(response, ('Origin', 'Accept', 'Accept-Language', 'Content-Type'))
        
        # En-têtes autorisés
        response['Access-Control-Allow-Headers'] = ', '.join([
            'Accept',
            'Accept-Encoding',
            'Accept-Language',
            'Authorization',
            'Content-Type',
            'DNT',
            'Origin',
            'User-Agent',
            'X-Requested-With',
            'X-CSRFToken',
            'X-Request-ID',
        ])
        
        # Méthodes autorisées
        response['Access-Control-Allow-Methods'] = ', '.join([
            'DELETE',
            'GET',
            'OPTIONS',
            'PATCH',
            'POST',
            'PUT',
        ])
        
        # Autoriser les credentials (cookies, en-têtes d'autorisation, etc.)
        response['Access-Control-Allow-Credentials'] = 'true'
        
        # En-têtes exposés
        response['Access-Control-Expose-Headers'] = ', '.join([
            'Content-Type',
            'Content-Length',
            'Content-Disposition',
            'X-Content-Type-Options',
            'Authorization',
            'X-Request-ID',
        ])
        
        # Durée de mise en cache des pré-vérifications CORS (en secondes)
        max_age = 86400  # 24 heures
        response['Access-Control-Max-Age'] = str(max_age)
        
        # Ajouter un en-tête X-Content-Type-Options pour la sécurité
        if 'X-Content-Type-Options' not in response:
            response['X-Content-Type-Options'] = 'nosniff'
        
        # Gérer les requêtes preflight (OPTIONS)
        if request.method == 'OPTIONS':
            response.status_code = 200
            # Ajouter des en-têtes supplémentaires pour les requêtes OPTIONS
            response['Access-Control-Allow-Headers'] = ', '.join([
                'accept',
                'accept-encoding',
                'accept-language',
                'authorization',
                'content-type',
                'dnt',
                'origin',
                'user-agent',
                'x-csrftoken',
                'x-requested-with',
                'x-request-id',
            ])
            
            # Ajouter un en-tête de cache pour les pré-vérifications
            response['Cache-Control'] = f'max-age={max_age}, public'
            response['Expires'] = (timezone.now() + timedelta(seconds=max_age)).strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        # Ajouter des en-têtes de sécurité
        if 'Access-Control-Allow-Origin' in response and origin != '*':
            # Ne définir Vary: Origin que si l'origine est spécifique
            patch_vary_headers(response, ('Origin',))
            
            # Ajouter des en-têtes de sécurité supplémentaires
            security_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block',
                'Referrer-Policy': 'same-origin',
            }
            
            for header, value in security_headers.items():
                if header not in response:
                    response[header] = value
        
        return response
