"""
Symptom Extractors
==================
NER and LLM-based symptom extraction components.
"""

from typing import Dict, List, Optional
from abc import ABC, abstractmethod
import asyncio
import logging

from app.agents.sra.symptom_db import DSM5SymptomDatabase


logger = logging.getLogger(__name__)


class BaseExtractor(ABC):
    """Base class for symptom extractors"""
    
    @abstractmethod
    async def extract(self, text: str, context: str = "") -> List[Dict]:
        """Extract symptoms from text"""
        pass


class NERExtractor(BaseExtractor):
    """
    Fast, local NER-based symptom extraction.
    Uses pattern matching for speed (< 50ms).
    """
    
    def __init__(self):
        self.db = DSM5SymptomDatabase()
    
    async def extract(self, text: str, context: str = "") -> List[Dict]:
        """
        Extract symptoms using pattern matching.
        
        Args:
            text: User message
            context: Conversation context (optional)
            
        Returns:
            List of extracted symptoms
        """
        # Run pattern matching (fast, local)
        symptoms = self.db.match_symptoms(text)
        
        # Also check context for additional symptoms
        if context:
            context_symptoms = self.db.match_symptoms(context)
            # Add context symptoms that aren't already found
            existing_names = {s["name"] for s in symptoms}
            for cs in context_symptoms:
                if cs["name"] not in existing_names:
                    cs["source"] = "context"
                    symptoms.append(cs)
        
        return symptoms


class LLMExtractor(BaseExtractor):
    """
    LLM-based semantic symptom extraction.
    More accurate but slower (1-2s).
    """
    
    EXTRACTION_PROMPT = """
    Analyze this message for mental health symptoms.
    
    Message: {message}
    Context: {context}
    
    Extract symptoms in JSON format:
    {{
        "symptoms": [
            {{
                "name": "symptom name",
                "category": "depressive|anxiety|trauma|bipolar|other",
                "severity": 0.1-1.0,
                "frequency": "daily|weekly|occasional|rare",
                "duration": "days|weeks|months|years",
                "evidence": "quote from text"
            }}
        ],
        "implicit_symptoms": [
            {{
                "name": "inferred symptom",
                "reasoning": "why this was inferred"
            }}
        ]
    }}
    
    Be thorough but only extract symptoms actually mentioned or clearly implied.
    Return valid JSON only.
    """
    
    def __init__(self, llm_client=None):
        self.llm = llm_client
    
    async def extract(self, text: str, context: str = "") -> List[Dict]:
        """
        Extract symptoms using LLM semantic analysis.
        
        Args:
            text: User message
            context: Conversation context
            
        Returns:
            List of extracted symptoms
        """
        if not self.llm:
            logger.warning("LLM client not configured, falling back to NER")
            return await NERExtractor().extract(text, context)
        
        try:
            prompt = self.EXTRACTION_PROMPT.format(
                message=text,
                context=context[:500] if context else "None"
            )
            
            response = await self.llm.generate_async(prompt)
            symptoms = self._parse_response(response)
            return symptoms
            
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            # Fallback to NER
            return await NERExtractor().extract(text, context)
    
    def _parse_response(self, response: str) -> List[Dict]:
        """Parse LLM response into symptom list"""
        import json
        
        try:
            # Find JSON in response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(response[start:end])
                symptoms = data.get("symptoms", [])
                
                # Add implicit symptoms
                for implicit in data.get("implicit_symptoms", []):
                    symptoms.append({
                        "name": implicit["name"],
                        "category": "inferred",
                        "severity": 0.5,
                        "source": "implicit",
                        "reasoning": implicit.get("reasoning", "")
                    })
                
                return symptoms
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM response: {e}")
        
        return []


class SymptomExtractor:
    """
    Combined symptom extractor using both NER and LLM.
    
    Pipeline:
    1. Fast NER extraction (immediate)
    2. LLM semantic extraction (parallel)
    3. Consolidate and deduplicate
    """
    
    def __init__(self, llm_client=None):
        self.ner = NERExtractor()
        self.llm = LLMExtractor(llm_client)
    
    async def extract(
        self,
        text: str,
        context: str = "",
        use_llm: bool = True
    ) -> List[Dict]:
        """
        Extract symptoms using hybrid approach.
        
        Args:
            text: User message
            context: Conversation context
            use_llm: Whether to use LLM extraction
            
        Returns:
            Consolidated list of symptoms
        """
        if use_llm:
            # Run both extractors in parallel
            ner_task = self.ner.extract(text, context)
            llm_task = self.llm.extract(text, context)
            
            ner_symptoms, llm_symptoms = await asyncio.gather(
                ner_task, llm_task
            )
            
            # Consolidate
            symptoms = self._consolidate(ner_symptoms, llm_symptoms)
        else:
            symptoms = await self.ner.extract(text, context)
        
        return symptoms
    
    def _consolidate(
        self,
        ner_symptoms: List[Dict],
        llm_symptoms: List[Dict]
    ) -> List[Dict]:
        """
        Consolidate symptoms from both sources.
        LLM results take priority for severity and details.
        """
        consolidated = {}
        
        # Add NER symptoms first
        for symptom in ner_symptoms:
            name = symptom["name"].lower()
            consolidated[name] = symptom
            consolidated[name]["source"] = "ner"
        
        # Add/update with LLM symptoms
        for symptom in llm_symptoms:
            name = symptom.get("name", "").lower()
            if not name:
                continue
                
            if name in consolidated:
                # Update with LLM details (more accurate)
                consolidated[name].update({
                    "severity": symptom.get("severity", consolidated[name].get("severity", 0.5)),
                    "frequency": symptom.get("frequency") or consolidated[name].get("frequency"),
                    "duration": symptom.get("duration") or consolidated[name].get("duration"),
                    "source": "both"
                })
            else:
                consolidated[name] = symptom
                consolidated[name]["source"] = "llm"
        
        return list(consolidated.values())


__all__ = ["SymptomExtractor", "NERExtractor", "LLMExtractor"]
