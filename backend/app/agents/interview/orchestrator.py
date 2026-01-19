"""
Interview Orchestrator
======================
Agentic orchestrator for SCID-based structured clinical interviews.
Uses MCP tools to guide adaptive, natural conversation flow.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from app.agents.base import BaseAgent, AgentOutput
from app.agents.interview.state import InterviewPhase, InterviewState, state_manager

logger = logging.getLogger(__name__)


class InterviewOrchestrator(BaseAgent):
    """
    Orchestrates SCID-based structured clinical interviews.
    
    Adaptive Flow:
    1. Demographics → Determines which SCID-SC items to use
    2. SCID-SC Screening → Determines which SCID-CV modules to deploy
    3. SCID-CV Module → Full diagnostic assessment
    
    Uses MCP tools internally for each step.
    """
    
    def __init__(self, llm_client=None, **kwargs):
        super().__init__(agent_name="InterviewOrchestrator", **kwargs)
        self.llm_client = llm_client
        self._load_scid_bank()
    
    def _load_scid_bank(self):
        """Load SCID-SC item bank"""
        try:
            from app.agents.interview.scid_bank import SCID_SC_Bank
            self.scid_bank = SCID_SC_Bank()
            logger.info(f"Loaded SCID bank: {len(self.scid_bank.sc_items)} items, {len(self.scid_bank.modules)} modules")
        except Exception as e:
            logger.warning(f"Could not load SCID bank: {e}")
            self.scid_bank = None
    
    async def get_next_step(self, session_id: str, patient_id: str, user_message: str = "") -> Dict[str, Any]:
        """
        MCP Tool: Get next interview step based on current state.
        
        Returns:
            - phase: Current interview phase
            - action: "ask_question" | "transition" | "complete"
            - question: Next question to ask (if action is ask_question)
            - module: Module being assessed (if in deep_dive)
            - progress: Current progress percentage
        """
        state = state_manager.get_or_create(session_id, patient_id)
        
        # Process user response if provided
        if user_message and state.current_question_id:
            await self._process_response(state, state.current_question_id, user_message)
        
        # Determine next action based on phase
        if state.phase == InterviewPhase.OVERVIEW:
            return await self._handle_overview_phase(state)
        
        elif state.phase == InterviewPhase.SCREENING:
            return await self._handle_screening_phase(state)
        
        elif state.phase == InterviewPhase.DEEP_DIVE:
            return await self._handle_deep_dive_phase(state)
        
        elif state.phase == InterviewPhase.TIMELINE:
            return await self._handle_timeline_phase(state)
        
        elif state.phase == InterviewPhase.SUMMARY:
            return await self._handle_summary_phase(state)
        
        return {"action": "complete", "phase": state.phase.value}
    
    async def _handle_overview_phase(self, state: InterviewState) -> Dict[str, Any]:
        """Handle initial overview phase"""
        
        # Check if we have enough info to move to screening
        if len(state.asked_questions) >= 2:
            # Transition to screening
            state.phase = InterviewPhase.SCREENING
            state_manager.save(state)
            
            # Select screening items based on demographics
            priority_items = await self._select_screening_items(state)
            state.priority_modules = [item["linked_modules"][0] for item in priority_items if item.get("linked_modules")]
            state_manager.save(state)
            
            return {
                "action": "transition",
                "phase": "screening",
                "message": "Thank you for sharing. I'd like to ask some more specific questions now.",
                "next_question": priority_items[0] if priority_items else None
            }
        
        # Ask overview questions
        overview_questions = [
            {"id": "OV_1", "text": "What brings you here today? What's been on your mind?"},
            {"id": "OV_2", "text": "How long have you been experiencing these feelings or concerns?"},
        ]
        
        for q in overview_questions:
            if q["id"] not in state.asked_questions:
                state.current_question_id = q["id"]
                state.asked_questions.append(q["id"])
                state_manager.save(state)
                
                return {
                    "action": "ask_question",
                    "phase": "overview",
                    "question_id": q["id"],
                    "question_text": q["text"],
                    "is_open_ended": True
                }
        
        # All overview questions asked, transition
        state.phase = InterviewPhase.SCREENING
        state_manager.save(state)
        return await self._handle_screening_phase(state)
    
    async def _handle_screening_phase(self, state: InterviewState) -> Dict[str, Any]:
        """Handle SCID-SC screening phase"""
        
        if not self.scid_bank:
            # Skip to summary if no SCID bank
            state.phase = InterviewPhase.SUMMARY
            state_manager.save(state)
            return await self._handle_summary_phase(state)
        
        # Get screening items to ask
        screening_items = await self._get_remaining_screening_items(state)
        
        if not screening_items:
            # Screening complete, determine modules to deploy
            modules_to_deploy = self._determine_modules_to_deploy(state)
            
            if modules_to_deploy:
                state.phase = InterviewPhase.DEEP_DIVE
                state.priority_modules = modules_to_deploy
                state.current_module = modules_to_deploy[0]
                state_manager.save(state)
                
                module_name = self.scid_bank.modules.get(modules_to_deploy[0])
                module_display = module_name.name if module_name else modules_to_deploy[0]
                
                return {
                    "action": "transition",
                    "phase": "deep_dive",
                    "message": f"Based on your responses, I'd like to explore {module_display} in more detail.",
                    "modules": modules_to_deploy
                }
            else:
                # No modules to deploy, go to summary
                state.phase = InterviewPhase.SUMMARY
                state_manager.save(state)
                return await self._handle_summary_phase(state)
        
        # Ask next screening question
        next_item = screening_items[0]
        state.current_question_id = next_item.id
        state.asked_questions.append(next_item.id)
        state_manager.save(state)
        
        return {
            "action": "ask_question",
            "phase": "screening",
            "question_id": next_item.id,
            "question_text": next_item.text,
            "category": next_item.category,
            "linked_modules": next_item.linked_modules,
            "is_open_ended": False,
            "progress": len(state.asked_questions) / max(1, len(screening_items) + len(state.asked_questions))
        }
    
    async def _handle_deep_dive_phase(self, state: InterviewState) -> Dict[str, Any]:
        """Handle SCID-CV module deep dive"""
        
        if not state.current_module:
            # No current module, check if more to deploy
            remaining = [m for m in state.priority_modules if m not in state.deployed_modules]
            
            if remaining:
                state.current_module = remaining[0]
                state_manager.save(state)
            else:
                # All modules complete, go to timeline
                state.phase = InterviewPhase.TIMELINE
                state_manager.save(state)
                return await self._handle_timeline_phase(state)
        
        # Get next question from current module
        module = self.scid_bank.modules.get(state.current_module) if self.scid_bank else None
        if not module:
            state.deployed_modules.append(state.current_module)
            state.current_module = None
            state_manager.save(state)
            return await self._handle_deep_dive_phase(state)
        
        # Get module questions (using linked items from SCID-SC)
        module_items = self.scid_bank.get_items_by_module(state.current_module)
        current_index = state.module_progress.get(state.current_module, 0)
        
        if current_index >= len(module_items):
            # Module complete
            state.deployed_modules.append(state.current_module)
            state.current_module = None
            state_manager.save(state)
            return await self._handle_deep_dive_phase(state)
        
        item = module_items[current_index]
        state.current_question_id = item.id
        state.module_progress[state.current_module] = current_index + 1
        state_manager.save(state)
        
        return {
            "action": "ask_question",
            "phase": "deep_dive",
            "module_id": state.current_module,
            "module_name": module.name,
            "question_id": item.id,
            "question_text": item.text,
            "progress": (current_index + 1) / len(module_items)
        }
    
    async def _handle_timeline_phase(self, state: InterviewState) -> Dict[str, Any]:
        """Handle timeline and severity assessment"""
        
        timeline_questions = [
            {"id": "TL_1", "text": "How long have you been experiencing these difficulties? When did they first start?"},
            {"id": "TL_2", "text": "How have these symptoms affected your daily life, work, or relationships?"},
        ]
        
        for q in timeline_questions:
            if q["id"] not in state.asked_questions:
                state.current_question_id = q["id"]
                state.asked_questions.append(q["id"])
                state_manager.save(state)
                
                return {
                    "action": "ask_question",
                    "phase": "timeline",
                    "question_id": q["id"],
                    "question_text": q["text"],
                    "is_open_ended": True
                }
        
        # Timeline complete, go to summary
        state.phase = InterviewPhase.SUMMARY
        state_manager.save(state)
        return await self._handle_summary_phase(state)
    
    async def _handle_summary_phase(self, state: InterviewState) -> Dict[str, Any]:
        """Handle summary and wrap-up"""
        
        return {
            "action": "complete",
            "phase": "summary",
            "message": "Thank you for taking the time to share with me. I have a good understanding of what you're experiencing now.",
            "modules_assessed": state.deployed_modules,
            "positive_screens": state.positive_screens,
            "ready_for_diagnosis": True
        }
    
    async def _process_response(self, state: InterviewState, question_id: str, response: str):
        """Process user response to a question using Semantic Analysis"""
        
        # Check if it's a screening question
        if self.scid_bank and question_id in self.scid_bank.sc_items:
            item = self.scid_bank.sc_items[question_id]
            
            # Semantic Analysis via LLM
            # (We use the therapist's LLM client if available, or create a new one)
            from app.core.llm_client import AgentLLMClient
            llm = self.llm_client or AgentLLMClient(agent_name="Orchestrator")
            
            prompt = f"""Analyze the patient's response to a clinical question.

