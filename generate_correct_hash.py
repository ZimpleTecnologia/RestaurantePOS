#!/usr/bin/env python3
"""
Script para generar el hash correcto de bcrypt para la contraseña '123456'
Uso: python generate_correct_hash.py
"""

from passlib.context import CryptContext

# Configurar contexto de encriptación
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_hash():
    """Generar hash para contraseña '123456'"""
    password = "123456"
    hashed = pwd_context.hash(password)
    
    print("🔐 Generando hash para contraseña '123456'")
    print("=" * 50)
    print(f"Contraseña: {password}")
    print(f"Hash bcrypt: {hashed}")
    print("=" * 50)
    
    # Verificar que el hash funciona
    if pwd_context.verify(password, hashed):
        print("✅ Hash verificado correctamente")
        return hashed
    else:
        print("❌ Error en la verificación del hash")
        return None

def main():
    """Función principal"""
    hash_result = generate_hash()
    
    if hash_result:
        print("\n📋 Query SQL para actualizar la base de datos:")
        print("-" * 50)
        print(f"UPDATE users SET hashed_password = '{hash_result}' WHERE username = 'admin';")
        print("-" * 50)
        print("\n🎯 Ejecuta esta query en tu base de datos de EasyPanel")

if __name__ == "__main__":
    main()

