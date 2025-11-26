#!/usr/bin/env python3
"""
Test de validation améliorée des URLs avec vérification DNS et disponibilité
"""
import sys
sys.path.append('/app/backend')

from competitive_intelligence import CompetitiveIntelligence

def test_validation_improved():
    """Test de validation complète"""
    print("🧪 TEST DE VALIDATION AMÉLIORÉE DES URLs")
    print("=" * 70)
    print()
    
    ci = CompetitiveIntelligence()
    
    test_cases = [
        # (URL, should_exist, description)
        ("https://google.com", True, "Site majeur existant"),
        ("https://github.com", True, "Site majeur existant"),
        ("hubfinancial.ca", False, "Domaine qui n'existe pas (du screenshot)"),
        ("lakavitale.com", False, "Domaine qui n'existe pas (du screenshot)"),
        ("https://thisdoesnotexist123456.com", False, "Domaine inventé"),
        ("https://example.com", True, "Domaine de test standard"),
        ("www.wikipedia.org", True, "Site sans protocole"),
    ]
    
    print("Test 1: Validation simple (structure + DNS)")
    print("-" * 70)
    for url, should_exist, desc in test_cases:
        result = ci._validate_url(url, check_reachable=False)
        status = "✅" if (result is not None) == should_exist else "❌"
        exists = "EXISTS" if result is not None else "NOT FOUND"
        print(f"{status} {url:45} → {exists:10} | {desc}")
    
    print()
    print("Test 2: Validation complète (structure + DNS + disponibilité)")
    print("-" * 70)
    for url, should_exist, desc in test_cases:
        result = ci._validate_url(url, check_reachable=True)
        status = "✅" if (result is not None) == should_exist else "⚠️ "
        exists = "REACHABLE" if result is not None else "NOT REACHABLE"
        print(f"{status} {url:45} → {exists:13} | {desc}")
    
    print()
    print("=" * 70)
    print("✅ Tests terminés")
    print()
    print("💡 Note: Les URLs du screenshot (hubfinancial.ca, lakavitale.com)")
    print("   devraient maintenant être filtrées AVANT l'analyse.")

if __name__ == "__main__":
    test_validation_improved()