Question: "{item.text}"
Patient Response: "{response}"

Determine if the response is:
- POSITIVE (Yes, I have experienced this)
- NEGATIVE (No, I haven't)
- AMBIGUOUS (Unclear, evasive, or unrelated)

Return ONLY one word: POSITIVE, NEGATIVE, or AMBIGUOUS."""
            
            try:
                analysis = await llm.generate_async(prompt, max_tokens=10, temperature=0.0)
                analysis = analysis.strip().upper()
                logger.debug(f"Semantic Analysis for {question_id}: {analysis} (Resp: {response[:20]}...)")
            except Exception as e:
                logger.error(f"Semantic analysis failed: {e}")
                # Fallback to keyword matching
                positive_indicators = ["yes", "yeah", "yep", "definitely", "i have", "i do", "i am"]
                is_positive = any(ind in response.lower() for ind in positive_indicators)
                analysis = "POSITIVE" if is_positive else "NEGATIVE"

            if "POSITIVE" in analysis:
                state.screening_scores[question_id] = 1.0
                for module_id in item.linked_modules:
                    if module_id not in state.positive_screens:
                        state.positive_screens.append(module_id)
            elif "NEGATIVE" in analysis:
                state.screening_scores[question_id] = 0.0
                
                # CHECK SKIP LOGIC
                if item.skip_module_if_negative:
                    # Skip all other items linked to these modules
                    for mod_id in item.linked_modules:
                        # Find all items linked to this module
                        module_items = self.scid_bank.get_items_by_module(mod_id)
                        for skip_item in module_items:
                            if skip_item.id != question_id and skip_item.id not in state.skipped_items:
                                state.skipped_items.append(skip_item.id)
                                logger.info(f"Skipping {skip_item.id} due to negative response on {question_id}")
            else:
                # Ambiguous - treat as 0.5 or flag for follow-up
                # For now, treat as non-positive for screening triggers to avoid over-triggering
                state.screening_scores[question_id] = 0.5
            
            state_manager.save(state)
    
    async def _select_screening_items(self, state: InterviewState) -> List[Dict]:
        """Select SCID-SC screening items based on demographics and initial concerns"""
        
        if not self.scid_bank:
            return []
        
        # Priority categories based on demographics
        # (In a full implementation, this would use the demographics data)
        default_categories = ["mood", "anxiety", "trauma", "substance"]
        
        selected_items = []
        for category in default_categories:
            items = self.scid_bank.get_items_by_category(category)
            if items:
                selected_items.extend(items[:2])  # First 2 items per category
        
        return selected_items
    
    async def _get_remaining_screening_items(self, state: InterviewState) -> List:
        """Get screening items not yet asked"""
        
        if not self.scid_bank:
            return []
        
        # Get priority items
        selected = await self._select_screening_items(state)
        
        # Filter out already asked AND skipped items
        remaining = [
            item for item in selected 
            if item.id not in state.asked_questions and item.id not in state.skipped_items
        ]
        
        # Limit to reasonable number
        return remaining[:10]
    
    def _determine_modules_to_deploy(self, state: InterviewState) -> List[str]:
        """Determine which SCID-CV modules to deploy based on positive screens"""
        
        # Get modules with positive screens
        modules = list(set(state.positive_screens))
        
        # Sort by priority (can be customized based on severity)
        if self.scid_bank:
            modules.sort(
                key=lambda m: self.scid_bank.modules.get(m).priority_weight if m in self.scid_bank.modules else 0,
                reverse=True
            )
        
        # Limit to top 2-3 modules
        return modules[:3]
    
    async def process(self, state: Dict) -> AgentOutput:
        """Main agent process method"""
        
        session_id = state.get("session_id")
        patient_id = state.get("patient_id")
        user_message = state.get("user_message", "")
        
        result = await self.get_next_step(session_id, patient_id, user_message)
        
        return AgentOutput(
            content=result,
            metadata={
                "phase": result.get("phase"),
                "action": result.get("action")
            }
        )


__all__ = ["InterviewOrchestrator"]
