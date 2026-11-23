# Voile flou : apparaît quand l'appli perd la main, disparaît au retour
import os,sys,subprocess,time;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from stub import page
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8771'],cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
try:
  with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg,errs=page(b)
    vis=lambda:pg.evaluate("!!document.getElementById('voile')&&document.getElementById('voile').classList.contains('on')")
    print('au départ:',not vis())
    pg.evaluate("window.dispatchEvent(new Event('blur'))");print('perd la main:',vis())
    pg.evaluate("window.dispatchEvent(new Event('focus'))");pg.wait_for_timeout(250);print('revient:',not vis())
    pg.evaluate("Object.defineProperty(document,'visibilityState',{value:'hidden',configurable:true});document.dispatchEvent(new Event('visibilitychange'))");print('arrière-plan:',vis())
    pg.evaluate("Object.defineProperty(document,'visibilityState',{value:'visible',configurable:true});document.dispatchEvent(new Event('visibilitychange'))");pg.wait_for_timeout(250);print('premier plan:',not vis())
    pg.evaluate("window.dispatchEvent(new Event('blur'))");pg.mouse.click(200,400);pg.wait_for_timeout(100);print('toucher enlève:',not vis())
    print('errors',errs)
finally: srv.terminate()
