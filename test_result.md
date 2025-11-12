#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: |
  Développer une plateforme SaaS complète de Generative Engine Optimization (GEO) avec 5 modules avancés:
  - Module 1: Tests de visibilité actifs dans ChatGPT, Claude, Perplexity, Gemini
  - Module 2: Génération automatique de 10 articles GEO-optimisés (2000+ mots)
  - Module 3: Intelligence compétitive - Reverse-engineering des compétiteurs
  - Module 4: Génération automatique de schemas JSON-LD (Organization, FAQ, Article, etc.)
  - Module 5: Expansion de requêtes (20 → 500+ variations)
  Deliverables: Rapport Word 50-70 pages, Dashboard HTML interactif, exports JSON/XLSX/MD

backend:
  - task: "Module 1: Visibility Testing (ChatGPT, Claude, Perplexity, Gemini)"
    implemented: true
    working: true
    file: "/app/backend/visibility_tester.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: true
          agent: "main"
          comment: "Module complet avec analyse détaillée (position, sentiment, contexte). Intégré dans process_analysis_job."
  
  - task: "Module 2: Automatic Content Generation (10 articles GEO-optimized)"
    implemented: true
    working: "NA"
    file: "/app/backend/content_generator.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Module créé avec logique complète pour générer 10 articles de 2500-3000 mots via Claude. Pas encore intégré dans le pipeline principal. À tester."
  
  - task: "Module 3: Competitive Intelligence"
    implemented: true
    working: true
    file: "/app/backend/competitive_intelligence.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Module complet créé avec analyse des compétiteurs, tableau comparatif et insights actionnables. NOUVELLEMENT intégré dans server.py process_analysis_job. À tester."
        - working: true
          agent: "testing"
          comment: "✅ TESTÉ ET FONCTIONNEL - Module intégré avec succès dans le pipeline. Génère competitive_intelligence avec competitors_analyzed, analyses, comparative_metrics et actionable_insights. Testé avec sekoia.ca, 1 compétiteur analysé. Minor: URL parsing needs cleanup but core functionality works."
  
  - task: "Module 4: Schema JSON-LD Generator"
    implemented: true
    working: "NA"
    file: "/app/backend/schema_generator.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Module créé avec génération de 9 types de schemas (Organization, Website, FAQPage, Article, LocalBusiness, Service, HowTo, Review, Breadcrumb). NOUVELLEMENT intégré dans server.py. À tester."
  
  - task: "Module 5: Query Expansion (20 → 500+ queries)"
    implemented: false
    working: "NA"
    file: "/app/backend/query_generator.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Le fichier query_generator.py existe mais génère seulement 20 requêtes. L'expansion vers 500+ requêtes n'est pas encore implémentée."
  
  - task: "Word Report Generator (50-70 pages)"
    implemented: true
    working: true
    file: "/app/backend/word_report_generator.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: true
          agent: "main"
          comment: "Module complet avec génération de rapport de 50-70 pages incluant: cover page, executive summary, introduction GEO, méthodologie, analyse des 8 critères, recommandations, plan d'action 12 mois, ROI estimation, annexes."
  
  - task: "HTML Dashboard Generator"
    implemented: true
    working: true
    file: "/app/backend/dashboard_generator.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: true
          agent: "main"
          comment: "Dashboard HTML interactif créé avec Chart.js pour graphique radar, barres de progression par plateforme, métriques clés, quick wins et recommandations."
  
  - task: "Database Manager (History & Alerts)"
    implemented: true
    working: "NA"
    file: "/app/backend/database_manager.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Module existant avec SQLite pour historique des analyses et génération d'alertes. Intégré dans process_analysis_job mais non testé."
  
  - task: "Core Analysis Pipeline Integration"
    implemented: true
    working: "NA"
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "critical"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Pipeline process_analysis_job mis à jour pour inclure: 1) Crawl 2) Query Generation 3) Visibility Testing 4) Competitive Intelligence 5) Schema Generation 6) Claude Analysis 7) Word Report 8) HTML Dashboard 9) History/Alerts. TOUT LE PIPELINE DOIT ÊTRE TESTÉ."

frontend:
  - task: "Report Page Display - Competitive Intelligence Section"
    implemented: false
    working: "NA"
    file: "/app/frontend/src/pages/ReportPage.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: "NA"
          agent: "main"
          comment: "ReportPage n'affiche pas encore les données de competitive intelligence. Il faut ajouter un nouvel onglet/section pour afficher le tableau comparatif et les insights actionnables."
  
  - task: "Report Page Display - Schema JSON-LD Section"
    implemented: false
    working: "NA"
    file: "/app/frontend/src/pages/ReportPage.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: "NA"
          agent: "main"
          comment: "ReportPage n'affiche pas encore les schemas générés ni le guide d'implémentation. Il faut ajouter un nouvel onglet pour afficher les schemas et le guide."

metadata:
  created_by: "main_agent"
  version: "2.0"
  test_sequence: 0
  run_ui: false

test_plan:
  current_focus:
    - "Core Analysis Pipeline Integration"
    - "Module 3: Competitive Intelligence"
    - "Module 4: Schema JSON-LD Generator"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
    - agent: "main"
      message: |
        INTÉGRATION DES MODULES 3 & 4 TERMINÉE
        
        Travail effectué:
        1. ✅ Créé schema_generator.py avec 9 types de schemas JSON-LD
        2. ✅ Intégré competitive_intelligence.py dans le pipeline
        3. ✅ Intégré schema_generator.py dans le pipeline
        4. ✅ Ajouté extraction des compétiteurs depuis les résultats de visibilité
        5. ✅ Mis à jour progress tracking (70% → 80%)
        6. ✅ Ajouté competitive_intelligence et schemas aux report_dict
        
        État actuel:
        - Le pipeline backend est complet et prêt à être testé
        - Les modules 1, 3, 4 sont intégrés
        - Le module 2 (content generation) existe mais n'est pas intégré
        - Le module 5 (query expansion) est partiellement implémenté
        
        Prochaines étapes:
        1. TESTER le backend complet avec deep_testing_backend_v2
        2. Mettre à jour le frontend pour afficher competitive intelligence et schemas
        3. Implémenter module 5 (query expansion) complètement
        4. Intégrer module 2 (content generation) dans le pipeline si nécessaire