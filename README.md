# Curriculum Vitae (CV) Online

Referência W3C: https://www.w3schools.com/howto/howto_website_create_resume.asp

## 🤖 Automação de Certificados e Skills da DIO

Este repositório conta com um sistema automatizado que busca e atualiza certificados e habilidades da **Digital Innovation One (DIO)** diretamente no currículo HTML.

### 📋 Como Funciona

O sistema é composto por:

1. **Script de Busca** (`scripts/fetch_dio_data.py`): Faz web scraping do perfil público da DIO para extrair certificados
2. **Script de Atualização** (`scripts/update_resume.py`): Atualiza o `index.html` com novos certificados e incrementa as barras de progresso das skills
3. **GitHub Actions** (`.github/workflows/update-dio-skills.yml`): Automatiza a execução dos scripts semanalmente

### ⚙️ Configuração

#### 1. Configurar Username da DIO

Edite o arquivo `dio-config.json` e adicione seu username da DIO:

```json
{
  "dio_username": "seu-username-aqui",
  "last_update": "",
  "skill_increment": 5,
  "auto_update_enabled": true
}
```

#### 2. Parâmetros de Configuração

- **dio_username**: Seu nome de usuário na plataforma DIO
- **skill_increment**: Percentual de incremento por curso (padrão: 5%)
- **auto_update_enabled**: Habilita/desabilita a automação (padrão: true)

### 🚀 Execução Manual

Para testar ou executar manualmente:

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Execute o script de busca:
```bash
python scripts/fetch_dio_data.py
```

3. Execute o script de atualização:
```bash
python scripts/update_resume.py
```

Ou execute via GitHub Actions:
1. Vá em **Actions** → **Update DIO Skills**
2. Clique em **Run workflow**
3. Aguarde a conclusão e verifique o currículo atualizado

### 📊 Mapeamento de Skills

O sistema detecta automaticamente skills baseado nos títulos dos cursos:

- **Python / POO**: python, poo, programação orientada
- **HTML / CSS**: html, css, web, frontend
- **Banco de dados**: sql, banco, database, mysql, postgres
- **Java**: java, spring, cloud native
- **JavaScript**: javascript, js, node, react
- **Git/GitHub**: git, github, versionamento

Cada curso relacionado incrementa a skill em 5-10% (configurável), até o máximo de 100%.

### 🔄 Automação

Por padrão, o workflow é executado:
- **Agendado**: Toda segunda-feira às 9h UTC
- **Manual**: Através do botão "Run workflow" no GitHub Actions

### 🛑 Desabilitar Automação

Para desabilitar a atualização automática:

1. Edite `dio-config.json` e defina:
```json
{
  "auto_update_enabled": false
}
```

2. Ou desabilite o workflow no GitHub:
   - Vá em **Actions** → **Update DIO Skills**
   - Clique nos "..." → **Disable workflow**

### 📁 Estrutura de Arquivos

```
.
├── index.html                    # Currículo HTML principal
├── dio-config.json               # Configurações da automação
├── requirements.txt              # Dependências Python
├── scripts/
│   ├── fetch_dio_data.py        # Script de busca na DIO
│   └── update_resume.py         # Script de atualização do HTML
└── .github/
    └── workflows/
        └── update-dio-skills.yml # Workflow do GitHub Actions
```

### 🔒 Importante

- Os certificados existentes são preservados
- O HTML mantém sua estrutura e formatação W3.CSS
- Não há duplicação de certificados
- Encoding UTF-8 para suporte a caracteres especiais

### 📝 Logs de Execução

Durante a execução, o sistema exibe:
```
🔍 Buscando certificados da DIO...
✅ Encontrados 3 novos certificados
📊 Skills detectadas: Python (+5%), Banco de dados (+10%)
📝 Atualizando index.html...
✅ Currículo atualizado com sucesso!
```

---

**Nota**: Configure o `dio_username` no arquivo `dio-config.json` antes de executar pela primeira vez.
