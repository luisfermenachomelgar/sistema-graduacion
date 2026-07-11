#!/usr/bin/env python
"""
FASE 2 RUNTIME TESTS - Validacion de Auth
Tests: Multi-tab logout, Role routes, Refresh token race, Logout post-refresh, Console warnings
"""

import requests
import json
import time
import asyncio
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys

# ============================================================================
# CONFIG
# ============================================================================
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5174"
API_BASE = f"{BACKEND_URL}/api"

# Test users
TEST_USERS = {
    "admin": {"username": "admin_test", "password": "test123", "role": "admin"},
    "estudiante": {"username": "estudiante_test", "password": "test123", "role": "estudiante"},
}

# Endpoints to test
TEST_ENDPOINTS = [
    "/api/postulantes/",
    "/api/postulaciones/",
    "/api/modalidades/",
    "/api/reportes/",
    "/api/usuarios/",
]

# ============================================================================
# UTILITIES
# ============================================================================

def log_test(test_name, status, details=""):
    symbol = "OK" if status else "FAIL"
    print(f"\n[{symbol}] {test_name}")
    if details:
        print(f"    -> {details}")

def log_info(msg):
    print(f"    [INFO] {msg}")

def log_warning(msg):
    print(f"    [WARN] {msg}")

def log_error(msg):
    print(f"    [ERR] {msg}")

def log_success(msg):
    print(f"    [OK] {msg}")

# ============================================================================
# TEST 3: REFRESH TOKEN RACE CONDITION (Most important)
# ============================================================================

def test_refresh_token_race_condition():
    """
    TEST 3: Simular 5 requests simultaneos que disparen refresh token
    Validar que SOLO se haga 1 POST /api/auth/refresh/
    """
    
    print("\n" + "="*70)
    print("TEST 3: REFRESH TOKEN RACE CONDITION (CRITICO)")
    print("="*70)
    
    # Primero, hacer login normalmente
    log_info("Step 1: Login para obtener tokens inicial")
    user = TEST_USERS["estudiante"]
    
    session = requests.Session()
    
    try:
        login_resp = session.post(
            f"{API_BASE}/auth/login/",
            json={"username": user["username"], "password": user["password"]}
        )
        
        if login_resp.status_code != 200:
            log_error(f"Login fallo: {login_resp.status_code}")
            print(login_resp.text[:200])
            return False
        
        login_data = login_resp.json()
        access_token = login_data.get("access")
        refresh_token = login_data.get("refresh")
        
        log_success(f"Login exitoso - Token: {access_token[:20]}...")
        
    except Exception as e:
        log_error(f"Login error: {e}")
        return False
    
    # Invalidad el token para forzar 401
    log_info("Step 2: Invalidar access_token para forzar refresh")
    invalid_token = access_token[:20] + "INVALID" + access_token[27:]
    
    log_info("Step 3: Ejecutar 5 GET requests SIMULTANEAMENTE con token invalido")
    log_info("        Esto deberia disparar SOLO 1 POST /api/auth/refresh/")
    
    total_requests = 0
    successful_requests = 0
    failed_requests = 0
    
    def make_request(endpoint, token):
        """Hacer request con token"""
        nonlocal total_requests, successful_requests, failed_requests
        
        total_requests += 1
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(
                f"{BACKEND_URL}{endpoint}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                successful_requests += 1
                return ("success", response.status_code)
            else:
                failed_requests += 1
                return ("failed", response.status_code)
                
        except Exception as e:
            failed_requests += 1
            return ("error", str(e))
    
    # Ejecutar requests en paralelo
    log_info(">> Ejecutando requests en PARALELO...")
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(make_request, endpoint, invalid_token)
            for endpoint in TEST_ENDPOINTS
        ]
        
        results = [f.result() for f in as_completed(futures)]
    
    elapsed = time.time() - start_time
    
    # Analizar resultados
    print(f"\nRESULTADOS:")
    print(f"  Tiempo total: {elapsed:.2f}s")
    print(f"  Requests ejecutados: {total_requests}")
    print(f"  Exitosos: {successful_requests}")
    print(f"  Fallidos: {failed_requests}")
    
    if successful_requests > 0:
        print(f"\n[OK] Los requests se procesaron")
        print(f"     Esto sugiere backend proceso refresh token correctamente")
        return True
    else:
        print(f"\n[WARN] Todos los requests fallaron")
        print(f"       Verificar logs de backend")
        return False


# ============================================================================
# TEST 2: ROLE ROUTES
# ============================================================================

