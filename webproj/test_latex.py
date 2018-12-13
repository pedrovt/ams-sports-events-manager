import os
from pylatex import Document, Section, Subsection, StandAloneGraphic, MultiColumn, Tabu, PageStyle, Head, Foot, MiniPage, LargeText, MediumText, \
    LineBreak, Tabularx, TextColor, simple_page_number, Math
from pylatex.utils import bold, NoEscape, italic

def generate_unique():
    geometry_options = {
        "head": "40pt",
        "margin": "0.5in",
        "bottom": "0.6in",
        "includeheadfoot": True
    }
    doc = Document(geometry_options=geometry_options)

    # Generating first page style
    first_page = PageStyle("firstpage")

    # Event Icon (we can choose if this has one or none)
    # The "L" in Head("L") stands for "Head -> Left"
    with first_page.create(Head("L")) as header_left:
        with header_left.create(MiniPage(width=NoEscape(r"0.19\textwidth"),pos='c')) as logo_wrapper:
            logo_file = os.path.join(os.path.dirname(__file__), 'static/images/logo.png')
            logo_wrapper.append(StandAloneGraphic(image_options="width=60px", filename=logo_file))

    # Document Title, will be altered with the need
    # The "R" in Head("R") stands for "Head -> Right"
    with first_page.create(Head("R")) as right_header:
        with right_header.create(MiniPage(width=NoEscape(r"0.70\textwidth"), pos='c', align='r')) as title_wrapper:
            title_wrapper.append(LargeText(bold("Título ( pode ser inserida uma var para alterar )")))
            title_wrapper.append(LineBreak())
            title_wrapper.append(MediumText(bold("Data")))

    # footer
    with first_page.create(Foot("C")) as footer:
        message = "VIF ( VERY IMPORTANT FOOTER )"
        with footer.create(Tabularx("X X", width_argument=NoEscape(r"\textwidth"))) as footer_table:
            footer_table.add_row([MultiColumn(2, align='c', data=TextColor("red", message))])
            footer_table.add_hline(color="red")

            branch_address = MiniPage(width=NoEscape(r"0.25\textwidth"), pos='t', align='l')
            branch_address.append("Rua das batatas")
            branch_address.append("\n")
            branch_address.append("Lisboa, Benfica")

            document_details = MiniPage(width=NoEscape(r"0.25\textwidth"), pos='t!', align='r')
            document_details.append("2 gaziliões")
            document_details.append(LineBreak())
            document_details.append(simple_page_number())

            footer_table.add_row([branch_address, document_details])

    doc.preamble.append(first_page)
    # End first page style

    # Add event information
    with doc.create(Tabu("X[l] X[r]")) as first_page_table:
        customer = MiniPage(width=NoEscape(r"0.49\textwidth"), pos='h')
        customer.append("Evento: Caça à batata")
        customer.append("\n")
        customer.append("Por alguma razão")
        customer.append("\n")
        customer.append("Mail do criador / team[0]")
        customer.append("\n")
        customer.append("Mail do team[1]")
        customer.append("\n")
        customer.append("Mail do team[2]")

        # More information
        branch = MiniPage(width=NoEscape(r"0.49\textwidth"), pos='t!', align='r')
        branch.append("Mais info??")
        branch.append(LineBreak())
        branch.append(bold("Info a bold"))
        branch.append(LineBreak())

        first_page_table.add_row([customer, branch])
        first_page_table.add_empty_row()

    doc.change_document_style("firstpage")
    doc.add_color(name="lightgray", model="gray", description="0.80")
   

    # Add a section with a subsection
    with doc.create(Section('Uma secção (não sei se é útil ou Não)')):
        doc.append('Texto numa secção')
        doc.append(italic('\nTexto Itálico (porque não?)'))
        with doc.create(Subsection('Uma subsecção')):
            doc.append('Com matemagaitas eheheh')
            doc.append(Math(data=['2*3', '=', 9]))
   
    # Add a numberless section with a subsection
    with doc.create(Section(title='Uma secção sem número (não sei se é útil ou não)', numbering=False)):
        doc.append('Texto numa secção')
        doc.append(italic('\nTexto Itálico (porque não?)'))
        with doc.create(Subsection('Uma subsecção sem número lel', False)):
            doc.append('Com matemagaitas eheheh')
            doc.append(Math(data=['2*3', '=', 9]))
    
    doc.generate_pdf("complex_report", clean_tex=False)

generate_unique()
