from backend.logica.user import registrar_contraseña, verificar_contraseña

registrar_contraseña("21300379", "123")

print(verificar_contraseña("21300379", "123"))  # Debería devolver True



