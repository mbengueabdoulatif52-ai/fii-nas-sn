#!/bin/sh
# Lance tous les tests de l'appli (Playwright + Chrome). Usage : sh tests/run.sh
cd "$(dirname "$0")" && mkdir -p out
ok=0; ko=0
for f in t*.py; do
  if timeout 150 python3 -u "$f" > "out/$f.log" 2>&1 && ! grep -q "Traceback" "out/$f.log" && ! grep -qE "errors \[.+\]|^\[.+\]$" "out/$f.log"; then ok=$((ok+1)); else ko=$((ko+1)); echo "ÉCHEC : $f (voir tests/out/$f.log)"; fi
done
for f in srv*.mjs; do node "$f" > "out/$f.log" 2>&1 && ok=$((ok+1)) || { ko=$((ko+1)); echo "ÉCHEC : $f"; }; done
echo "$ok réussis, $ko échoués"
