"""Tests unitarios de la máquina de estados del chatbot (RF-04).

Ejecutar desde la raíz del repositorio:
    python -m pytest tests/ -q
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

from routers.chatbot import procesar_mensaje, MensajeRequest, FLUJO  # noqa: E402


def test_inicio_avanza_a_tratamiento_datos():
    r = procesar_mensaje(MensajeRequest(estado_actual="inicio", opcion_elegida="Sí, cuéntame más"))
    assert r["estado"] == "tratamiento_datos"
    assert r["es_final"] is False
    assert len(r["opciones"]) == 2


def test_rechazo_inicial_lleva_a_despedida():
    r = procesar_mensaje(MensajeRequest(estado_actual="inicio", opcion_elegida="No gracias"))
    assert r["estado"] == "despedida"
    assert r["es_final"] is True


def test_flujo_feliz_completo_hasta_entrega_asesor():
    pasos = [
        ("inicio", "Sí, cuéntame más", "tratamiento_datos"),
        ("tratamiento_datos", "Autorizo", "calentamiento"),
        ("calentamiento", "El precio", "interes"),
        ("interes", "Sí, quiero que me llamen", "entrega_asesor"),
    ]
    for estado, opcion, esperado in pasos:
        r = procesar_mensaje(MensajeRequest(estado_actual=estado, opcion_elegida=opcion))
        assert r["estado"] == esperado, f"{estado} -> {opcion} debía dar {esperado}"
    assert r["es_final"] is True  # entrega_asesor es estado final


def test_opcion_invalida_resetea_a_inicio():
    r = procesar_mensaje(MensajeRequest(estado_actual="calentamiento", opcion_elegida="opcion_inexistente"))
    assert r["estado"] == "inicio"


def test_sin_opcion_devuelve_mensaje_inicial():
    r = procesar_mensaje(MensajeRequest(estado_actual="inicio"))
    assert r["estado"] == "inicio"
    assert r["mensaje"] == FLUJO["inicio"]["mensaje"]


def test_todos_los_estados_finales_no_tienen_opciones():
    for nombre, nodo in FLUJO.items():
        if not nodo["siguiente"]:
            assert nodo["opciones"] == [], f"El estado final {nombre} no debe tener opciones"
