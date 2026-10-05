#!/bin/bash
# Vérifier les dernières mises à jour des modèles IA

echo "🔄 CreaZik Model Update Checker"
echo "================================"
echo ""

# Vérifier ACE-Step
echo "📦 ACE-Step 1.5"
if [ -d "/d/ACE-Step 1.5" ] || [ -d "D:/ACE-Step 1.5" ]; then
    echo "  ✓ Installation détectée"
    # Vérifier version
    # find . -name "version.txt" 2>/dev/null | head -1
else
    echo "  ✗ Installation non trouvée"
fi

# Vérifier modèles HuggingFace
echo ""
echo "🤗 HuggingFace Models"
python -c "
import json
try:
    with open('models_registry.json', 'r') as f:
        data = json.load(f)
        print(f\"  Last updated: {data.get('last_updated', 'Never')}\")
        print(f\"  Models: {len(data.get('models', []))} available\")
except:
    print('  ✗ Registry not initialized')
"

echo ""
echo "💡 Tip: Run 'python model_updater.py update' to refresh"
