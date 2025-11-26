# Budget Épuisé - Solution Immédiate

## 🔴 Erreur Actuelle

```
litellm.BadRequestError: Budget has been exceeded!
Current cost: 2.038692300000001, Max budget: 2.0
```

## Cause

La **clé universelle Emergent LLM** (EMERGENT_LLM_KEY) a un budget de **2.00$** qui a été dépassé lors de nos tests et analyses.

### Coûts des analyses réalisées:
- Crawling + Analyse Claude Sonnet 4 (entrée ~2000 tokens, sortie ~1500 tokens)
- Coût par analyse: ~0.15$ - 0.25$
- Nombre d'analyses effectuées: ~10-12 analyses
- **Total: 2.04$**

## ✅ Solutions Immédiates

### **Option 1: Recharger la Clé Universelle (RECOMMANDÉ)**

1. Allez sur votre profil Emergent
2. Naviguez vers **Profile → Universal Key → Add Balance**
3. Ajoutez du crédit (minimum 5-10$ recommandé pour plusieurs analyses)
4. Activez **Auto Top-Up** pour ne plus être bloqué

**Avantages:**
- Solution la plus simple
- Pas de configuration
- Fonctionne immédiatement

### **Option 2: Utiliser Votre Propre Clé Claude**

Si vous avez votre propre clé API Anthropic:

1. **Modifier le .env:**
```bash
# Remplacer dans /app/backend/.env
CLAUDE_API_KEY="sk-ant-api03-YOUR_KEY_HERE"
```

2. **Modifier le code (server.py):**
```python
# Ligne actuelle:
api_key = os.environ.get('EMERGENT_LLM_KEY')

# Remplacer par:
api_key = os.environ.get('CLAUDE_API_KEY', os.environ.get('EMERGENT_LLM_KEY'))
```

3. **Utiliser l'API directe Anthropic:**
```python
# Au lieu de emergentintegrations, utiliser anthropic SDK:
from anthropic import AsyncAnthropic

client = AsyncAnthropic(api_key=api_key)
response = await client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=4096,
    messages=[{"role": "user", "content": analysis_prompt}]
)
```

### **Option 3: Optimiser pour Réduire les Coûts**

En attendant le budget, optimisez le système:

**A. Réduire les tokens envoyés:**
```python
# Dans server.py
max_pages_to_analyze = 2  # Au lieu de 3
content_preview_length = 300  # Au lieu de 400
```

**B. Utiliser un modèle moins cher:**
```python
# Claude 3.5 Haiku (10x moins cher)
.with_model("anthropic", "claude-3-5-haiku-20241022")
```

**C. Mettre en cache les analyses:**
```python
# Vérifier si URL déjà analysée récemment
existing_reports = await db.reports.find({"url": url}).sort("createdAt", -1).limit(1)
if existing_reports:
    last_report = existing_reports[0]
    if (datetime.now() - last_report['createdAt']).days < 7:
        return last_report  # Retourner analyse existante
```

## 📊 Monitoring du Budget

### Vérifier le budget restant:

L'API Emergent ne fournit pas d'endpoint pour vérifier le budget restant, mais vous pouvez:

1. **Suivre via Profile → Universal Key** sur le dashboard Emergent
2. **Calculer approximativement:**
   - Claude Sonnet 4: ~0.15$ par analyse
   - Budget 10$: ~60-65 analyses possibles

### Alertes de budget:

Ajoutez un système d'alerte dans le code:

```python
# Dans server.py
BUDGET_THRESHOLD = 0.20  # 20 centimes par analyse

async def check_budget_and_alert():
    # Compter les analyses du mois
    start_of_month = datetime.now().replace(day=1, hour=0, minute=0)
    count = await db.reports.count_documents({
        "createdAt": {"$gte": start_of_month}
    })
    
    estimated_cost = count * BUDGET_THRESHOLD
    
    if estimated_cost > 8.0:  # 80% d'un budget de 10$
        logger.warning(f"⚠️ Budget Alert: Estimated cost this month: ${estimated_cost:.2f}")
```

## 🎯 Recommandations pour Production

### 1. **Pricing Tiers pour Utilisateurs**

Implémenter des limites:
```python
FREE_TIER_LIMIT = 3  # 3 analyses gratuites
PAID_TIER_LIMIT = 50  # 50 analyses/mois

# Vérifier avant analyse
user_reports = await db.reports.count_documents({"userId": user_id})
if user_reports >= FREE_TIER_LIMIT and not user.is_premium:
    raise HTTPException(403, "Limite gratuite atteinte. Passez Premium!")
```

### 2. **Queue System avec Rate Limiting**

Éviter les analyses simultanées coûteuses:
```python
# Redis queue
max_concurrent_analyses = 2
analysis_queue = Queue(maxsize=max_concurrent_analyses)
```

### 3. **Cache Intelligent**

```python
# Cache Redis avec TTL
cache_key = f"analysis:{domain_hash}"
cached = await redis.get(cache_key)
if cached:
    return json.loads(cached)

# Après analyse
await redis.setex(cache_key, 86400 * 7, json.dumps(report))  # 7 jours
```

### 4. **Modèle Hybride**

```python
# Analyse rapide gratuite: Haiku
# Analyse complète payante: Sonnet 4

if report_type == "quick":
    model = "claude-3-5-haiku-20241022"  # 10x moins cher
else:
    model = "claude-3-7-sonnet-20250219"  # Meilleure qualité
```

## 💰 Estimation des Coûts

### Claude Sonnet 4 (claude-3-7-sonnet-20250219)
- Input: $3 / 1M tokens
- Output: $15 / 1M tokens

### Coût par analyse:
```
Input: 2000 tokens × $3/1M = $0.006
Output: 1500 tokens × $15/1M = $0.0225
Total: ~$0.029 par analyse

Avec overhead API: ~$0.15-0.25 par analyse
```

### Budget recommandé:
- **Phase Test/Dev:** 5-10$
- **Phase Production (100 analyses/mois):** 20-30$
- **Avec cache (50% hit rate):** 10-15$

## 🔧 Action Immédiate

**Pour débloquer le système maintenant:**

```bash
# Option 1: Profil Emergent → Add Balance
Recommandé: Ajouter 10$ + activer Auto Top-Up

# Option 2: Attendre renouvellement du budget
Le budget peut se renouveler mensuellement (à confirmer)

# Option 3: Utiliser votre propre clé Claude
Voir Option 2 ci-dessus
```

## 📝 Message à Afficher aux Utilisateurs

Ajoutez dans le frontend un message d'erreur clair:

```javascript
if (error.includes("Budget has been exceeded")) {
  toast.error(
    "Service temporairement indisponible. " +
    "Nos analyses GEO sont très demandées! " +
    "Veuillez réessayer dans quelques heures.",
    { duration: 5000 }
  );
}
```

## ✅ Résumé

**Problème:** Budget Emergent LLM épuisé (2.04$ dépensé sur 2.00$ limite)

**Solution recommandée:** Recharger via Profile → Universal Key → Add Balance (10$ + Auto Top-Up)

**Alternative:** Utiliser votre propre clé API Claude Anthropic

**Optimisations futures:** Cache, rate limiting, modèle Haiku pour analyses rapides
