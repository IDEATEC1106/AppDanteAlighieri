import requests

API_URL = "http://38.224.68.171:5000/api"

def ejecutar_login(user):
    try:
        response = requests.post(f"{API_URL}/login", json={"user": user}, timeout=10)
        return response.json() if response.status_code == 200 else None
    except Exception as ex:
        print(f"Error de conexión en login: {ex}")
        return None

def obtener_info_alumno(id_alumno):
    try:
        response = requests.get(f"{API_URL}/alumno", params={"id": id_alumno}, timeout=10)
        return response.json() if response.status_code == 200 else None
    except Exception as ex:
        print(f"Error: {ex}")
        return None

def obtener_cuotas_pendientes(id_alumno):
    try:
        response = requests.get(f"{API_URL}/cuotas_pendientes", params={"id": id_alumno}, timeout=10)
        return response.json() if response.status_code == 200 else []
    except Exception as ex:
        print(f"Error: {ex}")
        return []

def obtener_cuotas_pagadas(id_alumno):
    try:
        response = requests.get(f"{API_URL}/cuotas_pagadas", params={"id": id_alumno}, timeout=10)
        return response.json() if response.status_code == 200 else []
    except Exception as ex:
        print(f"Error: {ex}")
        return []

def obtener_comunicados_no_leidos(id_alumno):
    try:
        response = requests.get(f"{API_URL}/comunicados_no_leidos", params={"id": id_alumno}, timeout=10)
        return response.json() if response.status_code == 200 else []
    except Exception as ex:
        print(f"Error: {ex}")
        return []

def obtener_comunicados_leidos(id_alumno):
    try:
        response = requests.get(f"{API_URL}/comunicados_leidos", params={"id": id_alumno}, timeout=10)
        return response.json() if response.status_code == 200 else []
    except Exception as ex:
        print(f"Error: {ex}")
        return []

def actualizar_estado_comunicado(id_comunica):
    try:
        response = requests.post(f"{API_URL}/actualizar_comunicado", json={"id": id_comunica}, timeout=10)
        return response.status_code == 200
    except Exception as ex:
        print(f"Error: {ex}")
        return False

def registrar_token_fcm(id_alumno, token_fcm):
    try:
        # Asegurarse de usar la conexión activa
        cursor = conexion.cursor()
        sql = "UPDATE ALUMNO SET APO_FCM_TOKEN = %s WHERE Id_Alumno = %s"
        cursor.execute(sql, (token_fcm, id_alumno))
        conexion.commit() # ¡IMPORTANTE! Si no haces commit, los cambios no se guardan en la BD
        print(f"OK: Token guardado en APO_FCM_TOKEN para el Id_Alumno: {id_alumno}")
    except Exception as e:
        print(f"Error SQL al actualizar APO_FCM_TOKEN: {e}")
