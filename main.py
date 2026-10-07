from datetime import datetime
import flet as ft
import database

def main(page: ft.Page):
    page.title = "Colegio Dante Alighieri"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = "#F8F9FA"
    page.window_width = 400
    page.window_height = 750

    page.datos_alumno = None

    def mostrar_alerta(titulo, mensaje):
        def cerrar_dialogo(e):
            dialogo.open = False
            page.update()

        dialogo = ft.AlertDialog(
            title=ft.Text(titulo, weight=ft.FontWeight.BOLD),
            content=ft.Text(mensaje),
            actions=[ft.TextButton("OK", on_click=cerrar_dialogo)]
        )
        page.dialog = dialogo
        dialogo.open = True
        page.update()

    # --- PANTALLA LOGIN ---
    user_input = ft.TextField(label="Usuario (Código)", border=ft.InputBorder.OUTLINE, width=300)
    password_input = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, border=ft.InputBorder.OUTLINE, width=300)

    def verificar_login(e):
        user = user_input.value.strip()
        password = password_input.value.strip()
        
        if not user or not password:
            mostrar_alerta("Campos Incompletos", "Por favor, llene los dos campos.")
            return

        row_login = database.ejecutar_login(user)

        if row_login:
            ndoc_apo_db = str(row_login.get("NDocApo") or row_login.get("ndocapo") or "").strip()
            nombre_apoderado = row_login.get("Apoderado") or row_login.get("apoderado") or "Apoderado Registrado"
            nombre_estudiante = row_login.get("estudiante") or row_login.get("Estudiante") or "Estudiante"
            id_alumno = row_login.get("Id_alumno") or row_login.get("id_alumno") or row_login.get("Id_Alumno")
            
            if password == ndoc_apo_db:
                page.datos_alumno = {
                    "codigo": user,
                    "nombre_completo": nombre_estudiante,
                    "nro_doc": password,
                    "id_alumno": id_alumno,
                    "apoderado": nombre_apoderado,
                    "grado": "-",
                    "seccion": "-",
                    "turno": "-"
                }
                
               # --- CAPTURAR TOKEN REAL DE FIREBASE (FCM) ---
                try:
                    # En Flet para Android, el token se obtiene a través de los eventos de la página 
                    # o propiedades nativas inyectadas por el contenedor de notificaciones.
                    token_dispositivo = getattr(page, "fcm_token", None)
                    
                    # Si el token no está disponible inmediatamente en el evento de inicio, 
                    # dejamos una variable de escucha o validamos que la sesión capture el canal nativo.
                    if not token_dispositivo:
                        # Intentamos recuperar el token desde el cliente si soporta el canal nativo
                        token_dispositivo = page.client_storage.get("fcm_token")

                    if id_alumno and token_dispositivo and token_dispositivo not in ["FCM_PENDIENTE_NATIVO", "TOKEN_FCM_DEL_DISPOSITIVO_MOVIL"]:
                        database.registrar_token_fcm(id_alumno, token_dispositivo)
                        print(f"Token FCM real registrado exitosamente para el alumno {id_alumno}")
                    else:
                        # Registro de respaldo temporal si la API nativa de Google requiere un ciclo de espera
                        database.registrar_token_fcm(id_alumno, "FCM_PENDIENTE_NATIVO")
                except Exception as ex:
                    print(f"Error al intentar registrar el token push real: {ex}")
                # ---------------------------------------------

                user_input.value = ""
                password_input.value = ""
                crear_pantalla_home()
            else:
                mostrar_alerta("Error de Acceso", "La contraseña (Documento del Apoderado) es incorrecta.")
        else:
            mostrar_alerta("Error de Acceso", "El código de alumno ingresado no existe.")
    # --- PANTALLA HOME ---
    def crear_pantalla_home():
        page.clean()
        datos = page.datos_alumno

        card_bienvenida = ft.Container(
            content=ft.Column([
                ft.Text(f"Apoderado: {datos['apoderado']}", weight=ft.FontWeight.BOLD, size=16, color="#007373"),
                ft.Text(f"Estudiante: {datos['nombre_completo']}", size=14, color="#666666")
            ]),
            bgcolor="#E2EFF8",
            padding=16,
            border_radius=12,
            width=330
        )

        def ir_a_info(e):
            id_alumno = datos.get("id_alumno")
            row_alumno = database.obtener_info_alumno(id_alumno) if id_alumno else None
            if row_alumno:
                datos["grado"] = row_alumno.get("grado") or row_alumno.get("Grado") or "-"
                datos["seccion"] = row_alumno.get("seccion") or row_alumno.get("Seccion") or "-"
                datos["turno"] = row_alumno.get("turno") or row_alumno.get("Turno") or "-"
                if row_alumno.get("apellidos_nombres") or row_alumno.get("Apellidos_Nombres"):
                    datos["nombre_completo"] = row_alumno.get("apellidos_nombres") or row_alumno.get("Apellidos_Nombres")
            crear_pantalla_estudiante()

        def ir_a_pagos(e):
            crear_pantalla_pagos()

        def ir_a_comunicados(e):
            crear_pantalla_comunicados()

        def logout(e):
            page.datos_alumno = None
            crear_pantalla_login()

        page.add(
            ft.Column([
                card_bienvenida,
                ft.Container(height=10),
                ft.Text("MENÚ PRINCIPAL", weight=ft.FontWeight.BOLD, color="#008080", size=16),
                ft.Container(height=10),
                ft.ElevatedButton("1. Información del Estudiante Matriculado", width=330, bgcolor="#00A6A6", color="#FFFFFF", on_click=ir_a_info),
                ft.ElevatedButton("2. Estado de Cuenta - PAGOS", width=330, bgcolor="#00A6A6", color="#FFFFFF", on_click=ir_a_pagos),
                ft.ElevatedButton("3. Comunicados Informativos", width=330, bgcolor="#00A6A6", color="#FFFFFF", on_click=ir_a_comunicados),
                ft.Container(height=20),
                ft.OutlinedButton("4. Salir del sistema", width=330, on_click=logout)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
        page.update()

    # --- PANTALLA INFORMACIÓN ESTUDIANTE ---
    def crear_pantalla_estudiante():
        page.clean()
        datos = page.datos_alumno

        def volver(e):
            crear_pantalla_home()

        page.add(
            ft.Column([
                ft.Text("INFORMACIÓN DEL ESTUDIANTE", weight=ft.FontWeight.BOLD, size=18, color="#007373"),
                ft.Container(
                    content=ft.Column([
                        ft.Text("CÓDIGO INTERNO", size=11, color="#666666"),
                        ft.Text(str(datos["codigo"]), weight=ft.FontWeight.BOLD, size=15),
                        ft.Divider(),
                        ft.Text("APELLIDOS Y NOMBRES", size=11, color="#666666"),
                        ft.Text(str(datos["nombre_completo"]), weight=ft.FontWeight.BOLD, size=14),
                        ft.Divider(),
                        ft.Text("NRO. DOCUMENTO", size=11, color="#666666"),
                        ft.Text(str(datos["nro_doc"]), size=14),
                        ft.Divider(),
                        ft.Row([
                            ft.Column([ft.Text("GRADO", size=11, color="#666666"), ft.Text(str(datos["grado"]), weight=ft.FontWeight.BOLD)]),
                            ft.Column([ft.Text("SECCIÓN", size=11, color="#666666"), ft.Text(str(datos["seccion"]), weight=ft.FontWeight.BOLD)])
                        ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                        ft.Divider(),
                        ft.Row([
                            ft.Column([ft.Text("TURNO", size=11, color="#666666"), ft.Text(str(datos["turno"]), weight=ft.FontWeight.BOLD)]),
                            ft.Column([ft.Text("AÑO ESCOLAR", size=11, color="#666666"), ft.Text(str(datetime.now().year), weight=ft.FontWeight.BOLD)])
                        ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                    ]),
                    bgcolor="#E2EFF8", padding=16, border_radius=12, width=330
                ),
                ft.Container(height=15),
                ft.ElevatedButton("VOLVER AL MENÚ", width=330, bgcolor="#00A6A6", color="#FFFFFF", on_click=volver)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
        page.update()

    # --- PANTALLA PAGOS ---
    def crear_pantalla_pagos():
        page.clean()
        id_alumno = page.datos_alumno.get("id_alumno")
        pendientes = database.obtener_cuotas_pendientes(id_alumno) if id_alumno else []
        realizados = database.obtener_cuotas_pagadas(id_alumno) if id_alumno else []

        lista_pen = ft.ListView(expand=1, spacing=10, padding=10, width=330)
        if not pendientes:
            lista_pen.controls.append(ft.Text("No cuenta con deudas pendientes.", color="#666666", text_align=ft.TextAlign.CENTER))
        else:
            for item in pendientes:
                fecha_emision = item.get("Fch_Emi") or item.get("fch_emi") or "-"
                comp = item.get("Comprobante") or item.get("comprobante") or "-"
                concepto = item.get("Conceptos") or item.get("conceptos") or "Cuota"
                total = item.get("Total") or item.get("total") or "0.00"
                lista_pen.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(f"Fch.Emision: {fecha_emision}", weight=ft.FontWeight.BOLD, color="#B30000"),
                            ft.Text(f"Doc: {comp}", weight=ft.FontWeight.BOLD, color="#B30000"),
                            ft.Text(concepto, size=13),
                            ft.Text(f"Total: S/. {total}", weight=ft.FontWeight.BOLD, color="#B30000")
                        ]), bgcolor="#FFE6E6", padding=10, border_radius=8
                    )
                )

        lista_pag = ft.ListView(expand=1, spacing=10, padding=10, width=330)
        if not realizados:
            lista_pag.controls.append(ft.Text("No se registran pagos efectuados.", color="#666666", text_align=ft.TextAlign.CENTER))
        else:
            for item in realizados:
                fecha_pago = item.get("Fch_Pago") or item.get("fch_pago") or "-"
                comp = item.get("Comprobante") or item.get("comprobante") or "-"
                concepto = item.get("Conceptos") or item.get("conceptos") or "Pagado"
                total = item.get("Total") or item.get("total") or "0.00"
                modo_pago = item.get("Modo") or item.get("modo") or "Modalidad"
                lista_pag.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(f"Comprobante: {comp}", weight=ft.FontWeight.BOLD, color="#006600"),
                            ft.Text(f"Fecha Cancelación: {fecha_pago}", weight=ft.FontWeight.BOLD, color="#B30000"),
                            ft.Text(concepto, size=13),
                            ft.Text(f"Total Pagado: S/. {total}", weight=ft.FontWeight.BOLD, color="#006600"),
                            ft.Text(modo_pago, size=13),
                        ]), bgcolor="#E6FFE6", padding=10, border_radius=8
                    )
                )

        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="Pendientes", content=lista_pen),
                ft.Tab(text="Historial Pagos", content=lista_pag),
            ], expand=1
        )

        def volver(e):
            crear_pantalla_home()

        page.add(
            ft.Column([
                ft.Text("ESTADO DE CUENTA - PAGOS", weight=ft.FontWeight.BOLD, size=16, color="#007373"),
                ft.Container(content=tabs, height=450, width=340),
                ft.ElevatedButton("VOLVER AL MENÚ", width=330, bgcolor="#00A6A6", color="#FFFFFF", on_click=volver)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
        page.update()

    # --- PANTALLA COMUNICADOS ---
    def crear_pantalla_comunicados():
        page.clean()
        id_alumno = page.datos_alumno.get("id_alumno")
        no_leidos = database.obtener_comunicados_no_leidos(id_alumno) if id_alumno else []
        leidos = database.obtener_comunicados_leidos(id_alumno) if id_alumno else []

        lista_no_leidos = ft.ListView(expand=1, spacing=10, padding=10, width=330)
    
        def abrir_detalle(asunto, detalle, id_comunicado):
            def cerrar_y_actualizar(e):
                if id_comunicado:
                    database.actualizar_estado_comunicado(id_comunicado)
                dlg.open = False
                page.update()
                crear_pantalla_comunicados()

            dlg = ft.AlertDialog(
                title=ft.Text(asunto, weight=ft.FontWeight.BOLD),
                content=ft.Text(detalle),
                actions=[ft.TextButton("CERRAR", on_click=cerrar_y_actualizar)]
            )
            page.dialog = dlg
            dlg.open = True
            page.update()

        if not no_leidos:
            lista_no_leidos.controls.append(ft.Text("No tienes comunicados pendientes.", color="#666666", text_align=ft.TextAlign.CENTER))
        else:
            for item in no_leidos:
                asunto = item.get("Asunto") or item.get("asunto") or "Sin Asunto"
                detalle = item.get("Detalle") or item.get("detalle") or "Sin contenido."
                fecha_emision = item.get("Fecha") or item.get("fecha") or "Fecha no disponible"
                remitente = item.get("Remitente") or item.get("remitente") or "Remitente no especificado"
                id_c = item.get("id_comunica") or item.get("Id_Comunica") or item.get("id_comunicado")
                lista_no_leidos.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(f"📅 Emitido: {fecha_emision}", size=11, color="#555555"),
                            ft.Text(f"👤 Remitente: {remitente}", size=12, italic=True, color="#444444"),
                            ft.Text(asunto, weight=ft.FontWeight.BOLD, size=13),
                            ft.TextButton("VER DETALLE", on_click=lambda e, a=asunto, d=detalle, ic=id_c: abrir_detalle(a, d, ic))
                        ], spacing=3), 
                        bgcolor="#EFEFFF", padding=10, border_radius=8
                    )
                )

        lista_leidos = ft.ListView(expand=1, spacing=10, padding=10, width=330)
        if not leidos:
            lista_leidos.controls.append(ft.Text("No hay comunicados archivados.", color="#666666", text_align=ft.TextAlign.CENTER))
        else:
            for item in leidos:
                asunto = item.get("Asunto") or item.get("asunto") or "Sin Asunto"
                detalle = item.get("Detalle") or item.get("detalle") or "Sin contenido."
                fecha_emision = item.get("Fecha") or item.get("fecha") or "Fecha no disponible"
                remitente = item.get("Remitente") or item.get("remitente") or "Remitente no especificado"
                fecha_lectura = item.get("Leido") or item.get("leido") or "No registrada"
                hora_lectura = item.get("Hora") or item.get("hora") or ""
                texto_lectura = f"{fecha_lectura} {hora_lectura}".strip() or "No registrada"
                
                lista_leidos.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(f"📅 Emitido: {fecha_emision}", size=11, color="#555555"),
                            ft.Text(f"👤 Remitente: {remitente}", size=12, italic=True, color="#444444"),
                            ft.Text(asunto, weight=ft.FontWeight.BOLD, size=13),
                            ft.Text(f"👁️ Leído el: {fecha_lectura} a Horas: {hora_lectura}", size=11, color="#007373"),
                            ft.TextButton("VER DETALLE", on_click=lambda e, a=asunto, d=detalle, ic=None: abrir_detalle(a, d, ic))
                        ], spacing=3), 
                        bgcolor="#F0F0F0", padding=10, border_radius=8
                    )
                )

        tabs = ft.Tabs(
                selected_index=0,
                animation_duration=300,
                tabs=[
                    ft.Tab(text="No Leídos", content=lista_no_leidos),
                    ft.Tab(text="Historial / Leídos", content=lista_leidos),
                ], expand=1
        )

        def volver(e):
            crear_pantalla_home()

        page.add(
            ft.Column([
                ft.Text("COMUNICADOS INFORMATIVOS", weight=ft.FontWeight.BOLD, size=16, color="#007373"),
                ft.Container(content=tabs, height=450, width=340),
                ft.ElevatedButton("VOLVER AL MENÚ", width=330, bgcolor="#00A6A6", color="#FFFFFF", on_click=volver)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
        page.update()

    # --- INICIALIZACIÓN LOGIN ---
    def crear_pantalla_login():
        page.clean()
        page.add(
            ft.Column([
                ft.Image(src="escudodante.png", width=120, height=120, fit=ft.ImageFit.CONTAIN),
                ft.Container(height=10),
                ft.Text("COLEGIO DANTE ALIGHIERI", weight=ft.FontWeight.BOLD, size=20, color="#007373", text_align=ft.TextAlign.CENTER),
                ft.Text("Aplicativo Institucional", size=14, color="#6699CC", text_align=ft.TextAlign.CENTER),
                ft.Container(height=20),
                user_input,
                password_input,
                ft.Container(height=15),
                ft.ElevatedButton("INGRESAR", width=300, bgcolor="#00A6A6", color="#FFFFFF", on_click=verificar_login)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER)
        )
        page.update()

    crear_pantalla_login()

ft.app(target=main)
