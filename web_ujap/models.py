from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
import uuid


# ===== MODELO LEGACY (NO TOCAR) =====
# ===== MODELO LEGACY (NO TOCAR) =====
class UsuarioUJAP(models.Model):
    """
    Modelo de la versión anterior del sistema.
    Mantenido como registro histórico — NO usar para autenticación.
    El campo password fue eliminado en migración 0002 (era texto plano).
    """
    cedula   = models.CharField(max_length=20, unique=True)
    correo   = models.EmailField(unique=True)
    facultad = models.CharField(max_length=100)
    # campo password eliminado — era CharField en texto plano

    def __str__(self):
        return self.cedula

# ===== USUARIO =====
class Usuario(AbstractUser):
    ROL_PROFESOR   = 'profesor'
    ROL_ESTUDIANTE = 'estudiante'
    ROLES = [
        (ROL_PROFESOR,   'Profesor'),
        (ROL_ESTUDIANTE, 'Estudiante'),
    ]

    cedula   = models.CharField(max_length=20, unique=True, blank=True, null=True)
    facultad = models.CharField(max_length=100, blank=True, null=True)
    rol      = models.CharField(max_length=15, choices=ROLES, default=ROL_ESTUDIANTE)

    @property
    def es_profesor(self):
        return self.rol == self.ROL_PROFESOR

    @property
    def es_estudiante(self):
        return self.rol == self.ROL_ESTUDIANTE

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"


# ===== MATERIA =====
class Materia(models.Model):
    """
    Ej: PROGRAMACION I / PRO02305
    Una misma materia puede aparecer en varias secciones.
    """
    nombre      = models.CharField(max_length=100)
    codigo      = models.CharField(max_length=20, unique=True)
    descripcion = models.TextField(blank=True)
    creditos    = models.IntegerField(default=3)
    activa      = models.BooleanField(default=True)

    class Meta:
        verbose_name        = "Materia"
        verbose_name_plural = "Materias"
        ordering            = ['nombre']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


# ===== SECCIÓN =====
class Seccion(models.Model):
    """
    Representa un grupo de estudiantes. Ej: 10212, 10213.
    Cada sección tiene su propio conjunto de horarios.
    """
    codigo   = models.CharField(max_length=20, unique=True)   # "10212"
    periodo  = models.CharField(max_length=20)                # "20261CR"
    carrera  = models.CharField(max_length=100)               # "Ingeniería en Computación"
    activa   = models.BooleanField(default=True)

    class Meta:
        verbose_name        = "Sección"
        verbose_name_plural = "Secciones"
        ordering            = ['codigo']

    def __str__(self):
        return f"Sección {self.codigo} — {self.carrera} ({self.periodo})"

    def get_materias(self):
        """Devuelve todas las materias únicas de esta sección."""
        return Materia.objects.filter(
            horarios__seccion=self
        ).distinct()


# ===== HORARIO =====
class Horario(models.Model):
    """
    Una franja horaria específica de una materia en una sección.
    Una materia puede tener VARIOS registros de horario por semana.
    Ej: FISICA I — Martes 7:45-8:30 aula 4405
        FISICA I — Jueves 8:40-10:10 aula 4404
    """
    DIAS_SEMANA = [
        ('lunes',     'Lunes'),
        ('martes',    'Martes'),
        ('miercoles', 'Miércoles'),
        ('jueves',    'Jueves'),
        ('viernes',   'Viernes'),
        ('sabado',    'Sábado'),
    ]

    seccion     = models.ForeignKey(
        Seccion,
        on_delete=models.CASCADE,
        related_name='horarios',
        null=True, blank=True    # null temporal para no romper migración
    )
    materia     = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='horarios')
    dia_semana  = models.CharField(max_length=10, choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fin    = models.TimeField()
    aula        = models.CharField(max_length=50)
    profesor    = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='horarios',
        limit_choices_to={'rol': 'profesor'}
    )

    class Meta:
        verbose_name        = "Horario"
        verbose_name_plural = "Horarios"
        ordering            = ['dia_semana', 'hora_inicio']

    def __str__(self):
        seccion_str = f" [{self.seccion.codigo}]" if self.seccion else ""
        return (
            f"{self.materia.nombre}{seccion_str} — "
            f"{self.get_dia_semana_display()} "
            f"{self.hora_inicio.strftime('%H:%M')}-{self.hora_fin.strftime('%H:%M')} "
            f"(Aula {self.aula})"
        )


