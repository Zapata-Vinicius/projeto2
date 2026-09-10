import pytest
from unittest.mock import patch,MagicMock
from api import app


@pytest.fixture #Poderá ser utilizada em outras funções
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@patch("api.conectar_banco")
def test_listar_imoveis_vazios (mock_conectar_banco, client):
    mock_conn = MagicMock() 
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = []

    mock_conectar_banco.return_value = mock_conn

    response = client.get("/imoveis")

    assert response.status_code == 200
    assert response.get_json() == []

    mock_cursor.execute.assert_called_once_with (
        "SELECT * FROM imoveis"
    )

    mock_cursor.fetchall.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("api.conectar_banco")
def test_listar_imoveis_com_dados (mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [
        (1, 'Nicole Common', 'Travessa', 'Lake Danielle', 'Judymouth', '85184', 'casa em condominio', 488423.52, '2017-07-29'),
        (2, 'Price Prairie', 'Travessa', 'Colonton', 'North Garyville', '93354', 'casa em condominio', 260069.89, '2021-11-30')
    ]

    mock_conectar_banco.return_value = mock_conn

    response = client.get("/imoveis")

    assert response.status_code == 200
    assert response.get_json() == [
        {
            "id": 1,
            "logradouro": "Nicole Common",
            "tipo_logradouro": "Travessa",
            "bairro": "Lake Danielle",
            "cidade": "Judymouth",
            "cep": "85184",
            "tipo": "casa em condominio",
            "valor": 488423.52,
            "data_aquisicao": "2017-07-29"
        },
        {
            "id": 2,
            "logradouro": "Price Prairie",
            "tipo_logradouro": "Travessa",
            "bairro": "Colonton",
            "cidade": "North Garyville",
            "cep": "93354",
            "tipo": "casa em condominio",
            "valor": 260069.89,
            "data_aquisicao": "2021-11-30"
        }
    ]

    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM imoveis"
    )

    mock_cursor.fetchall.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("api.conectar_banco")
def test_imovel_id_especifico_ok(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (1, 'Nicole Common', 'Travessa', 'Lake Danielle', 'Judymouth', '85184', 'casa em condominio', 488423.52, '2017-07-29')

    mock_conectar_banco.return_value = mock_conn
    response = client.get("/imoveis/1")

    assert response.status_code == 200
    assert response.get_json() =={
            "id": 1,
            "logradouro": "Nicole Common",
            "tipo_logradouro": "Travessa",
            "bairro": "Lake Danielle",
            "cidade": "Judymouth",
            "cep": "85184",
            "tipo": "casa em condominio",
            "valor": 488423.52,
            "data_aquisicao": "2017-07-29"
        }

    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM imoveis WHERE id = %s",
        (1,)
    )
    mock_cursor.fetchone.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("api.conectar_banco")
def test_imovel_id_especifico_erro(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchone.return_value = None
    mock_conectar_banco.return_value = mock_conn

    response = client.get("/imoveis/1")

    assert response.status_code == 404
    assert response.get_json() == {"erro": "Imóvel não encontrado"}

    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM imoveis WHERE id = %s",
        (1, ), 
    )
    mock_cursor.fetchone.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("api.conectar_banco")
