from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from web_ujap.models import Usuario, Estudiante, Materia, Seccion, Horario, SesionClase, Asistencia


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def crear_profesor(username='profe_test'):
    return Usuario.objects.create_user(
        username=username,
        password='testpass123',
        rol=Usuario.ROL_PROFESOR,
    )

def crear_estudiante_completo(cedula='12345678', username='est_test', sec_codigo='SEC01'):
    """
    Crea sección, materia, horario, usuario estudiante y perfil vinculado.
    sec_codigo permite crear varias secciones distintas en el mismo test.
    """
    # get_or_create evita el error de clave duplicada si la sección ya existe
    seccion, _ = Seccion.objects.get_or_create(
        codigo=sec_codigo,
        defaults={'periodo': '20261CR', 'carrera': 'Ingeniería en Computación'}
    )
    materia, _ = Materia.objects.get_or_create(
        codigo='PRO001',
        defaults={'nombre': 'Programación I'}
    )
    profesor = crear_profesor(f'profe_aux_{username}')
    horario, _ = Horario.objects.get_or_create(
        seccion=seccion,
        materia=materia,
        dia_semana='lunes',
        defaults={
            'hora_inicio': '08:00',
            'hora_fin':    '10:00',
            'aula':        '401',
            'profesor':    profesor,
        }
    )
    usuario = Usuario.objects.create_user(
        username=username,
        password='testpass123',
        rol=Usuario.ROL_ESTUDIANTE,
    )
    perfil = Estudiante.objects.create(
        usuario=usuario,
        seccion=seccion,
        nombre='Juan',
        apellido='Pérez',
        cedula=cedula,
        correo=f'{cedula}@test.com',
    )
    return perfil, horario, seccion, materia


# ─────────────────────────────────────────────────────────────────────────────
# TEST 1 — Generación del QR y creación de SesionClase
# ─────────────────────────────────────────────────────────────────────────────

class SesionClaseTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.profesor = crear_profesor()
        _, self.horario, _, _ = crear_estudiante_completo()
        self.horario.profesor = self.profesor
        self.horario.save()

    def test_sesion_se_crea_con_token_unico(self):
        """Cada sesión debe tener un token UUID diferente."""
        sesion1 = SesionClase.objects.create(
            horario=self.horario,
            fecha=timezone.now().date(),
            duracion_minutos=15,
            creada_por=self.profesor,
        )
        sesion2 = SesionClase.objects.create(
            horario=self.horario,
            fecha=timezone.now().date(),
            duracion_minutos=15,
            creada_por=self.profesor,
        )
        self.assertNotEqual(sesion1.token, sesion2.token)

    def test_sesion_vigente_recien_creada(self):
        """Una sesión recién creada debe estar vigente."""
        sesion = SesionClase.objects.create(
            horario=self.horario,
            fecha=timezone.now().date(),
            duracion_minutos=15,
            creada_por=self.profesor,
        )
        self.assertTrue(sesion.esta_vigente)

    def test_sesion_inactiva_no_esta_vigente(self):
        """Una sesión marcada como inactiva no debe estar vigente."""
        sesion = SesionClase.objects.create(
            horario=self.horario,
            fecha=timezone.now().date(),
            duracion_minutos=15,
            creada_por=self.profesor,
            activa=False,
        )
        self.assertFalse(sesion.esta_vigente)

    def test_solo_profesor_puede_iniciar_sesion(self):
        """Un estudiante no puede acceder a la vista de iniciar sesión."""
        perfil, _, _, _ = crear_estudiante_completo(
            cedula='99999999', username='est2', sec_codigo='SEC02'
        )
        self.client.login(username='est2', password='testpass123')
        response = self.client.get(reverse('dashboard:iniciar_sesion'))
        self.assertEqual(response.status_code, 403)

    def test_profesor_puede_iniciar_sesion(self):
        """Un profesor autenticado puede acceder a iniciar sesión."""
        self.client.login(username='profe_test', password='testpass123')
        response = self.client.get(reverse('dashboard:iniciar_sesion'))
        self.assertEqual(response.status_code, 200)


# ─────────────────────────────────────────────────────────────────────────────
# TEST 2 — Registro de asistencia por QR
# ─────────────────────────────────────────────────────────────────────────────

class RegistroAsistenciaQRTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.profesor = crear_profesor()
        self.perfil, self.horario, self.seccion, self.materia = crear_estudiante_completo()
        self.horario.profesor = self.profesor
        self.horario.save()

        self.sesion = SesionClase.objects.create(
            horario=self.horario,
            fecha=timezone.now().date(),
            duracion_minutos=15,
            creada_por=self.profesor,
        )

    def test_estudiante_puede_registrar_asistencia_qr(self):
        """Un estudiante que escanea un QR válido queda como presente."""
        self.client.login(username='est_test', password='testpass123')
        url = reverse('escanear_qr', kwargs={'token': self.sesion.token})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Asistencia.objects.filter(
                estudiante=self.perfil,
                materia=self.materia,
                fecha=self.sesion.fecha,
                estado='presente',
                metodo='qr',
            ).exists()
        )

    def test_no_se_registra_doble_asistencia(self):
        """El mismo estudiante no puede registrar asistencia dos veces el mismo día."""
        self.client.login(username='est_test', password='testpass123')
        url = reverse('escanear_qr', kwargs={'token': self.sesion.token})

        self.client.get(url)  # primer escaneo
        self.client.get(url)  # segundo escaneo — debe ser ignorado

        total = Asistencia.objects.filter(
            estudiante=self.perfil,
            materia=self.materia,
            fecha=self.sesion.fecha,
        ).count()
        self.assertEqual(total, 1)  # exactamente 1, nunca 2

    def test_qr_expirado_no_registra(self):
        """Un QR de sesión inactiva no debe registrar asistencia."""
        self.sesion.activa = False
        self.sesion.save()

        self.client.login(username='est_test', password='testpass123')
        url = reverse('escanear_qr', kwargs={'token': self.sesion.token})
        self.client.get(url)

        existe = Asistencia.objects.filter(
            estudiante=self.perfil,
            materia=self.materia,
            fecha=self.sesion.fecha,
        ).exists()
        self.assertFalse(existe)

    def test_profesor_no_puede_escanear_qr(self):
        """Un profesor no puede registrar asistencia por QR."""
        self.client.login(username='profe_test', password='testpass123')
        url = reverse('escanear_qr', kwargs={'token': self.sesion.token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)