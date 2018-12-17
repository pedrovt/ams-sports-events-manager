import os
from pylatex import Command, Document, Section, Subsection, PageStyle, Head, Foot, MiniPage, LargeText, HugeText, MediumText, LineBreak, TextColor, StandAloneGraphic, Math, NewLine
from pylatex.utils import bold, NoEscape, italic
from pylatex.position import Center

##############################################################
# general stuff
geometry_options = {
    "head": "40pt",
    "margin": "0.5in",
    "bottom": "0.6in",
    "includeheadfoot": True
}

doc = Document('basic',geometry_options=geometry_options)
first_page = PageStyle("firstpage")

def security_docs(authority=None,event=None,icon_path='static/images/logo.png',admin_name=None):
    # preamble stuff
    # Top Left Corner
    with first_page.create(Head("L")) as header_left:
        with header_left.create(MiniPage(width=NoEscape(r"0.30\textwidth"),pos='c')) as logo_wrapper:
            logo_file = os.path.join(os.path.dirname(__file__), icon_path)
            logo_wrapper.append(StandAloneGraphic(image_options="width=100px", filename=logo_file))
    
    # Top Center 
    with first_page.create(Head("C")) as right_header:
        with right_header.create(MiniPage(width=NoEscape(r"\textwidth"), pos='r', align='c')) as title_wrapper:
            title_wrapper.append(HugeText(bold(event)))
   

    doc.preamble.append(first_page)
    
    # body stuff
    doc.change_document_style("firstpage")
    doc.append(LargeText(bold(NoEscape('\centerline{Segurança}'))))
    with doc.create(Section(title='Secção sem número (não sei se é útil ou não)', numbering=False)):
        doc.append('Texto numa secção')
        doc.append(italic('\nTexto Itálico (porque não?)'))
        with doc.create(Subsection('Uma subsecção sem número lel', False)):
            doc.append('Com matemagaitas eheheh')
            doc.append(Math(data=['2*3', '=', 9]))
    doc.add_color(name="lightgray", model="gray", description="0.80")
    doc.generate_pdf("sec_doc_"+str(event), clean_tex=False)


def health_docs(authority=None,event=None,icon_path='static/images/logo.png',admin_name=None):
    pass

def invitations_docs(authority=None,event=None,icon_path='static/images/logo.png',admin_name=None):
    pass

def sponsors_docs(authority=None,event=None,icon_path='static/images/logo.png',admin_name=None):
    pass

security_docs(event="Event Name")
