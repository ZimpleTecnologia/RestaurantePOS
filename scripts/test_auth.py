#!/usr/bin/env python3
"""
Script para probar autenticación paso a paso
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.auth.security import verify_password, get_password_hash
from app.routers.auth import login
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends

def test_user_in_db():
    """Verificar usuario en base de datos"""
    print("🔍 Verificando usuario en base de datos...")
    
    db = next(get_db())
    
    try:
        user = db.query(User).filter(User.username == "admin").first()
        
        if not user:
            print("❌ Usuario 'admin' no encontrado")
            return None
        
        print(f"✅ Usuario encontrado:")
        print(f"   ID: {user.id}")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Role: {user.role}")
        print(f"   Is Active: {user.is_active}")
        print(f"   Is Verified: {user.is_verified}")
        print(f"   Hash: {user.hashed_password}")
        
        return user
        
    except Exception as e:
        print(f"❌ Error al buscar usuario: {e}")
        return None
    finally:
        db.close()

def test_password_verification(user):
    """Probar verificación de contraseña"""
    print("\n🔐 Probando verificación de contraseña...")
    
    test_passwords = ["admin123", "admin", "password", "123456"]
    
    for password in test_passwords:
        is_valid = verify_password(password, user.hashed_password)
        print(f"   Contraseña '{password}': {'✅ Válida' if is_valid else '❌ Inválida'}")
        
        if is_valid:
            print(f"   🎉 ¡Contraseña correcta encontrada: '{password}'!")
            return password
    
    print("   ❌ Ninguna contraseña funcionó")
    return None

def test_new_hash():
    """Probar generación de nuevo hash"""
    print("\n🔄 Probando generación de hash...")
    
    password = "admin123"
    new_hash = get_password_hash(password)
    
    print(f"   Contraseña: {password}")
    print(f"   Nuevo hash: {new_hash}")
    
    # Verificar que el nuevo hash funciona
    is_valid = verify_password(password, new_hash)
    print(f"   Verificación del nuevo hash: {'✅ Válida' if is_valid else '❌ Inválida'}")
    
    return new_hash

def test_login_function():
    """Probar función de login directamente"""
    print("\n🚀 Probando función de login...")
    
    try:
        # Crear un objeto form_data simulado
        class MockFormData:
            def __init__(self):
                self.username = "admin"
                self.password = "admin123"
        
        form_data = MockFormData()
        
        # Obtener sesión de BD
        db = next(get_db())
        
        # Buscar usuario
        user = db.query(User).filter(User.username == form_data.username).first()
        
        if not user:
            print("   ❌ Usuario no encontrado")
            return
        
        print(f"   ✅ Usuario encontrado: {user.username}")
        
        # Verificar contraseña
        if not verify_password(form_data.password, user.hashed_password):
            print("   ❌ Contraseña incorrecta")
            return
        
        print("   ✅ Contraseña válida")
        
        # Verificar si está activo
        if not user.is_active:
            print("   ❌ Usuario inactivo")
            return
        
        print("   ✅ Usuario activo")
        print("   🎉 Login exitoso!")
        
    except Exception as e:
        print(f"   ❌ Error en login: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Iniciando diagnóstico de autenticación...")
    
    # 1. Verificar usuario en BD
    user = test_user_in_db()
    
    if user:
        # 2. Probar verificación de contraseña
        correct_password = test_password_verification(user)
        
        # 3. Probar generación de hash
        new_hash = test_new_hash()
        
        # 4. Probar función de login
        test_login_function()
        
        if correct_password:
            print(f"\n📋 Resumen:")
            print(f"   Usuario: admin")
            print(f"   Contraseña correcta: {correct_password}")
            print(f"   Hash actual: {user.hashed_password}")
            print(f"   Nuevo hash: {new_hash}")
        else:
            print(f"\n❌ Problema: La contraseña en la BD no coincide con 'admin123'")
            print(f"   Solución: Actualizar la contraseña en la BD")
    else:
        print("❌ No se pudo encontrar el usuario en la BD")
