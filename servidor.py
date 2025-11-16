from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import threading

app = Flask(__name__)
CORS(app)

class BuscadorPanoramasWeb:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.eventos_gratuitos = []
        self.eventos_pagados = []
        self.progreso = 0
        self.total_fuentes = 10
        self.buscando = False
    
    def actualizar_progreso(self):
        self.progreso += 1
    
    # ============ EVENTOS GRATUITOS ============
    
    def buscar_eventbrite_gratis(self):
        """Busca eventos gratuitos en Eventbrite"""
        print("🔍 Buscando en Eventbrite (gratis)...")
        try:
            url = "https://www.eventbrite.cl/d/chile--santiago/free--events/"
            response = requests.get(url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar múltiples posibles selectores
            eventos = (soup.find_all('div', class_='discover-search-desktop-card') or
                      soup.find_all('article') or
                      soup.find_all('div', class_='event-card'))[:15]
            
            for evento in eventos:
                titulo = evento.find('h3') or evento.find('h2') or evento.find('div', class_='event-title')
                fecha = evento.find('time') or evento.find('p', class_='event-date')
                link = evento.find('a')
                
                if titulo and link:
                    href = link.get('href', '')
                    if not href.startswith('http'):
                        href = 'https://www.eventbrite.cl' + href
                    
                    self.eventos_gratuitos.append({
                        'titulo': titulo.get_text(strip=True),
                        'fuente': 'Eventbrite',
                        'fecha': fecha.get_text(strip=True) if fecha else 'Ver fecha en sitio',
                        'precio': 'GRATIS',
                        'link': href
                    })
            
            print(f"✅ Encontrados {len(eventos)} eventos en Eventbrite")
        except Exception as e:
            print(f"❌ Error en Eventbrite: {str(e)}")
        finally:
            self.actualizar_progreso()
    
    def buscar_latercera_gratis(self):
        """Busca panoramas gratis en La Tercera"""
        print("🔍 Buscando en La Tercera (panoramas gratis)...")
        try:
            url = "https://www.latercera.com/etiqueta/panoramas-gratis/"
            response = requests.get(url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            eventos = soup.find_all('article', limit=10)
            
            for evento in eventos:
                titulo = evento.find('h2') or evento.find('h3')
                link = evento.find('a')
                
                if titulo and link:
                    href = link.get('href', '')
                    if not href.startswith('http'):
                        href = 'https://www.latercera.com' + href
                    
                    self.eventos_gratuitos.append({
                        'titulo': titulo.get_text(strip=True),
                        'fuente': 'La Tercera',
                        'fecha': 'Consultar artículo',
                        'precio': 'GRATIS',
                        'link': href
                    })
            
            print(f"✅ Encontrados {len(eventos)} panoramas en La Tercera")
        except Exception as e:
            print(f"❌ Error en La Tercera: {str(e)}")
        finally:
            self.actualizar_progreso()
    
    def buscar_mnba(self):
        """Busca exposiciones en el Museo Nacional de Bellas Artes"""
        print("🔍 Buscando en MNBA...")
        try:
            url = "https://www.mnba.gob.cl/cartelera"
            response = requests.get(url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Múltiples selectores posibles
            eventos = (soup.find_all('div', class_='exposicion') or
                      soup.find_all('article') or
                      soup.find_all('div', class_='evento'))[:10]
            
            for evento in eventos:
                titulo = evento.find('h3') or evento.find('h2') or evento.find('h4')
                link = evento.find('a')
                
                if titulo:
                    href = 'https://www.mnba.gob.cl/cartelera'
                    if link and link.get('href'):
                        href = link.get('href')
                        if not href.startswith('http'):
                            href = 'https://www.mnba.gob.cl' + href
                    
                    self.eventos_gratuitos.append({
                        'titulo': titulo.get_text(strip=True),
                        'fuente': 'MNBA',
                        'fecha': 'Ver cartelera',
                        'precio': 'GRATIS',
                        'link': href
                    })
            
            print(f"✅ Encontradas {len(eventos)} exposiciones en MNBA")
        except Exception as e:
            print(f"❌ Error en MNBA: {str(e)}")
        finally:
            self.actualizar_progreso()
    
    def buscar_mnhn(self):
        """Busca actividades en el Museo Nacional de Historia Natural"""
        print("🔍 Buscando en MNHN...")
        try:
            url = "https://www.mnhn.gob.cl/cartelera"
            response = requests.get(url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            eventos = (soup.find_all('div', class_='evento') or
                      soup.find_all('article'))[:10]
            
            for evento in eventos:
                titulo = evento.find('h3') or evento.find('h2')
                
                if titulo:
                    self.eventos_gratuitos.append({
                        'titulo': titulo.get_text(strip=True),
                        'fuente': 'MNHN',
                        'fecha': 'Ver cartelera',
                        'precio': 'GRATIS',
                        'link': 'https://www.mnhn.gob.cl/cartelera'
                    })
            
            print(f"✅ Encontradas {len(eventos)} actividades en MNHN")
        except Exception as e:
            print(f"❌ Error en MNHN: {str(e)}")
        finally:
            self.actualizar_progreso()
    
    def buscar_mhn(self):
        """Busca actividades en el Museo Histórico Nacional"""
        print("🔍 Buscando en MHN...")
        try:
            url = "https://www.mhn.gob.cl/cartelera"
            response = requests.get(url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            eventos = (soup.find_all('div', class_='actividad') or
                      soup.find_all('article'))[:10]
            
            for evento in eventos:
                titulo = evento.find('h3') or evento.find('h2')
                
                if titulo:
                    self.eventos_gratuitos.append({
                        'titulo': titulo.get_text(strip=True),
                        'fuente': 'MHN',
                        'fecha': 'Ver cartelera',
                        'precio': 'GRATIS',
                        'link': 'https://www.mhn.gob.cl/cartelera'
                    })
            
            print(f"✅ Encontradas {len(eventos)} actividades en MHN")
        except Exception as e:
            print(f"❌ Error en MHN: {str(e)}")
        finally:
            self.actualizar_progreso()
    
    def buscar_santiago_secreto(self):
        """Busca panoramas en Santiago Secreto"""
        print("🔍 Buscando en Santiago Secreto...")
        urls = [
            ("https://santiagosecreto.com/que-hacer/", "Qué hacer"),
            ("https://santiagosecreto.com/guias-secretas/", "Guías secretas"),
            ("https://santiagosecreto.com/cultura/", "Cultura"),
            ("https://santiagosecreto.com/comer-y-beber/", "Comer y beber")
        ]
        
        for url, seccion in urls:
            try:
                response = requests.get(url, headers=self.headers, timeout=15)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                eventos = soup.find_all('article', limit=3)
                
                for evento in eventos:
                    titulo = evento.find('h2') or evento.find('h3')
                    link = evento.find('a')
                    
                    if titulo and link:
                        href = link.get('href', '')
                        if not href.startswith('http'):
                            href = 'https://santiagosecreto.com' + href
                        
                        self.eventos_gratuitos.append({
                            'titulo': titulo.get_text(strip=True),
                            'fuente': f'Santiago Secreto - {seccion}',
                            'fecha': 'Ver artículo',
                            'precio': 'Varía (revisar)',
                            'link': href
                        })
            except Exception as e:
                print(f"  ⚠️ Error en {seccion}: {str(e)}")
        
        print(f"✅ Búsqueda completada en Santiago Secreto")
        self.actualizar_progreso()
    
    def buscar_mavi(self):
        """Busca exposiciones en MAVI UC"""
        print("🔍 Buscando en MAVI UC...")
        try:
            url = "https://mavi.uc.cl/exposiciones-actuales/"
            response = requests.get(url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            eventos = (soup.find_all('div', class_='exposicion') or
                      soup.find_all('article'))[:10]
            
            for evento in eventos:
                titulo = evento.find('h3') or evento.find('h2')
                
                if titulo:
                    self.eventos_gratuitos.append({
                        'titulo': titulo.get_text(strip=True),
                        'fuente': 'MAVI UC',
                        'fecha': 'Ver exposiciones',
                        'precio': 'GRATIS',
                        'link': 'https://mavi.uc.cl/exposiciones-actuales/'
                    })
            
            print(f"✅ Encontradas {len(eventos)} exposiciones en MAVI")
        except Exception as e:
            print(f"❌ Error en MAVI: {str(e)}")
        finally:
            self.actualizar_progreso()
    
    # ============ EVENTOS PAGADOS ============
    
    def buscar_ticketplus(self):
        """Busca eventos pagados en TicketPlus"""
        print("🔍 Buscando en TicketPlus (pagados)...")
        try:
            url = "https://ticketplus.cl/states/region-metropolitana"
            response = requests.get(url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            eventos = (soup.find_all('div', class_='event-item') or
                      soup.find_all('article') or
                      soup.find_all('div', class_='evento'))[:15]
            
            for evento in eventos:
                titulo = evento.find('h3') or evento.find('h2')
                fecha = evento.find('span', class_='date') or evento.find('time')
                link = evento.find('a')
                precio = evento.find('span', class_='price')
                
                if titulo and link:
                    href = link.get('href', '')
                    if not href.startswith('http'):
                        href = 'https://ticketplus.cl' + href
                    
                    self.eventos_pagados.append({
                        'titulo': titulo.get_text(strip=True),
                        'fuente': 'TicketPlus',
                        'fecha': fecha.get_text(strip=True) if fecha else 'Ver fecha',
                        'precio': precio.get_text(strip=True) if precio else 'Ver precio',
                        'link': href
                    })
            
            print(f"✅ Encontrados {len(eventos)} eventos en TicketPlus")
        except Exception as e:
            print(f"❌ Error en TicketPlus: {str(e)}")
        finally:
            self.actualizar_progreso()
    
    def buscar_gam(self):
        """Busca eventos en GAM"""
        print("🔍 Buscando en GAM...")
        try:
            url = "https://gam.cl/calendario/"
            response = requests.get(url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            eventos = (soup.find_all('div', class_='evento') or
                      soup.find_all('article'))[:15]
            
            for evento in eventos:
                titulo = evento.find('h3') or evento.find('h2')
                fecha = evento.find('span', class_='fecha')
                link = evento.find('a')
                
                if titulo:
                    href = 'https://gam.cl/calendario/'
                    if link and link.get('href'):
                        href = link.get('href')
                        if not href.startswith('http'):
                            href = 'https://gam.cl' + href
                    
                    self.eventos_pagados.append({
                        'titulo': titulo.get_text(strip=True),
                        'fuente': 'GAM',
                        'fecha': fecha.get_text(strip=True) if fecha else 'Ver calendario',
                        'precio': 'Ver precio en sitio',
                        'link': href
                    })
            
            print(f"✅ Encontrados {len(eventos)} eventos en GAM")
        except Exception as e:
            print(f"❌ Error en GAM: {str(e)}")
        finally:
            self.actualizar_progreso()
    
    def ejecutar_busqueda_completa(self):
        """Ejecuta todas las búsquedas"""
        self.eventos_gratuitos = []
        self.eventos_pagados = []
        self.progreso = 0
        self.buscando = True
        
        print("\n" + "="*70)
        print("🎭 INICIANDO BÚSQUEDA DE PANORAMAS")
        print("="*70 + "\n")
        
        # Buscar eventos GRATUITOS
        self.buscar_eventbrite_gratis()
        self.buscar_latercera_gratis()
        self.buscar_mnba()
        self.buscar_mnhn()
        self.buscar_mhn()
        self.buscar_santiago_secreto()
        self.buscar_mavi()
        
        # Buscar eventos PAGADOS
        self.buscar_ticketplus()
        self.buscar_gam()
        
        self.buscando = False
        print("\n✅ Búsqueda completada!")
        return {
            'gratuitos': self.eventos_gratuitos,
            'pagados': self.eventos_pagados,
            'total': len(self.eventos_gratuitos) + len(self.eventos_pagados)
        }

# Instancia global del buscador
buscador = BuscadorPanoramasWeb()

@app.route('/')
def index():
    """Sirve el archivo HTML"""
    return send_from_directory('.', 'buscador_panoramas.html')

@app.route('/api/buscar', methods=['POST'])
def buscar():
    """Endpoint para buscar eventos"""
    try:
        data = request.json
        fecha_inicio = data.get('fechaInicio')
        fecha_fin = data.get('fechaFin')
        
        print(f"📅 Buscando eventos del {fecha_inicio} al {fecha_fin}")
        
        # Ejecutar búsqueda en un thread separado para no bloquear
        resultados = buscador.ejecutar_busqueda_completa()
        
        return jsonify({
            'success': True,
            'data': resultados
        })
    except Exception as e:
        print(f"❌ Error en búsqueda: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/progreso', methods=['GET'])
def obtener_progreso():
    """Endpoint para obtener el progreso de la búsqueda"""
    return jsonify({
        'progreso': buscador.progreso,
        'total': buscador.total_fuentes,
        'buscando': buscador.buscando
    })

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 SERVIDOR INICIADO")
    print("="*70)
    print("\n📱 Abre tu navegador en: http://localhost:5001")
    print("⏹️  Presiona Ctrl+C para detener el servidor\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
