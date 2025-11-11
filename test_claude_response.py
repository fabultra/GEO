"""Script de test pour vérifier la réponse de Claude"""
import asyncio
import os
import json
from emergentintegrations.llm.chat import LlmChat, UserMessage

async def test_claude():
    api_key = os.environ.get('EMERGENT_LLM_KEY', 'sk-emergent-1FaAbE34622033dC70')
    
    test_prompt = """
IMPORTANT: Répondez UNIQUEMENT en JSON valide. Pas de texte avant ou après.
Descriptions sur UNE seule ligne. Échappez les guillemets avec \\"

Analysez ce site: https://example.com

JSON REQUIS:
{
  "scores": {"structure": 7.5, "infoDensity": 3.0, "readability": 5.0, "eeat": 6.0, "educational": 2.0, "thematic": 4.5, "aiOptimization": 3.5, "visibility": 2.5, "global_score": 4.25},
  "detailed_observations": {
    "structure": {"score_justification": "Justification courte", "specific_problems": ["Prob 1"], "positive_points": ["Point 1"], "missing_elements": ["Element 1"]}
  },
  "recommendations": [
    {"title": "Titre", "criterion": "structure", "impact": "high", "effort": "low", "priority": 1, "description": "Description courte", "example": "Exemple"}
  ],
  "quick_wins": [
    {"title": "Action", "impact": "Impact", "time_required": "1h", "description": "Description"}
  ],
  "analysis": {"strengths": ["Force 1"], "weaknesses": ["Faiblesse 1"], "opportunities": ["Opp 1"]},
  "executive_summary": {"global_assessment": "Eval", "critical_issues": ["Issue 1"], "key_opportunities": ["Opp 1"], "estimated_visibility_loss": "50%", "recommended_investment": "10k"},
  "roi_estimation": {"current_situation": "Current", "potential_improvement": "Potential", "timeline": "6 mois"}
}

Générez ce JSON avec des scores réalistes pour example.com
"""
    
    try:
        chat = LlmChat(
            api_key=api_key,
            session_id="test_session",
            system_message="Vous êtes un expert GEO. Répondez UNIQUEMENT en JSON valide."
        ).with_model("anthropic", "claude-3-7-sonnet-20250219")
        
        user_message = UserMessage(text=test_prompt)
        response = await chat.send_message(user_message)
        
        print("=" * 80)
        print("RÉPONSE BRUTE DE CLAUDE:")
        print("=" * 80)
        print(response)
        print("\n" + "=" * 80)
        
        # Tenter de parser
        response_text = response.strip()
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0]
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0]
        
        response_text = response_text.strip()
        
        try:
            parsed = json.loads(response_text)
            print("✅ JSON VALIDE!")
            print(json.dumps(parsed, indent=2, ensure_ascii=False))
        except json.JSONDecodeError as e:
            print(f"❌ ERREUR JSON: {e}")
            print(f"\nPremiers 1000 caractères:")
            print(response_text[:1000])
            
    except Exception as e:
        print(f"❌ ERREUR: {e}")

if __name__ == "__main__":
    asyncio.run(test_claude())