def test_adicionar_novo_imovel_ok (mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.lastrowid = 1

    mock_conectar_banco.return_value = mock_conn

    payload = {
            "logradouro": "Nicole Common",
            "tipo_logradouro": "Travessa",
            "bairro": "Lake Danielle",
            "cidade": "Judymouth",
            "cep": "85184",
            "tipo": "casa em condominio",
            "valor": 488423.52,
            "data_aquisicao": "2017-07-29"
    }
    response = client.post("/imoveis", json=payload)

    assert response.status_code == 201
    assert response.get_json() == {"id":1}

    mock_cursor.execute.assert_called_once_with(
        "INSERT INTO imoveis (logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao) VALUES (%s, %s, %s, %s ,%s, %s, %s, %s)",
        ("Nicole Common", "Travessa", "Lake Danielle", "Judymouth", "85184", "casa em condominio", 488423.52, "2017-07-29"),
    )

    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("api.conectar_banco")
def test_adicionar_novo_imovel_erro (mock_conectar_banco, client):
    response = client.post("/imoveis", json={"logradouro":"Sé"})

    assert response.status_code == 400
    assert response.get_json() == {"erro": "Campos obrigatórios: logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao"}

    mock_conectar_banco.assert_not_called()


@patch("api.conectar_banco")
def test_atualizar_imovel(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.rowcount = 1
    mock_conectar_banco.return_value = mock_conn

    payload = {
        "logradouro": "Nicole Common",
        "tipo_logradouro": "Travessa",
        "bairro": "Lake Danielle",
        "cidade": "Judymouth",
        "cep": "85184",
        "tipo": "casa em condominio",
        "valor": 488423.52,
        "data_aquisicao": "2017-07-29"
    }
    response = client.put("/imoveis/1", json=payload)

    assert response.status_code == 200
    assert response.get_json() == {"mensagem": "Imóvel atualizado com sucesso!"}

    mock_cursor.execute.assert_called_once_with(
        "UPDATE imoveis SET logradouro = %s , tipo_logradouro = %s , bairro = %s , cidade = %s , cep = %s , tipo = %s , valor = %s , data_aquisicao = %s WHERE id  = %s ",
        ('Nicole Common', 'Travessa', 'Lake Danielle', 'Judymouth', '85184', 'casa em condominio', 488423.52, '2017-07-29', 1)
    )

    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("api.conectar_banco")
def test_erro_ao_atualizar_sem_dados(mock_conectar_banco, client):
    payload = {"logradouro": "Nicole Common"}
    response = client.put("/imoveis/1", json=payload)

    assert response.status_code == 400
    assert response.get_json() == {"erro": "Campos obrigatórios: logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao"}

    mock_conectar_banco.assert_not_called()

@patch("api.conectar_banco")
def test_imovel_nao_encontrado_atualizando(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.rowcount = 0
    mock_conectar_banco.return_value = mock_conn

    payload = {
        "logradouro": "Nicole Common",
        "tipo_logradouro": "Travessa",
        "bairro": "Lake Danielle",
        "cidade": "Judymouth",
        "cep": "85184",
        "tipo": "casa em condominio",
        "valor": 488423.52,
        "data_aquisicao": "2017-07-29"
    }
    response = client.put("/imoveis/999", json=payload)

    assert response.status_code == 404
    assert response.get_json() == {"erro": "Imóvel não encontrado"}

    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("api.conectar_banco")
def test_deletar_imovel(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.rowcount = 1
    mock_conectar_banco.return_value = mock_conn
    response = client.delete("/imoveis/1")

    assert response.status_code == 200
    assert response.get_json() == {"mensagem": "Imóvel apagado com sucesso!"}

    mock_cursor.execute.assert_called_once_with(
        "DELETE FROM imoveis WHERE id= %s",
        (1,)
    )

    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("api.conectar_banco")
def test_falha_ao_deletar(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.rowcount = 0
    mock_conectar_banco.return_value = mock_conn
    response = client.delete("/imoveis/999")

    assert response.status_code == 404
    assert response.get_json() == {"erro": "Imóvel não encontrado"}

    mock_cursor.execute.assert_called_once_with(
        "DELETE FROM imoveis WHERE id= %s",
        (999,)
    )

    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("api.conectar_banco")
def test_buscar_imoveis_tipo(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_conectar_banco.return_value = mock_conn
    mock_cursor.fetchall.return_value = [
        (
            1,
            "Nicole Common",
            "Travessa",
            "Lake Danielle",
            "Judymouth",
            "85184",
            "casa",
            488423.52,
            "2017-07-29"
        )
    ]
    response = client.get("/imoveis?tipo=casa")
    assert response.status_code == 200
    assert response.get_json() == [
        {
            "id": 1,
            "logradouro": "Nicole Common",
            "tipo_logradouro": "Travessa",
            "bairro": "Lake Danielle",
            "cidade": "Judymouth",
            "cep": "85184",
            "tipo": "casa",
            "valor": 488423.52,
            "data_aquisicao": "2017-07-29"
        }
    ]

    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM imoveis WHERE tipo = %s",
        ("casa",)
    )
    mock_cursor.fetchall.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("api.conectar_banco")
def test_buscar_imoveis_tipo_erro(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_conectar_banco.return_value = mock_conn
    mock_cursor.fetchall.return_value = []

    response = client.get("/imoveis?tipo=castelo")
    assert response.status_code == 200
    assert response.get_json() == []

    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM imoveis WHERE tipo = %s",
        ("castelo",)
    )
    mock_cursor.fetchall.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("api.conectar_banco")
def test_buscar_imoveis_cidade(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_conectar_banco.return_value = mock_conn
    mock_cursor.fetchall.return_value =[
        (
            1,
            "Nicole Common",
            "Travessa",
            "Lake Danielle",
            "Judymouth",
            "85184",
            "casa",
            488423.52,
            "2017-07-29"
        )
    ]
    response = client.get("/imoveis?cidade=Judymouth")
    assert response.status_code == 200
    assert response.get_json() == [
        {
            "id": 1,
            "logradouro": "Nicole Common",
            "tipo_logradouro": "Travessa",
            "bairro": "Lake Danielle",
            "cidade": "Judymouth",
            "cep": "85184",
            "tipo": "casa",
            "valor": 488423.52,
            "data_aquisicao": "2017-07-29"
        }
    ]
    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM imoveis WHERE cidade = %s",
        ("Judymouth",)
    )

    mock_cursor.fetchall.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("api.conectar_banco")
def test_buscar_imoveis_cidade_erro(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_conectar_banco.return_value = mock_conn
    mock_cursor.fetchall.return_value = []

    response = client.get("/imoveis?cidade=seoul")
    assert response.status_code == 200
    assert response.get_json() == []

    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM imoveis WHERE cidade = %s",
        ("seoul",)
    )

    mock_cursor.fetchall.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()