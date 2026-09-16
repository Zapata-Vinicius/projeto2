# projeto2

Link do deploy:
http://54.87.227.253:5000/imoveis

## Links da API (HATEOAS)

As respostas de sucesso incluem `_links`. Cada link tem `href` (endereço relativo
à API) e `method` (método HTTP). Esse é o formato adotado por este projeto.

- A listagem retorna `{"imoveis": [...], "_links": {...}}`, inclusive quando vazia.
- Cada imóvel possui `self`, `collection`, `atualizar` e `remover`.
- A coleção oferece `criar`, `buscar_por_tipo` e `buscar_por_cidade`.
- Links com `templated: true` exigem substituir `{tipo}` ou `{cidade}` pelo
  valor desejado, codificado para URL.
- Após criar, use `self` ou o cabeçalho `Location` para consultar o novo imóvel.
- Após excluir, use `collection` para voltar à listagem.

Para criar (POST) ou atualizar (PUT), envie `Content-Type: application/json` e
os campos `logradouro`, `tipo_logradouro`, `bairro`, `cidade`, `cep`, `tipo`,
`valor` e `data_aquisicao` no corpo. Por exemplo:

```json
{
  "logradouro": "Rua Exemplo",
  "tipo_logradouro": "Rua",
  "bairro": "Centro",
  "cidade": "São Paulo",
  "cep": "01001000",
  "tipo": "casa",
  "valor": 250000,
  "data_aquisicao": "2026-09-16"
}
```

No Postman, a lista agora está em `pm.response.json().imoveis`.
Para rodar os testes: `python -m pytest -q`.
