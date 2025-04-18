from fpdf import FPDF

def text_to_pdf(input_file, output_file):
    # Read the text file
    with open(input_file, 'r') as f:
        text = f.read()
    
    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Split text into lines and add to PDF
    lines = text.split('\n')
    for line in lines:
        # Check if line is a heading
        if line.strip() and not line.startswith('-') and not line.startswith(' '):
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, txt=line, ln=True)
            pdf.set_font("Arial", size=12)
        else:
            pdf.cell(0, 10, txt=line, ln=True)
    
    # Save PDF
    pdf.output(output_file)
    
    print(f"PDF created at {output_file}")

if __name__ == "__main__":
    text_to_pdf("documents/delivery_driver_faq.txt", "documents/delivery_driver_faq.pdf")