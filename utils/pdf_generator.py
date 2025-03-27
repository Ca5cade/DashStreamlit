import base64
import io
import plotly.io as pio
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from dash import html
import re
import traceback
from datetime import datetime

def generate_pdf(graphs):
    """
    Generate a PDF report from Dash graphs
    
    Args:
        graphs: List of graph components from Dash
        
    Returns:
        dict with filename and content for Dash download component
    """
    try:
        # Create a BytesIO buffer to save the PDF to
        buffer = io.BytesIO()
        
        # Setup the PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        # Get styles for document
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        heading_style = styles['Heading2']
        normal_style = styles['Normal']
        
        # Create custom styles
        caption_style = ParagraphStyle(
            'Caption',
            parent=styles['Normal'],
            fontSize=9,
            leading=11,
            textColor=colors.grey
        )
        
        # Content elements
        elements = []
        
        # Add report title
        elements.append(Paragraph("Analytics Report", title_style))
        elements.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", caption_style))
        elements.append(Spacer(1, 0.25*inch))
        
        # Add summary information
        elements.append(Paragraph("Report Summary", heading_style))
        elements.append(Paragraph("This report contains analytical visualizations generated from the data.", normal_style))
        elements.append(Paragraph(f"Number of visualizations: {len(graphs)}", normal_style))
        elements.append(Spacer(1, 0.25*inch))
        
        # Process and add each graph
        for i, graph_div in enumerate(graphs):
            # Regex pattern to extract the id string
            pattern = r'{"type":"report-graph","index":\s*(\d+)}'
            
            # If this is a Dash component and has a dcc.Graph
            if hasattr(graph_div, 'children') and len(graph_div.children) > 0:
                graph = graph_div.children[0]
                
                # Check if it's a graph component with a figure
                if hasattr(graph, 'figure') and graph.figure is not None:
                    # Add section title
                    elements.append(Paragraph(f"Visualization {i+1}", heading_style))
                    
                    # Extract title from figure
                    title = graph.figure.get('layout', {}).get('title', {}).get('text', f"Graph {i+1}")
                    if title:
                        elements.append(Paragraph(title, normal_style))
                    
                    # Create a PNG image from the figure
                    try:
                        img_bytes = pio.to_image(graph.figure, format="png", width=650, height=450, scale=2)
                        img = Image(io.BytesIO(img_bytes))
                        img.drawHeight = 4.5*inch
                        img.drawWidth = 6.5*inch
                        elements.append(img)
                    except Exception as e:
                        elements.append(Paragraph(f"Error rendering graph: {str(e)}", normal_style))
                    
                    elements.append(Spacer(1, 0.25*inch))
                    
                    # Add page break after each graph except the last one
                    if i < len(graphs) - 1:
                        elements.append(PageBreak())
            
        # Build the PDF
        doc.build(elements)
        
        # Get the PDF data
        buffer.seek(0)
        
        # Return the data for download
        return {
            'content': base64.b64encode(buffer.getvalue()).decode('utf-8'),
            'filename': f'analytics_report_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf',
            'type': 'base64'
        }
        
    except Exception as e:
        print("Error generating PDF:")
        print(traceback.format_exc())
        return None
