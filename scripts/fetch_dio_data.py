#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para buscar certificados do perfil público da DIO (Digital Innovation One)
Extrai certificados obtidos e identifica novas habilidades baseadas nos títulos
"""

import requests
import json
import sys
from datetime import datetime
from bs4 import BeautifulSoup


def fetch_dio_profile(username):
    """
    Busca certificados do perfil público da DIO
    
    Args:
        username (str): Nome de usuário da DIO
    
    Returns:
        list: Lista de dicionários com certificados (titulo, url, data)
    """
    if not username:
        print("⚠️  Username da DIO não configurado em dio-config.json")
        return []
    
    url = f"https://www.dio.me/users/{username}"
    
    try:
        print(f"🔍 Buscando certificados da DIO para usuário: {username}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar links de certificados (hermes.dio.me)
        certificates = []
        cert_links = soup.find_all('a', href=lambda href: href and 'hermes.dio.me' in href)
        
        for link in cert_links:
            cert_url = link.get('href')
            # Tentar extrair o título do certificado
            cert_title = link.get_text(strip=True)
            
            # Se não tiver texto no link, tentar pegar do elemento pai
            if not cert_title:
                parent = link.find_parent()
                if parent:
                    cert_title = parent.get_text(strip=True)
            
            # Filtrar título vazio
            if cert_title and cert_url not in [c['url'] for c in certificates]:
                certificates.append({
                    'titulo': cert_title,
                    'url': cert_url,
                    'data': datetime.now().strftime('%Y-%m-%d')
                })
        
        print(f"✅ Encontrados {len(certificates)} certificados no perfil")
        return certificates
        
    except requests.RequestException as e:
        print(f"❌ Erro ao buscar perfil da DIO: {e}")
        return []
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return []


def extract_skills_from_certs(cert_titles):
    """
    Analisa títulos de certificados e detecta skills
    
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
    try:
        # Ler configuração
        with open('dio-config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        username = config.get('dio_username', '')
        
        if not username:
            print("⚠️  Configure o username da DIO em dio-config.json antes de executar")
            sys.exit(0)
        
        # Buscar certificados
        certificates = fetch_dio_profile(username)
        
        if not certificates:
            print("ℹ️  Nenhum certificado novo encontrado ou perfil inacessível")
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
        
    except FileNotFoundError:
        print("❌ Arquivo dio-config.json não encontrado")
        sys.exit(1)
    except json.JSONDecodeError:
        print("❌ Erro ao ler dio-config.json - formato JSON inválido")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro ao processar: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
