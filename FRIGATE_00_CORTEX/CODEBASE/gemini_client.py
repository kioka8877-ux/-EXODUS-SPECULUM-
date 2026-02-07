#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate CORTEX - Client Gemini
Gestion de l'API Gemini 1.5 Pro avec rate limiting.
"""

import os
import time
import json
import base64
from pathlib import Path
from typing import Dict, Any, List, Optional
import google.generativeai as genai


class GeminiClient:
    """
    Client pour Gemini 1.5 Pro avec gestion des rate limits.
    
    Free tier: 1500 req/jour, 60 QPM (1 req/sec)
    """
    
    MODEL_NAME = "gemini-1.5-pro"
    MIN_REQUEST_INTERVAL = 1.1
    MAX_RETRIES = 3
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: Clé API Gemini (ou via GEMINI_API_KEY env var)
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY non trouvée. "
                "Définir via: os.environ['GEMINI_API_KEY'] = 'votre_clé'"
            )
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.MODEL_NAME)
        self.last_request_time = 0
        self.request_count = 0
        
        print(f"🧠 GeminiClient initialisé")
        print(f"   Modèle: {self.MODEL_NAME}")
    
    def _wait_for_rate_limit(self):
        """Attend si nécessaire pour respecter le rate limit."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.MIN_REQUEST_INTERVAL:
            wait_time = self.MIN_REQUEST_INTERVAL - elapsed
            time.sleep(wait_time)
    
    def _encode_image(self, image_path: str) -> Dict[str, Any]:
        """Encode une image en base64 pour l'API."""
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        
        ext = Path(image_path).suffix.lower()
        mime_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp"
        }
        mime_type = mime_types.get(ext, "image/png")
        
        return {
            "mime_type": mime_type,
            "data": image_data
        }
    
    def analyze_image(self, 
                      image_path: str, 
                      prompt: str,
                      retry_count: int = 0) -> Dict[str, Any]:
        """
        Analyse une image avec un prompt.
        
        Args:
            image_path: Chemin de l'image
            prompt: Prompt d'analyse
            retry_count: Compteur de retry (interne)
            
        Returns:
            Dict avec la réponse parsée
        """
        self._wait_for_rate_limit()
        
        try:
            image_data = self._encode_image(image_path)
            
            response = self.model.generate_content([
                {"inline_data": image_data},
                prompt
            ])
            
            self.last_request_time = time.time()
            self.request_count += 1
            
            text = response.text
            try:
                if "```json" in text:
                    json_str = text.split("```json")[1].split("```")[0]
                elif "```" in text:
                    json_str = text.split("```")[1].split("```")[0]
                else:
                    json_str = text
                
                return {
                    "status": "success",
                    "data": json.loads(json_str.strip()),
                    "raw_response": text
                }
            except json.JSONDecodeError:
                return {
                    "status": "success",
                    "data": None,
                    "raw_response": text
                }
                
        except Exception as e:
            error_msg = str(e)
            
            if "429" in error_msg or "quota" in error_msg.lower():
                if retry_count < self.MAX_RETRIES:
                    wait_time = (retry_count + 1) * 30
                    print(f"   ⚠️ Rate limit, attente {wait_time}s...")
                    time.sleep(wait_time)
                    return self.analyze_image(image_path, prompt, retry_count + 1)
            
            return {
                "status": "error",
                "error": error_msg,
                "data": None
            }
    
    def analyze_multiple_images(self,
                                 image_paths: List[str],
                                 prompt: str) -> Dict[str, Any]:
        """
        Analyse plusieurs images ensemble.
        
        Args:
            image_paths: Liste des chemins d'images
            prompt: Prompt d'analyse
            
        Returns:
            Dict avec la réponse
        """
        self._wait_for_rate_limit()
        
        try:
            content = []
            for path in image_paths:
                content.append({"inline_data": self._encode_image(path)})
            content.append(prompt)
            
            response = self.model.generate_content(content)
            
            self.last_request_time = time.time()
            self.request_count += 1
            
            text = response.text
            try:
                if "```json" in text:
                    json_str = text.split("```json")[1].split("```")[0]
                else:
                    json_str = text
                return {
                    "status": "success",
                    "data": json.loads(json_str.strip()),
                    "raw_response": text
                }
            except json.JSONDecodeError:
                return {
                    "status": "success", 
                    "data": None,
                    "raw_response": text
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "data": None
            }
