"""Test de l'API Anthropic directe avec la clé utilisateur"""
import asyncio
import os
from anthropic import AsyncAnthropic

async def test_anthropic():
    api_key = os.environ.get('ANTHROPIC_API_KEY', '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')
    
    print(f"🔑 Utilisation de la clé: {api_key[:20]}...")
    
    try:
        client = AsyncAnthropic(api_key=api_key)
        
        response = await client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1000,
            temperature=0.3,
            system="Vous êtes un expert en GEO.",
            messages=[
                {
                    "role": "user",
                    "content": "Donnez-moi un score GEO de 0-10 pour le site example.com et expliquez en 2 phrases."
                }
            ]
        )
        
        print("\n✅ SUCCÈS! Réponse reçue:")
        print("=" * 80)
        print(response.content[0].text)
        print("=" * 80)
        print(f"\nTokens utilisés: Input={response.usage.input_tokens}, Output={response.usage.output_tokens}")
        print(f"Coût estimé: ~${(response.usage.input_tokens * 3 + response.usage.output_tokens * 15) / 1000000:.4f}")
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")

if __name__ == "__main__":
    asyncio.run(test_anthropic())
