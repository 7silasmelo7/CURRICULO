# Curriculum Vitae (CV) Online

Referência W3C: https://www.w3schools.com/howto/howto_website_create_resume.asp

## 🤖 Automação de Certificados e Skills da DIO

Este repositório conta com um sistema automatizado que busca e atualiza certificados e habilidades da **Digital Innovation One (DIO)** diretamente no currículo HTML.

### ✨ Novo: Login Automatizado com Selenium

O sistema agora suporta **autenticação automatizada** na DIO usando Selenium WebDriver, permitindo:
- ✅ Acesso a perfis privados ou restritos
- ✅ Extração de certificados de contas que requerem login
- ✅ Maior confiabilidade na obtenção dos dados
- ✅ Compatível com GitHub Actions

### 📋 Como Funciona

O sistema é composto por:

1. **Script de Busca com Selenium** (`scripts/fetch_dio_data_selenium.py`): Faz login automatizado na DIO e extrai certificados (incluindo de perfis privados)
2. **Script de Busca Legado** (`scripts/fetch_dio_data.py`): Faz web scraping do perfil público da DIO para extrair certificados (apenas perfis públicos)
3. **Script de Atualização** (`scripts/update_resume.py`): Atualiza o `index.html` com novos certificados e incrementa as barras de progresso das skills
4. **GitHub Actions** (`.github/workflows/update-dio-skills.yml`): Automatiza a execução dos scripts semanalmente

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

#### 2. Configurar GitHub Secrets (Necessário para Login Automatizado)

Para usar o novo script com autenticação, você precisa configurar os secrets no GitHub:

**Passo a passo:**

1. Vá até seu repositório no GitHub
2. Clique em **Settings** (Configurações)
3. No menu lateral, vá em **Secrets and variables** → **Actions**
4. Clique em **New repository secret**
5. Crie dois secrets:
   - **Nome**: `DIO_EMAIL` | **Valor**: seu-email@exemplo.com
   - **Nome**: `DIO_PASSWORD` | **Valor**: sua-senha-da-dio

**⚠️ Importante:**
- Nunca compartilhe ou commite suas credenciais no código
- Os secrets são criptografados e nunca aparecem nos logs
- Apenas workflows autorizados podem acessar os secrets

#### 3. Parâmetros de Configuração

- **dio_username**: Seu nome de usuário na plataforma DIO
- **skill_increment**: Percentual de incremento por curso (padrão: 5%)
- **auto_update_enabled**: Habilita/desabilita a automação (padrão: true)

### 🚀 Execução Manual

#### Script com Selenium (requer credenciais)

Para testar localmente o novo script com autenticação:

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Configure as variáveis de ambiente:
```bash
export DIO_EMAIL="seu-email@exemplo.com"
export DIO_PASSWORD="sua-senha"
```

3. Execute o script de busca com Selenium:
```bash
python scripts/fetch_dio_data_selenium.py
```

#### Script Legado (apenas perfis públicos)

Para usar o script original sem autenticação:

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

#### Via GitHub Actions

Execute via GitHub Actions:
1. Vá em **Actions** → **Update DIO Skills**
2. Clique em **Run workflow**
3. Aguarde a conclusão e verifique o currículo atualizado

### 🔄 Diferenças entre os Scripts

| Característica | Script com Selenium | Script Legado |
|---|---|---|
| **Arquivo** | `fetch_dio_data_selenium.py` | `fetch_dio_data.py` |
| **Autenticação** | ✅ Sim (via login) | ❌ Não |
| **Perfis Privados** | ✅ Funciona | ❌ Não funciona |
| **Perfis Públicos** | ✅ Funciona | ✅ Funciona |
| **Requer Credenciais** | ✅ Sim | ❌ Não |
| **Requer Chrome** | ✅ Sim | ❌ Não |
| **Velocidade** | 🐢 Mais lento (15-30s) | ⚡ Rápido (5-10s) |
| **Confiabilidade** | ⭐⭐⭐⭐⭐ Alta | ⭐⭐⭐ Média |
| **Uso Atual** | ✅ Padrão no workflow | 🔄 Fallback/legado |

**Recomendação**: Use o script com Selenium para maior confiabilidade e acesso a perfis privados.

### 🔐 Segurança

**Boas Práticas Implementadas:**
- ✅ Credenciais armazenadas apenas em GitHub Secrets (criptografados)
- ✅ Senhas nunca aparecem em logs ou outputs
- ✅ Variáveis de ambiente usadas para credenciais locais
- ✅ Nenhuma credencial hardcoded no código
- ✅ Conexões seguras (HTTPS)

**⚠️ Notas de Segurança:**
- Nunca commite credenciais no repositório
- Mantenha seus secrets do GitHub protegidos
- Use senhas fortes e únicas para a DIO
- Considere habilitar 2FA na sua conta DIO (pode requerer ajustes no script)

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
├── index.html                         # Currículo HTML principal
├── dio-config.json                    # Configurações da automação
├── dio-data.json                      # Dados extraídos da DIO (gerado)
├── requirements.txt                   # Dependências Python
├── scripts/
│   ├── fetch_dio_data_selenium.py    # Script de busca com login (Selenium)
│   ├── fetch_dio_data.py             # Script de busca legado (público)
│   └── update_resume.py              # Script de atualização do HTML
└── .github/
    └── workflows/
        └── update-dio-skills.yml      # Workflow do GitHub Actions
```

### 🔒 Importante

- Os certificados existentes são preservados
- O HTML mantém sua estrutura e formatação W3.CSS
- Não há duplicação de certificados
- Encoding UTF-8 para suporte a caracteres especiais
- Credenciais nunca são expostas em logs

### 📝 Logs de Execução

Durante a execução do script com Selenium, o sistema exibe:
```
🔧 Configurando Chrome WebDriver em modo headless...
✅ Chrome WebDriver configurado com sucesso
🔐 Realizando login na DIO com email: seu***@exemplo.com
📧 Email preenchido
🔑 Senha preenchida
🖱️  Botão de login clicado
✅ Login realizado com sucesso!
🔍 Buscando certificados para o usuário: seu-username
📋 Encontrados 15 links de certificados
✅ Extraídos 15 certificados únicos
📊 Skills detectadas: Python / Programação Orientada a Objetos (3), JavaScript (2)
✅ Dados salvos em dio-data.json
🎉 Processo concluído com sucesso!
🔒 Navegador fechado
```

### 🔧 Troubleshooting

**Problema: "Credenciais não configuradas"**
- Certifique-se de que os GitHub Secrets `DIO_EMAIL` e `DIO_PASSWORD` estão configurados
- Para teste local, verifique se as variáveis de ambiente estão definidas

**Problema: "Login falhou"**
- Verifique se o email e senha estão corretos
- A DIO pode ter alterado a página de login - o script pode precisar de atualização
- Verifique se sua conta não requer 2FA

**Problema: "Nenhum certificado encontrado"**
- Verifique se o username está correto no `dio-config.json`
- A DIO pode ter alterado o layout da página - o script pode precisar de atualização
- Certifique-se de que você possui certificados visíveis no seu perfil

**Problema: "Chrome WebDriver não encontrado"**
- No GitHub Actions, certifique-se de que o step `setup-chrome` está presente
- Localmente, instale o Chrome e ChromeDriver manualmente

---

**Nota**: Configure o `dio_username` no arquivo `dio-config.json` antes de executar pela primeira vez.
