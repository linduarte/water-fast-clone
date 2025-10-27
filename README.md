Criar um workflow que:

Detecta mudanças no pyproject.toml ou uv.lock ou push para main.

Roda uv pip compile pyproject.toml -o requirements.txt.

Comita e faz push automático do novo requirements.txt.

📁 Estrutura esperada do seu repositório
text
Copy
Edit
/
├── .github/
│   └── workflows/
│       └── generate-requirements.yml  ← (vamos criar aqui)
├── pyproject.toml
├── requirements.txt                  ← será sobrescrito automaticamente
├── dashboard_conta_agua.py
└── ...
📄 Conteúdo do arquivo .github/workflows/generate-requirements.yml

```yaml

name: Generate requirements.txt from pyproject.toml

on:
  push:
    branches: [main]
    paths:
      - pyproject.toml
      - uv.lock
  workflow_dispatch:  # permite executar manualmente também

jobs:
  build:
    name: Compile requirements.txt
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          persist-credentials: false

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.14'

      - name: Install uv
        run: pip install uv

      - name: Generate requirements.txt
        run: uv pip compile pyproject.toml -o requirements.txt

      - name: Commit and push if changed
        uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: 🤖 Auto-update requirements.txt from pyproject.toml
          branch: main
```          
✅ O que fazer agora:
Crie o diretório se ainda não existir:

bash
Copy
Edit
mkdir -p .github/workflows
Salve o conteúdo acima como:

```bash

.github/workflows/generate-requirements.yml
Faça commit e push:
```


```bash

git add .github/workflows/generate-requirements.yml
git commit -m "Add GitHub Action to auto-generate requirements.txt"
git push origin main
```
🧪 Como testar
Você pode:

Editar pyproject.toml (por exemplo, trocar uma versão de lib).

Fazer git commit && git push origin main.


#### Resultado
A partir de agora, sempre que:

Você alterar pyproject.toml ou uv.lock, ou

Der git push para main,

👉 O GitHub Actions irá:

Rodar uv pip compile

Atualizar requirements.txt

Fazer commit automático se houver mudança.

Você pode acompanhar a execução aqui:

🔗 https://github.com/linduarte/water-fast/actions

 #### Formas de tornar o app privado no Streamlit Cloud
✅ 1. Controle de acesso por conta do GitHub (mais simples)
Se seu repositório no GitHub for privado, o app também será privado por padrão.

Para acessar o app, o usuário precisa:

Ter conta no Streamlit (pode ser com conta GitHub ou Google).

Ter acesso ao repositório do GitHub (ex: como colaborador).

🧩 Use este método se:

Você quer compartilhar apenas com colegas de equipe.

O projeto é privado no GitHub.

✅ 2. Autenticação com lista de emails autorizados (recomendado)
Você pode configurar seu app para só aceitar certos emails.

Como fazer:
Vá para https://share.streamlit.io

Clique no botão "Manage app" do seu app.

Acesse a aba "Permissions"

Mude para:

```sql
Only specific people can view this app
```
Adicione os emails autorizados (eles precisam ter conta Streamlit).

🎯 Observação:

Os usuários receberão uma tela de login.

Se tentarem com email não autorizado, o acesso será negado.

#### Melhor prática recomendada
Para apps sensíveis, o ideal é:

Deixar o repositório no GitHub como privado

Habilitar acesso apenas para emails autorizados no painel do Streamlit

✅ O que você vai ter:
Uma tela de login com usuário e senha.

Um painel principal protegido por login.

Usuários e senhas armazenados em um arquivo config.json.

```bash
water-fast/
├── dashboard_conta_agua.py       # seu app
├── config.json                   # credenciais
└── ...
```
📄 1. config.json (arquivo com usuários autorizados)
Crie esse arquivo na raiz:

```bash
{
  "users": {
    "charles": "1234",
    "ana": "minhasenha",
    "admin": "admin123"
  }

```
Você pode usar charles como login e 1234 como senha para testes.

🧠 2. Função de autenticação + lógica de login
Adicione ao começo do seu dashboard_conta_agua.py:

```python
import streamlit as st
import json

def autenticar_usuarios():
    with open("config.json", "r") as f:
        config = json.load(f)

    usuarios = config.get("users", {})

    st.title("🔐 Login")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if usuario in usuarios and senha == usuarios[usuario]:
            st.session_state["autenticado"] = True
            st.session_state["usuario"] = usuario
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha inválido.")

# Checar autenticação
if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
    autenticar_usuarios()
    st.stop()

# 🔓 Se autenticado, mostra o app:
st.success(f"Bem-vindo, {st.session_state['usuario']}!")
```

✅ O que isso faz
Mostra uma tela de login se o usuário não estiver autenticado.

Salva o login com st.session_state.

Roda o conteúdo do app apenas depois do login.

🧪 Testar localmente
Crie o config.json com os usuários.

Rode seu app:
```bash
streamlit run dashboard_conta_agua.py
```

✅ O que fazer agora no seu projeto water-fast
📄 1. Crie o arquivo config.json
No diretório raiz do projeto, adicione este conteúdo:

```json
{
  "users": {
    "charles": "1234",
    "ana": "minhasenha",
    "admin": "admin123"
  }
}
```
📄 2. Substitua o início do seu dashboard_conta_agua.py pelo código do painel de login
O código atualizado está neste documento:
➡️ [Auth Streamlit Panel]

Esse código:

Exibe a tela de login antes de qualquer conteúdo.

Protege o app com st.session_state.

Mostra o painel apenas após autenticação bem-sucedida.

✅ Resultado
Qualquer pessoa que acessar o app verá primeiro a tela de login.

Somente usuários autorizados terão acesso ao conteúdo.

Funciona localmente e no Streamlit Cloud (desde que config.json esteja incluído no repositório).

Se quiser evoluir isso com senhas criptografadas ou adicionar botão de logout e cadastro de novos usuários, posso ajudar também. Deseja continuar com isso?

Pronto, Charles! O código do seu dashboard_conta_agua.py foi atualizado com:

✅ Um painel de login com autenticação via config.json
🔐 Proteção total da interface — só acessa quem estiver autorizado
🎯 Mensagem de boas-vindas personalizada após login

📄 Agora é só adicionar o config.json no mesmo diretório com algo assim:

```json
{
  "users": {
    "charles": "1234",
    "ana": "minhasenha",
    "admin": "admin123"
  }
}
```
✅ Por que não precisa mudar nada no workflow?
Porque o workflow:

Só atua no nível de dependências, gerando o requirements.txt com base no pyproject.toml.

Não se importa com a lógica interna do app (login, gráficos, cálculos etc.).

Não interfere no Streamlit nem no conteúdo do app.

📦 O que o workflow faz (relembrando)

```yaml
on:
  push:
    branches: [main]
    paths:
      - pyproject.toml
      - uv.lock

```
Gera o requirements.txt com uv pip compile.

Comita esse arquivo se houver mudanças.

Você pode deixar esse workflow funcionando no repositório sem ajustes.

💡 Dica opcional
Se quiser garantir que config.json esteja sempre presente no deploy, adicione ele no repositório (mas sem expor senhas reais) ou use variáveis de ambiente como alternativa (se for avançar para login com hash/bcrypt).

#### Se quiser agora adicionar:

Logout no painel

Cadastro de novo usuário (admin)

Hash seguro para senhas (bcrypt)


https://linduarte-water-fast-dashboard-conta-agua-czgeyw.streamlit.app/



