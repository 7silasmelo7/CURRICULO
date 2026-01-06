#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para buscar certificados da DIO (Digital Innovation One) com autenticação via Selenium
Permite acessar perfis privados através de login automatizado
Extrai certificados obtidos e identifica novas habilidades baseadas nos títulos
"""

import os
import sys
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException


def setup_driver():
    """
    Configura o Chrome WebDriver em modo headless
    
    Returns:
        webdriver.Chrome: Instância configurada do driver
    """
    print("🔧 Configurando Chrome WebDriver em modo headless...")
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        print("✅ Chrome WebDriver configurado com sucesso")
        return driver
    except WebDriverException as e:
        print(f"❌ Erro ao configurar Chrome WebDriver: {e}")
        print("💡 Certifique-se de que o Chrome e ChromeDriver estão instalados")
        sys.exit(1)


def login_dio(driver, email, password):
    """
    Realiza login na plataforma DIO
    
    Args:
        driver: Instância do WebDriver
        email (str): Email de login
        password (str): Senha de login
    
    Returns:
        bool: True se login foi bem-sucedido, False caso contrário
    """
    print(f"🔐 Realizando login na DIO com email: {email[:3]}***{email[-10:]}")
    
    try:
        # Navegar para página de login
        driver.get("https://www.dio.me/sign-in")
        
        # Aguardar o carregamento da página de login
        wait = WebDriverWait(driver, 15)
        
        # Tentar encontrar os campos de login (podem ter diferentes seletores)
        # Tentativa 1: Por ID
        try:
            email_field = wait.until(
                EC.presence_of_element_located((By.ID, "email"))
            )
        except TimeoutException:
            # Tentativa 2: Por name
            try:
                email_field = driver.find_element(By.NAME, "email")
            except NoSuchElementException:
                # Tentativa 3: Por type
                email_field = driver.find_element(By.CSS_SELECTOR, 'input[type="email"]')
        
        # Preencher email
        email_field.clear()
        email_field.send_keys(email)
        print("📧 Email preenchido")
        
        # Encontrar campo de senha
        try:
            password_field = driver.find_element(By.ID, "password")
        except NoSuchElementException:
            try:
                password_field = driver.find_element(By.NAME, "password")
            except NoSuchElementException:
                password_field = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
        
        # Preencher senha
        password_field.clear()
        password_field.send_keys(password)
        print("🔑 Senha preenchida")
        
        # Encontrar e clicar no botão de login
        try:
            login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        except NoSuchElementException:
            try:
                login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Entrar') or contains(text(), 'Login')]")
            except NoSuchElementException:
                login_button = driver.find_element(By.CSS_SELECTOR, 'button.btn-primary')
        
        login_button.click()
        print("🖱️  Botão de login clicado")
        
        # Aguardar o login ser processado (esperar por redirecionamento ou elemento da página logada)
        time.sleep(5)
        
        # Verificar se o login foi bem-sucedido
        # Procurar por elementos que indicam login bem-sucedido
        try:
            # Tentar encontrar elemento de perfil ou navegação autenticada
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="user-menu"], .user-menu, [class*="avatar"], [class*="profile"]'))
            )
            print("✅ Login realizado com sucesso!")
            return True
        except TimeoutException:
            # Verificar se ainda estamos na página de login (indicando falha)
            if "sign-in" in driver.current_url:
                print("❌ Login falhou - ainda na página de login")
                return False
            else:
                # Assumir que login foi bem-sucedido se saímos da página de login
                print("✅ Login realizado com sucesso!")
                return True
    
    except TimeoutException as e:
        print(f"❌ Timeout ao tentar fazer login: {e}")
        return False
    except NoSuchElementException as e:
        print(f"❌ Elemento não encontrado durante o login: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado durante o login: {e}")
        return False


def fetch_certificates(driver, username):
    """
    Extrai certificados do perfil do usuário após login
    
    Args:
        driver: Instância do WebDriver (já logado)
        username (str): Nome de usuário da DIO
    
    Returns:
        list: Lista de dicionários com certificados (titulo, url, data)
    """
    print(f"🔍 Buscando certificados para o usuário: {username}")
    
    try:
        # Navegar para o perfil do usuário
        profile_url = f"https://www.dio.me/users/{username}"
        driver.get(profile_url)
        
        # Aguardar o carregamento da página
        time.sleep(5)
        
        # Tentar rolar a página para carregar todo o conteúdo
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # Buscar links de certificados (hermes.dio.me)
        certificates = []
        
        # Encontrar todos os links que apontam para certificados
        cert_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="hermes.dio.me"]')
        
        print(f"📋 Encontrados {len(cert_links)} links de certificados")
        
        for link in cert_links:
            try:
                cert_url = link.get_attribute('href')
                cert_title = link.text.strip()
                
                # Se não tiver texto no link, tentar pegar de elemento relacionado
                if not cert_title:
                    # Tentar encontrar texto em elementos próximos
                    parent = link.find_element(By.XPATH, '..')
                    cert_title = parent.text.strip()
                
                # Filtrar certificados vazios ou duplicados
                if cert_title and cert_url not in [c['url'] for c in certificates]:
                    certificates.append({
                        'titulo': cert_title,
                        'url': cert_url,
                        'data': datetime.now().strftime('%Y-%m-%d')
                    })
            except Exception as e:
                print(f"⚠️  Erro ao processar certificado: {e}")
                continue
        
        print(f"✅ Extraídos {len(certificates)} certificados únicos")
        return certificates
    
    except TimeoutException as e:
        print(f"❌ Timeout ao buscar certificados: {e}")
        return []
    except Exception as e:
        print(f"❌ Erro ao buscar certificados: {e}")
        return []


def extract_skills_from_certs(cert_titles):
    """
    Analisa títulos de certificados e detecta skills
    (Mesma lógica do script original)
    
    Args:
        cert_titles (list): Lista de títulos de certificados
    
    Returns:
        dict: Dicionário com skills detectadas e sua frequência
    """
    # Mapeamento de palavras-chave para skills
    skill_keywords = {
        'Python / Programação Orientada a Objetos': ['python', 'poo', 'programação orientada', 'objetos'],
        'HTML / CSS': ['html', 'css', 'web', 'frontend', 'front-end'],
        'Banco de dados': ['sql', 'banco', 'database', 'mysql', 'postgres', 'oracle', 'mongodb'],
        'Java': ['java', 'spring', 'cloud native', 'jvm'],
        'JavaScript': ['javascript', 'js', 'node', 'react', 'angular', 'vue'],
        'Git/GitHub': ['git', 'github', 'versionamento', 'controle de versão']
    }
    
    detected_skills = {}
    
    for title in cert_titles:
        title_lower = title.lower()
        
        for skill_name, keywords in skill_keywords.items():
            for keyword in keywords:
                if keyword in title_lower:
                    detected_skills[skill_name] = detected_skills.get(skill_name, 0) + 1
                    break  # Evitar contar múltiplas vezes o mesmo certificado para a mesma skill
    
    return detected_skills


def main():
    """Função principal"""
    driver = None
    
    try:
        # Obter credenciais de variáveis de ambiente
        email = os.environ.get('DIO_EMAIL')
        password = os.environ.get('DIO_PASSWORD')
        
        if not email or not password:
            print("❌ Credenciais não configuradas!")
            print("💡 Configure as variáveis de ambiente DIO_EMAIL e DIO_PASSWORD")
            print("   Exemplo: export DIO_EMAIL='seu-email@exemplo.com'")
            print("            export DIO_PASSWORD='sua-senha'")
            sys.exit(1)
        
        # Ler configuração para obter username
        try:
            with open('dio-config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
        except FileNotFoundError:
            print("❌ Arquivo dio-config.json não encontrado")
            sys.exit(1)
        
        username = config.get('dio_username', '')
        
        if not username:
            print("⚠️  Configure o username da DIO em dio-config.json antes de executar")
            sys.exit(1)
        
        # Configurar WebDriver
        driver = setup_driver()
        
        # Fazer login
        login_success = login_dio(driver, email, password)
        
        if not login_success:
            print("❌ Não foi possível fazer login na DIO")
            print("💡 Verifique suas credenciais e tente novamente")
            sys.exit(1)
        
        # Buscar certificados
        certificates = fetch_certificates(driver, username)
        
        if not certificates:
            print("ℹ️  Nenhum certificado encontrado")
            # Criar arquivo vazio para não quebrar o workflow
            data = {
                'certificates': [],
                'skills': {},
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        else:
            # Extrair skills dos títulos
            cert_titles = [cert['titulo'] for cert in certificates]
            detected_skills = extract_skills_from_certs(cert_titles)
            
            # Preparar dados para salvar
            data = {
                'certificates': certificates,
                'skills': detected_skills,
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            print(f"📊 Skills detectadas: {', '.join([f'{k} ({v})' for k, v in detected_skills.items()])}")
        
        # Salvar dados em JSON
        with open('dio-data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print("✅ Dados salvos em dio-data.json")
        
        # Atualizar data da última busca no config
        config['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('dio-config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print("🎉 Processo concluído com sucesso!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Processo interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Fechar o navegador
        if driver:
            try:
                driver.quit()
                print("🔒 Navegador fechado")
            except Exception:
                pass


if __name__ == '__main__':
    main()
