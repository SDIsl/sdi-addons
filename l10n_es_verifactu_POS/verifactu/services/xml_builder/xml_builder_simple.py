# Desarrollado por Juan Ormaechea (Mr. Rubik) — Todos los derechos reservados
# Este módulo está protegido por la Odoo Proprietary License v1.0
# Cualquier redistribución está prohibida sin autorización expresa.

from xml.dom import minidom
from xml.etree import ElementTree as ET


class VerifactuSimpleXMLBuilder:
    def __init__(self, invoice):
        self.invoice = invoice

    def build(self):
        """
        Genera un XML simplificado con los campos básicos de la factura.
        """
        self.invoice.ensure_one()

        root = ET.Element("Factura")
        ET.SubElement(root, "Numero").text = self.invoice.number or ""
        ET.SubElement(root, "Cliente").text = self.invoice.partner_id.name or ""
        ET.SubElement(root, "Fecha").text = str(self.invoice.date_invoice or "")
        ET.SubElement(root, "Total").text = str(self.invoice.amount_total or "0.0")
        ET.SubElement(root, "Hash").text = self.invoice.verifactu_hash or ""
        ET.SubElement(root, "HashAnterior").text = self.invoice.verifactu_previous_hash or ""

        lineas_xml = ET.SubElement(root, "Lineas")
        for line in self.invoice.invoice_line_ids:
            linea = ET.SubElement(lineas_xml, "Linea")
            ET.SubElement(linea, "Producto").text = (
                line.product_id.display_name or line.name or ""
            )
            ET.SubElement(linea, "Cantidad").text = str(line.quantity or "0.0")
            ET.SubElement(linea, "Precio").text = str(line.price_unit or "0.0")

        rough_string = ET.tostring(root, "utf-8")
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
