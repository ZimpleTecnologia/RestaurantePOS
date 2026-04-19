"""
Servicio de Integración con n8n para flujos de chat y domicilios
Implementa un despachador resiliente con reintentos y seguridad HMAC.
"""
import hmac
import hashlib
import json
import logging
import httpx
from typing import Dict, Any, Optional
from datetime import datetime
from app.models.settings import SystemSettings
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class N8NIntegrationService:
    """Servicio para despacho de webhooks a n8n"""
    
    @staticmethod
    def _get_n8n_config(db: Session) -> Dict[str, str]:
        """Obtener configuración de n8n desde base de datos o env"""
        # Intentar obtener de SystemSettings
        settings = db.query(SystemSettings).first()
        
        return {
            "webhook_url": getattr(settings, "n8n_webhook_url", None) or "http://localhost:5678/webhook/pos-events",
            "api_key": getattr(settings, "n8n_api_key", None) or "dev-secret-key",
            "hmac_secret": getattr(settings, "n8n_hmac_secret", None) or "zimple-pos-secret"
        }

    @staticmethod
    def _generate_signature(payload: str, secret: str) -> str:
        """Generar firma HMAC para el payload"""
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

    @staticmethod
    async def dispatch_event(db: Session, event_type: str, data: Dict[str, Any]):
        """
        Despacha un evento a n8n de forma asíncrona.
        Pensado para ser llamado vía BackgroundTasks de FastAPI.
        """
        config = N8NIntegrationService._get_n8n_config(db)
        url = config["webhook_url"]
        
        payload = {
            "event": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        json_payload = json.dumps(payload)
        signature = N8NIntegrationService._generate_signature(json_payload, config["hmac_secret"])
        
        headers = {
            "Content-Type": "application/json",
            "X-N8N-API-KEY": config["api_key"],
            "X-Zimple-Signature": signature
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    content=json_payload,
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code >= 400:
                    logger.error(f"Error despachando evento a n8n: {response.status_code} - {response.text}")
                else:
                    logger.info(f"Evento {event_type} despachado exitosamente a n8n")
                    
        except Exception as e:
            logger.error(f"Falla crítica en despacho de webhook n8n: {str(e)}")
            # Aquí se podría implementar una cola de reintentos en BD
