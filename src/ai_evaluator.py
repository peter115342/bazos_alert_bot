import os
import json
import logging
import re
from typing import Optional, Tuple

import requests

logger = logging.getLogger(__name__)


class AIEvaluator:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        # Používáme stabilní a rychlý model z free tieru
        self.model = "gemini-2.0-flash"  # případně "gemini-2.5-flash-lite" nebo "gemini-1.5-flash"
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    def evaluate_deal(
        self,
        title: str,
        price_str: str,
        description: str = "",
        location: str = "",
    ) -> Tuple[bool, str, Optional[float]]:
        """
        Returns:
            (should_notify, reason, discount_percent)
        """
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not set – skipping AI evaluation")
            return False, "Gemini API key missing", None

        # Extrahuj číslo z ceny
        price_clean = re.sub(r"[^\d]", "", price_str or "")
        if not price_clean:
            return False, "Nelze přečíst cenu", None

        price = int(price_clean)

        prompt = f"""Jsi expert na český bazarový trh s použitou elektronikou a šperky (Bazoš, Vinted, Sbazar, Aukro).

Úkol: Ohodnoť, jestli je tato nabídka výhodná pro flipping (koupit levně a prodat dráž).

Nabídka:
- Titulek: {title}
- Cena: {price} Kč
- Lokalita: {location or "neznámá"}
- Popis: {(description or "bez popisu")[:400]}

Pravidla:
1. Odhadni realistickou tržní cenu použitého kusu v dobrém stavu v ČR (rok 2026).
2. Spočítej slevu v procentech (záporné číslo = pod tržní cenou).
3. Doporuč koupit POUZE pokud je sleva mezi 2 % a 30 % pod trhem.
4. Sleva větší než 30 % = rizikové (často vadné/podvod).
5. Cena nad trhem nebo jen minimálně pod = nekupovat.

Odpověz VÝHRADNĚ platným JSON objektem (žádný markdown, žádný další text):
{{
  "market_price_estimate": číslo,
  "discount_percent": číslo,
  "should_buy": true/false,
  "reason": "krátké zdůvodnění česky (1-2 věty)"
}}
"""

        try:
            headers = {
                "Content-Type": "application/json",
            }
            params = {
                "key": self.api_key
            }
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 400,
                    "responseMimeType": "application/json"  # Gemini umí vynutit JSON
                }
            }

            response = requests.post(
                self.base_url,
                headers=headers,
                params=params,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            # Gemini struktura odpovědi
            content = data["candidates"][0]["content"]["parts"][0]["text"].strip()

            # Vyčisti případný markdown
            if content.startswith("```"):
                content = re.sub(r"^```(?:json)?\n?", "", content)
                content = re.sub(r"\n?```$", "", content)

            result = json.loads(content)

            should_buy = bool(result.get("should_buy", False))
            discount = result.get("discount_percent")
            reason = result.get("reason", "bez důvodu")

            # Dodatečná kontrola rozsahu 2–30 %
            if should_buy and discount is not None:
                if not (2 <= abs(float(discount)) <= 30 and float(discount) < 0):
                    should_buy = False
                    reason += " (mimo rozsah 2–30 %)"

            logger.info(
                f"Gemini eval: {title[:50]}... → buy={should_buy}, discount={discount}%, reason={reason}"
            )
            return should_buy, reason, discount

        except Exception as e:
            logger.error(f"Gemini evaluation failed: {e}")
            return False, f"Chyba Gemini: {str(e)[:120]}", None
