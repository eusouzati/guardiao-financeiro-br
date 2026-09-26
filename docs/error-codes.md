# Códigos de erro da API

Toda resposta de erro segue o formato:

```json
{
  "code": "GFB-0403",
  "message": "Você não tem permissão para executar esta operação.",
  "request_id": "5be3a11bb2564070af384ab23917dcf0",
  "details": []
}
```

- `message` é sempre em pt-BR e segura para exibição: nunca contém traceback, SQL,
  caminhos internos, segredos ou o valor enviado pelo usuário.
- `request_id` também vem no cabeçalho `X-Request-ID` e aparece nos logs — informe-o ao
  suporte para localizar o erro.
- `details` lista problemas por campo em erros de validação.

| Código     | HTTP | Significado                                                              |
| ---------- | ---- | ------------------------------------------------------------------------ |
| `GFB-0401` | 401  | Autenticação necessária.                                                 |
| `GFB-0403` | 403  | Usuário autenticado sem permissão para a operação (decidido no backend). |
| `GFB-0404` | 404  | Recurso ou rota inexistente.                                             |
| `GFB-0409` | 409  | Conflito de concorrência/versão (uso a partir da Sprint 4).              |
| `GFB-0422` | 422  | Dados da requisição inválidos (ver `details`).                           |
| `GFB-0500` | 500  | Erro interno inesperado (detalhes apenas nos logs).                      |
| `GFB-0503` | 503  | Serviço temporariamente indisponível.                                    |
| `GFB-1001` | 503  | Organização não inicializada (`python -m app.cli bootstrap`).            |
| `GFB-1101` | 422  | Valor de configuração inválido.                                          |
| `GFB-1201` | 422  | Valor monetário/decimal inválido.                                        |

Novos códigos são adicionados em `app/domain/errors.py` e documentados aqui na mesma PR.