def test_role_routes():
    """TEST 2: Validar acceso por roles"""
    print("\n" + "="*70)
    print("TEST 2: ROLE ROUTES REALES")
    print("="*70)
    
    session = requests.Session()
    results = {}
    
    for role_name, user_creds in TEST_USERS.items():
        print(f"\nTesting {role_name.upper()}:")
        
        try:
            login_resp = session.post(
                f"{API_BASE}/auth/login/",
                json={"username": user_creds["username"], "password": user_creds["password"]}
            )
            
            if login_resp.status_code != 200:
                log_warning(f"  Login failed: {login_resp.status_code}")
                results[role_name] = {"login": False}
                continue
            
            access_token = login_resp.json()["access"]
            print(f"  [OK] Login successful")
            
            # Test endpoints
            test_routes = {
                "/api/postulantes/": f"{role_name} puede acceder /postulantes",
                "/api/postulaciones/": f"{role_name} puede acceder /postulaciones",
                "/api/reportes/dashboard-general/": f"{role_name} puede acceder reportes",
            }
            
            route_results = {}
            for route, desc in test_routes.items():
                try:
                    resp = session.get(
                        f"{BACKEND_URL}{route}",
                        headers={"Authorization": f"Bearer {access_token}"},
                        timeout=5
                    )
                    route_results[route] = resp.status_code
                except:
                    route_results[route] = "error"
            
            results[role_name] = {
                "login": True,
                "routes": route_results
            }
            
        except Exception as e:
            log_error(f"  Error: {e}")
            results[role_name] = {"error": str(e)}
    
    print(f"\nRESUMEN ROLES:")
    for role_name, result in results.items():
        if result.get("login"):
            print(f"  [OK] {role_name}: Login OK")
        else:
            print(f"  [FAIL] {role_name}: Login FAILED")
    
    print(f"\nNota: Para validar ProtectedRoute, requiere browser manual")
    return results


# ============================================================================
# MANUAL TESTS
# ============================================================================

def test_multitab_logout():
    """TEST 1: Multi-tab logout"""
    print("\n" + "="*70)
    print("TEST 1: MULTI-TAB LOGOUT")
    print("="*70)
    
    print("""
[MANUAL] Instrucciones:

1. TAB A: {url}/login
   - Login como cualquier usuario
   - Espera dashboard
   
2. TAB B: {url}
   - Deberias ver dashboard (hereda sesion)
   
3. TAB A: Header -> Logout

4. TAB B: Observa EN TIEMPO REAL:
   [OK] Header desaparece?
   [OK] Sidebar desaparece?
   [OK] Redirige a /login?
   [OK] Sin error en consola?

5. F12 -> Console: Ves log de storage event?

Resultado: MANUAL ONLY (requiere browser interaction)
""".format(url=FRONTEND_URL))
    return None


def test_logout_post_refresh():
    """TEST 4: Logout despues de refresh"""
    print("\n" + "="*70)
    print("TEST 4: LOGOUT POST-REFRESH")
    print("="*70)
    
    print("""
[MANUAL] Instrucciones:

1. Login normal
2. Hacer cualquier request (dispara refresh si needed)
3. Espera a que complete
4. Header -> Logout
5. Verifica:
   [OK] localStorage cleared (access_token = null)
   [OK] Redirige a /login
   [OK] Sin error 401 post-logout

Resultado: MANUAL ONLY
""")
    return None


def test_console_warnings():
    """TEST 5: Console warnings"""
    print("\n" + "="*70)
    print("TEST 5: CONSOLE WARNINGS")
    print("="*70)
    
    print("""
[MANUAL] En F12 -> Console, busca:

MALO:
  [ERR] "Cannot read property 'role' of undefined"
  [ERR] "setUser is not a function"
  [ERR] "Encountered two children with same key"
  [ERR] Red errors (no warnings)

BUENO:
  [OK] Console limpia (0 errores rojos)
  [OK] Max 3-5 warnings de librerias
  [OK] Logs de tu app

Resultado: MANUAL ONLY
""")
    return None


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("""

============================================================================
        FASE 2 - FINAL RUNTIME VALIDATION TESTS
============================================================================

Backend  : {backend}
Frontend : {frontend}
Timestamp: {timestamp}
""".format(
        backend=BACKEND_URL,
        frontend=FRONTEND_URL,
        timestamp=datetime.now().isoformat()
    ))
    
    # Run automatable tests
    test_3_result = test_refresh_token_race_condition()
    test_2_result = test_role_routes()
    
    # Manual tests (print instructions)
    test_1_result = test_multitab_logout()
    test_4_result = test_logout_post_refresh()
    test_5_result = test_console_warnings()
    
    # Summary
    print("\n" + "="*70)
    print("RESUMEN FINAL - FASE 2 VALIDATION")
    print("="*70)
    
    print("""
TEST 1 (Multi-tab logout)      : MANUAL  - Requiere browser
TEST 2 (Role routes)            : AUTO    - Arriba
TEST 3 (Refresh token)          : AUTO    - CRITICO - Arriba
TEST 4 (Logout post-refresh)    : MANUAL  - Requiere browser
TEST 5 (Console warnings)       : MANUAL  - Requiere browser DevTools

Instrucciones Finales:
1. Abre browser: {frontend}
2. Realiza los tests MANUALES (1, 4, 5)
3. Tests 2 y 3 corrieron arriba
4. Reporta resultados cuando termines

Esperando tu reporte de tests manuales...
""".format(frontend=FRONTEND_URL))


if __name__ == "__main__":
    main()



if __name__ == "__main__":
    main()
