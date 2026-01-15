from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import os

# Cargar datos desde archivo CSV
def cargar_datos():
    try:
        # En Vercel, los archivos están en la raíz
        df = pd.read_csv('COBROS_RECORDATORIOS_FINAL.csv')
        return df
    except Exception as e:
        print(f"Error cargando datos: {e}")
        return None

class FacturaDiacor(FPDF):
    def header(self):
        # Nota: El logo se puede agregar descargándolo desde la URL si es necesario
        # Por ahora, solo mostramos el encabezado de texto
        
        # Encabezado
        self.set_font('Arial', 'B', 18)
        self.set_text_color(0, 150, 200)
        self.cell(0, 10, 'DIACOR GPS', 0, 1, 'C')
        self.set_text_color(0, 0, 0)
        self.set_font('Arial', '', 9)
        self.cell(0, 4, 'RUC: 2216867-1-775831 DV1', 0, 1, 'C')
        self.cell(0, 4, 'Plaza las Piramides Local 1', 0, 1, 'C')
        self.cell(0, 4, 'Tel: 6471-2589', 0, 1, 'C')
        self.ln(3)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

def generar_factura_pdf(cliente_data):
    """Genera un PDF de factura"""
    pdf = FacturaDiacor()
    pdf.add_page()
    
    # Título
    pdf.set_fill_color(220, 50, 50)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'RECIBO DE COBRO', 0, 1, 'C', True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(3)
    
    # Información
    pdf.set_font('Arial', '', 10)
    fecha_actual = datetime.now().strftime('%d/%m/%Y')
    pdf.cell(0, 6, f'Fecha: {fecha_actual}', 0, 1)
    numero_recibo = f"REC-{datetime.now().strftime('%Y%m%d')}-{cliente_data['Client_ID']}"
    pdf.cell(0, 6, f'Recibo No: {numero_recibo}', 0, 1)
    pdf.cell(0, 6, f'Codigo de Cliente: {int(cliente_data["Client_ID"])}', 0, 1)
    pdf.ln(5)
    
    # Datos del cliente
    pdf.set_fill_color(0, 150, 200)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, 'DATOS DEL CLIENTE', 0, 1, 'L', True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 10)
    nombre_completo = f"{cliente_data['First Name']} {cliente_data['Last Name']}"
    pdf.cell(0, 6, f'Nombre: {nombre_completo}', 0, 1)
    pdf.cell(0, 6, f'Telefono: {cliente_data["Phone"]}', 0, 1)
    pdf.ln(3)
    
    # Tabla de vehículos
    pdf.set_fill_color(0, 150, 200)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, 'DETALLE DE SERVICIOS', 0, 1, 'L', True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)
    
    # Procesar placas
    placas = str(cliente_data['Placas']).split(',')
    placas = [p.strip() for p in placas]
    
    # Encabezados
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(95, 8, 'Placa', 1, 0, 'C', True)
    pdf.cell(95, 8, 'Tarifa Mensual', 1, 1, 'C', True)
    
    # Datos
    pdf.set_font('Arial', '', 10)
    tarifa = float(cliente_data['TARIFA'])
    for placa in placas:
        pdf.cell(95, 8, placa, 1, 0, 'C')
        pdf.cell(95, 8, f'${tarifa:.2f}', 1, 1, 'C')
    
    # Resumen
    pdf.ln(5)
    meses_debe = int(cliente_data['Numero de meses que debe'])
    meses_texto = str(cliente_data['Meses que debe'])
    
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(95, 8, 'Deuda:', 0, 0, 'R')
    pdf.set_font('Arial', '', 11)
    pdf.cell(95, 8, f'{meses_debe} meses ({meses_texto})', 0, 1, 'L')
    
    # Total
    total = float(cliente_data['Total a pagar'])
    pdf.set_fill_color(220, 50, 50)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(95, 12, 'TOTAL A PAGAR:', 1, 0, 'R', True)
    pdf.cell(95, 12, f'${total:.2f}', 1, 1, 'C', True)
    pdf.set_text_color(0, 0, 0)
    
    # Métodos de pago
    pdf.ln(8)
    pdf.set_fill_color(0, 150, 200)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, 'METODOS DE PAGO', 0, 1, 'L', True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 6, 'Yappy: 6471-2579', 0, 1)
    pdf.cell(0, 6, 'Banco General - Cuenta de Ahorros', 0, 1)
    pdf.cell(0, 6, 'N° 0421980210994', 0, 1)
    pdf.cell(0, 6, 'A nombre de: CESAR AUGUSTO DIAZ CORTEZ', 0, 1)
    
    pdf.ln(5)
    pdf.set_font('Arial', 'I', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 5, 'Por favor, realice su pago a la brevedad posible para mantener su servicio activo.\nSi ya realizo el pago, favor de ignorar este mensaje.')
    
    return pdf

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        params = parse_qs(parsed_path.query)
        client_id = params.get('client_id', [None])[0]
        
        if not client_id:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"error": "Client ID requerido"}')
            return
        
        try:
            client_id = int(client_id)
            datos = cargar_datos()
            
            if datos is None:
                raise Exception("No se pudieron cargar los datos")
            
            cliente = datos[datos['Client_ID'] == client_id]
            
            if cliente.empty:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"error": "Cliente no encontrado"}')
                return
            
            # Generar PDF
            cliente_data = cliente.iloc[0]
            pdf = generar_factura_pdf(cliente_data)
            
            # Enviar PDF
            pdf_output = pdf.output(dest='S').encode('latin1')
            self.send_response(200)
            self.send_header('Content-type', 'application/pdf')
            self.send_header('Content-Disposition', f'attachment; filename="Factura_Diacor_{client_id}.pdf"')
            self.send_header('Content-Length', str(len(pdf_output)))
            self.end_headers()
            self.wfile.write(pdf_output)
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_msg = f'{{"error": "{str(e)}"}}'
            self.wfile.write(error_msg.encode())
