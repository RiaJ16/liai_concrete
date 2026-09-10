from dotenv import load_dotenv
load_dotenv()
import uuid
import pytest

from concrete.db import session_scope, NodoRepository


@pytest.fixture
def test_mac():
    return f"TEST-CIMPS-{f'{uuid.uuid4()}'[-4:]}"


@pytest.fixture
def cleanup_test_node():
    created_macs = []

    def register(mac):
        created_macs.append(mac)

    yield register

    with session_scope() as session:
        repo = NodoRepository(session)

        for mac in created_macs:
            nodo = repo.obtener_por_mac(mac)

            if nodo is not None:
                repo.eliminar(nodo.nodo_id)