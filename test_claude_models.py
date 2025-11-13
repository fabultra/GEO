#!/usr/bin/env python3
"""
Test Claude models to see which ones are available with current API key
"""
import os
from anthropic import Anthropic

def test_claude_models():
    """Test different Claude model versions"""
    
    # Get API key
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment")
        return
    
    print(f"🔑 Using API key: {api_key[:20]}...")
    
    client = Anthropic(api_key=api_key)
    
    # Models to test
    models_to_test = [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-sonnet-20240620", 
        "claude-3-5-sonnet-latest",
        "claude-3-5-sonnet",
        "claude-3-haiku-20240307",
        "claude-3-opus-20240229"
    ]
    
    working_models = []
    
    for model in models_to_test:
        print(f"\n🔍 Testing model: {model}")
        try:
            response = client.messages.create(
                model=model,
                max_tokens=50,
                messages=[{
                    "role": "user",
                    "content": "Respond with 'OK' if you receive this message."
                }]
            )
            
            response_text = response.content[0].text
            print(f"✅ SUCCESS: {response_text}")
            working_models.append(model)
            
        except Exception as e:
            print(f"❌ FAILED: {str(e)}")
    
    print(f"\n📊 SUMMARY:")
    print(f"Working models: {len(working_models)}")
    for model in working_models:
        print(f"  ✅ {model}")
    
    if not working_models:
        print("❌ No Claude models are working with this API key!")
    
    return working_models

if __name__ == "__main__":
    test_claude_models()