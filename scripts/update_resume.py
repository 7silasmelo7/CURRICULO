#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para atualizar o currículo HTML (index.html) com dados da DIO
Adiciona novos certificados e atualiza barras de progresso das skills
"""

import json
import sys
import re
from bs4 import BeautifulSoup


def load_dio_data():
    """Carrega dados extraídos da DIO"""
    try:
        with open('dio-data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Arquivo dio-data.json não encontrado. Execute fetch_dio_data.py primeiro")
        sys.exit(1)
    except json.JSONDecodeError:
        print("❌ Erro ao ler dio-data.json - formato JSON inválido")
        sys.exit(1)


def load_config():
    """Carrega configurações"""
    try:
        with open('dio-config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Arquivo dio-config.json não encontrado")
        sys.exit(1)


def update_skills(html_content, detected_skills, skill_increment):
    """
    Atualiza as barras de progresso das skills no HTML
    
    Args:
        html_content (str): Conteúdo HTML atual
        detected_skills (dict): Skills detectadas e suas frequências
        skill_increment (int): Incremento percentual por curso
    
    Returns:
        str: HTML atualizado
    """
    if not detected_skills:
        return html_content
    
    # Mapeamento de skills para seus nomes no HTML
    skill_names = {
        'Python / Programação Orientada a Objetos': 'Python / Programação Orientada a Objetos',
        'HTML / CSS': 'HTML / CSS',
        'Banco de dados': 'Banco de dados',
        'Java': 'Java',
        'JavaScript': 'JavaScript',
        'Git/GitHub': 'Git/GitHub'
    }
    
    updated_skills = []
    
    for skill, count in detected_skills.items():
        skill_html_name = skill_names.get(skill)
        if not skill_html_name:
            continue
        
        # Calcular incremento total
        total_increment = count * skill_increment
        
        # Buscar o padrão da skill no HTML usando regex
        # Procura por: <p>Nome da Skill</p> seguido de div com width:XX%
        pattern = rf'(<p>{re.escape(skill_html_name)}</p>\s*<div class="w3-light-grey w3-round-xlarge w3-small">\s*<div class="w3-container w3-center w3-round-xlarge w3-red" style="width:)(\d+)(%;?">)(\d+)(%;?</div>)'
        
        match = re.search(pattern, html_content)
        if match:
            current_percent = int(match.group(2))
            new_percent = min(current_percent + total_increment, 100)  # Máximo 100%
            
            if new_percent > current_percent:
                # Substituir width e texto interno
                replacement = f'{match.group(1)}{new_percent}{match.group(3)}{new_percent}{match.group(5)}'
                html_content = html_content[:match.start()] + replacement + html_content[match.end():]
                updated_skills.append(f"{skill} ({current_percent}% → {new_percent}%)")
        else:
            # Se não encontrou, tentar adicionar a skill (caso não exista)
            # Para simplicidade, apenas logamos que a skill não foi encontrada
            print(f"⚠️  Skill '{skill}' não encontrada no HTML para atualizar")
    
    if updated_skills:
        print(f"📊 Skills atualizadas: {', '.join(updated_skills)}")
    
    return html_content


def update_certificates(soup, new_certificates, existing_urls):
    """
    Adiciona novos certificados à lista da DIO no HTML
    
    Args:
        soup (BeautifulSoup): Objeto BeautifulSoup do HTML
        new_certificates (list): Lista de novos certificados
        existing_urls (set): URLs de certificados já existentes
    
    Returns:
        int: Número de certificados adicionados
    """
    # Encontrar a seção da DIO (procurar pelo título)
    dio_section = None
    for h5 in soup.find_all('h5', class_='w3-opacity'):
        if 'Digital Innovation One' in h5.get_text():
            dio_section = h5.find_parent('div', class_='w3-container')
            break
    
    if not dio_section:
        print("⚠️  Seção da DIO não encontrada no HTML")
        return 0
    
    # Encontrar a lista <ul> de certificados
    cert_list = dio_section.find('ul')
    if not cert_list:
        print("⚠️  Lista de certificados não encontrada na seção DIO")
        return 0
    
    # Adicionar novos certificados
    added_count = 0
    for cert in new_certificates:
        cert_url = cert['url']
        
        # Verificar se o certificado já existe
        if cert_url in existing_urls:
            continue
        
        # Criar novo item de lista
        new_li = soup.new_tag('li')
        new_a = soup.new_tag('a', href=cert_url, target='_blank')
        
        # Tentar extrair um título limpo
        cert_title = cert['titulo']
        if 'Curso:' not in cert_title:
            cert_title = f"Curso: {cert_title}"
        
        new_a.string = cert_title
        new_li.append(new_a)
        cert_list.append(new_li)
        
        added_count += 1
    
    return added_count


def main():
    """Função principal"""
    try:
        print("📝 Atualizando index.html...")
        
        # Carregar dados
        dio_data = load_dio_data()
        config = load_config()
        
        certificates = dio_data.get('certificates', [])
        detected_skills = dio_data.get('skills', {})
        skill_increment = config.get('skill_increment', 5)
        
        if not certificates and not detected_skills:
            print("ℹ️  Nenhum dado novo para atualizar")
            return
        
        # Ler HTML atual
        with open('index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Atualizar skills (fazemos isso diretamente no HTML string para preservar formatação)
        html_content = update_skills(html_content, detected_skills, skill_increment)
        
        # Parsear HTML com BeautifulSoup para atualizar certificados
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extrair URLs dos certificados existentes
        existing_urls = set()
        for a in soup.find_all('a', href=lambda href: href and 'hermes.dio.me' in href):
            existing_urls.add(a.get('href'))
        
        # Adicionar novos certificados
        added_count = update_certificates(soup, certificates, existing_urls)
        
        if added_count > 0:
            print(f"✅ Encontrados {added_count} novos certificados")
            
            # Salvar HTML atualizado (preservando formatação original)
            # Usamos prettify com formatter=None para manter encoding
            updated_html = str(soup)
            
            with open('index.html', 'w', encoding='utf-8') as f:
                f.write(updated_html)
            
            print("✅ Currículo atualizado com sucesso!")
        else:
            # Mesmo sem novos certificados, salvamos se skills foram atualizadas
            if detected_skills:
                with open('index.html', 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print("✅ Currículo atualizado com sucesso!")
            else:
                print("ℹ️  Nenhum certificado novo para adicionar")
        
    except FileNotFoundError:
        print("❌ Arquivo index.html não encontrado")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro ao atualizar HTML: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