# ===== ESTUDIANTE =====
class Estudiante(models.Model):
    """
    Perfil extendido de un usuario estudiante.
    Se vincula a un Usuario al momento del registro.
 
    La sección indica el grupo base del estudiante, pero sus horarios
    reales se asignan individualmente mediante `horarios_personales`,
    lo que permite cursar materias de distintas secciones.
    """
    usuario       = models.OneToOneField(
        Usuario,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='perfil_estudiante'
    )
    seccion       = models.ForeignKey(
        Seccion,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='estudiantes'
    )
    # ── NUEVO ────────────────────────────────────────────────────────────────
    # Horarios individuales del estudiante.
    # Permite asignar franjas de distintas secciones (ej: Mates II de 10213
    # aunque el estudiante sea de la 10212).
    # Se gestiona desde el Admin de Django.
    horarios_personales = models.ManyToManyField(
        'Horario',
        blank=True,
        related_name='estudiantes_inscritos',
        verbose_name='Horarios personales',
    )
    # ─────────────────────────────────────────────────────────────────────────
    nombre        = models.CharField(max_length=100)
    apellido      = models.CharField(max_length=100)
    cedula        = models.CharField(max_length=20, unique=True)
    correo        = models.EmailField(unique=True)
    fecha_ingreso = models.DateField(default=timezone.now)
    activo        = models.BooleanField(default=True)
 
    class Meta:
        verbose_name        = "Estudiante"
        verbose_name_plural = "Estudiantes"
        ordering            = ['apellido', 'nombre']
 
    def __str__(self):
        return f"{self.apellido}, {self.nombre} ({self.cedula})"
 
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"
 
    def get_materias(self):
        """
        Las materias del estudiante vienen de sus horarios personales.
        Si no tiene horarios asignados aún, cae a las de su sección.
        """
        if self.horarios_personales.exists():
            return Materia.objects.filter(
                horarios__estudiantes_inscritos=self
            ).distinct()
        if self.seccion:
            return self.seccion.get_materias()
        return Materia.objects.none()
 
    def calcular_porcentaje_asistencia(self):
        total = self.asistencias.count()
        if total == 0:
            return 0
        presentes = self.asistencias.filter(estado='presente').count()
        return round((presentes / total) * 100, 2)
 
    @staticmethod
    def con_porcentaje():
        from django.db.models import Count, Case, When, FloatField, Value, ExpressionWrapper, F
        from django.db.models.functions import Coalesce
 
        return Estudiante.objects.filter(activo=True).annotate(
            total_clases=Count('asistencias'),
            clases_presente=Count(
                Case(
                    When(asistencias__estado='presente', then=1),
                    output_field=FloatField()
                )
            )
        ).annotate(
            porcentaje=Case(
                When(total_clases=0, then=Value(0.0)),
                default=ExpressionWrapper(
                    F('clases_presente') * 100.0 / F('total_clases'),
                    output_field=FloatField()
                ),
                output_field=FloatField()
            )
        )


# ===== SESIÓN DE CLASE =====
class SesionClase(models.Model):
    """
    Una clase activa iniciada por el profesor.
    Genera un token único que se codifica en el QR.
    """
    horario          = models.ForeignKey(Horario, on_delete=models.CASCADE, related_name='sesiones')
    fecha            = models.DateField(default=timezone.now)
    token            = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    activa           = models.BooleanField(default=True)
    duracion_minutos = models.IntegerField(default=15)
    creada_en        = models.DateTimeField(auto_now_add=True)
    creada_por       = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='sesiones_creadas',
        limit_choices_to={'rol': 'profesor'}
    )

    class Meta:
        verbose_name        = "Sesión de Clase"
        verbose_name_plural = "Sesiones de Clase"
        ordering            = ['-creada_en']

    def __str__(self):
        estado = 'Activa' if self.activa else 'Cerrada'
        return f"{self.horario.materia.nombre} — {self.fecha} ({estado})"

    @property
    def expira_en(self):
        from datetime import timedelta
        return self.creada_en + timedelta(minutes=self.duracion_minutos)

    @property
    def esta_vigente(self):
        return self.activa and timezone.now() < self.expira_en

    @property
    def minutos_restantes(self):
        if not self.esta_vigente:
            return 0
        diff = self.expira_en - timezone.now()
        return max(0, int(diff.total_seconds() / 60))


# ===== ASISTENCIA =====
class Asistencia(models.Model):
    ESTADOS = [
        ('presente',    'Presente'),
        ('ausente',     'Ausente'),
        ('tarde',       'Tardanza'),
        ('justificado', 'Justificado'),
    ]

    METODOS = [
        ('qr',     'Escaneo QR'),
        ('manual', 'Manual'),
    ]

    estudiante    = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='asistencias')
    materia       = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='asistencias')
    sesion        = models.ForeignKey(
        SesionClase, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='asistencias'
    )
    fecha         = models.DateField(default=timezone.now)
    hora          = models.TimeField(auto_now_add=True)
    estado        = models.CharField(max_length=15, choices=ESTADOS, default='presente')
    metodo        = models.CharField(max_length=10, choices=METODOS, default='qr')
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name        = "Asistencia"
        verbose_name_plural = "Asistencias"
        ordering            = ['-fecha', '-hora']
        unique_together     = ['estudiante', 'materia', 'fecha']

    def __str__(self):
        return (
            f"{self.estudiante.nombre_completo} — "
            f"{self.materia.nombre} "
            f"({self.get_estado_display()}) — {self.fecha}"
        )