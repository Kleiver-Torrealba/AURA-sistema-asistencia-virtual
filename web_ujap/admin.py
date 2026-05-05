from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Usuario, UsuarioUJAP, Materia, Seccion,
    Horario, Estudiante, SesionClase, Asistencia
)
 
 
# ── Usuario ───────────────────────────────────────────────────────────────────
@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display  = ('username', 'email', 'rol', 'is_active')
    list_filter   = ('rol', 'is_active')
    fieldsets     = UserAdmin.fieldsets + (
        ('Datos AURA', {'fields': ('cedula', 'facultad', 'rol')}),
    )
 
 
# ── Materia ───────────────────────────────────────────────────────────────────
@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display  = ('codigo', 'nombre', 'creditos', 'activa')
    list_filter   = ('activa',)
    search_fields = ('codigo', 'nombre')
 
 
# ── Sección ───────────────────────────────────────────────────────────────────
@admin.register(Seccion)
class SeccionAdmin(admin.ModelAdmin):
    list_display  = ('codigo', 'carrera', 'periodo', 'activa')
    list_filter   = ('activa', 'periodo')
 
 
# ── Horario ───────────────────────────────────────────────────────────────────
@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display  = ('materia', 'seccion', 'dia_semana', 'hora_inicio', 'hora_fin', 'aula')
    list_filter   = ('dia_semana', 'seccion')
    search_fields = ('materia__nombre', 'materia__codigo', 'aula')
 
 
# ── Estudiante ────────────────────────────────────────────────────────────────
@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display   = ('apellido', 'nombre', 'cedula', 'seccion', 'activo')
    list_filter    = ('activo', 'seccion')
    search_fields  = ('nombre', 'apellido', 'cedula', 'correo')
 
    # Widget de dos columnas para asignar horarios de forma visual
    # Izquierda: horarios disponibles | Derecha: horarios asignados al estudiante
    filter_horizontal = ('horarios_personales',)
 
    fieldsets = (
        ('Datos personales', {
            'fields': ('usuario', 'nombre', 'apellido', 'cedula', 'correo', 'fecha_ingreso', 'activo')
        }),
        ('Académico', {
            'fields': ('seccion',)
        }),
        ('Horarios personales', {
            # Aquí se asignan los horarios individuales del estudiante
            # Podés seleccionar horarios de CUALQUIER sección
            'fields': ('horarios_personales',),
            'description': (
                'Asigná los horarios específicos de este estudiante. '
                'Podés mezclar horarios de distintas secciones. '
                'Cada fila representa una franja horaria (día + hora + materia + aula).'
            )
        }),
    )
 
 
# ── Sesión de Clase ───────────────────────────────────────────────────────────
@admin.register(SesionClase)
class SesionClaseAdmin(admin.ModelAdmin):
    list_display  = ('horario', 'fecha', 'activa', 'creada_por', 'creada_en')
    list_filter   = ('activa', 'fecha')
    readonly_fields = ('token', 'creada_en')
 
 
# ── Asistencia ────────────────────────────────────────────────────────────────
@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display  = ('estudiante', 'materia', 'fecha', 'estado', 'metodo')
    list_filter   = ('estado', 'metodo', 'fecha')
    search_fields = ('estudiante__nombre', 'estudiante__apellido', 'materia__nombre')
 
 
# ── Legacy ────────────────────────────────────────────────────────────────────
@admin.register(UsuarioUJAP)
class UsuarioUJAPAdmin(admin.ModelAdmin):
    list_display = ('cedula', 'correo', 'facultad')