import os
from pylatex import Command, Document, Section, Subsection, PageStyle, Head, Foot, MiniPage, LargeText, HugeText, MediumText, LineBreak, TextColor, StandAloneGraphic, Math, NewLine, Itemize
from pylatex.utils import bold, NoEscape, italic
from pylatex.position import Center, VerticalSpace
from pylatex.section import Paragraph

##############################################################
# general stuff
geometry_options = {
    "head": "40pt",
    "margin": "0.5in",
    "bottom": "0.6in",
    "includeheadfoot": True
}

def date_process(date_lst):
    months = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
    start, end = date_lst
    s_y,s_m, s_d = start.split('-')
    e_y, e_m, e_d = end.split('-')
    s_date = s_d + ' de ' + months[int(s_m)-1] + ' de ' + s_y
    e_date = e_d + ' de ' + months[int(e_m)-1] + ' de ' + e_y
    return (s_date,e_date)
    
##############################################################
# security documents
def security_docs(entity_list=None,event=None,icon_path='../static/images/logo.png',admin_name=None,dates=None,place=None):
    doc = Document('basic',geometry_options=geometry_options)
    first_page = PageStyle("firstpage")
    s_date, e_date = date_process(dates)
    
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
    # Title
    doc.change_document_style("firstpage")
    doc.append(VerticalSpace('3cm'))
    with doc.create(Center()):
        with doc.create(Section(title=bold(NoEscape("\LARGE{Segurança}")), numbering=False)):
            with doc.create(Subsection(title=NoEscape('\large{Pedido de Apoio e Cooperação}'), numbering=False)):
                pass

    # body
    with doc.create(Section(title=NoEscape('\\normalsize{Às seguintes entidades:}'), numbering=False)):
        with doc.create(Itemize()) as itemize:
            for entity in entity_list:
                itemize.add_item(entity)
        if e_date==s_date:
            doc.append('Vimos por este meio solicitar a vossa presença, com vista a garantir melhor segurança a todos os participantes do evento '+event+', que se realizará a '+s_date+', em '+place+'.')
        else:
            doc.append('Vimos por este meio solicitar a vossa presença, com vista a garantir melhor segurança a todos os participantes do evento '+event+', que se realizará entre '+s_date+' e '+e_date+', em '+place+'.')
        doc.append('\n\nEsperando contar com a vossa colaboração neste sentido, antecipadamente agradecemos e nos colocamos à disposição para qualquer dúvida.')
    
    # thank you note
    with doc.create(Center()):
        with doc.create(Section(title=NoEscape("\\normalsize{Atenciosamente,}"), numbering=False)):
            with doc.create(Subsection(title=NoEscape('\\normalsize{'+admin_name+'}'), numbering=False)):
                pass

    doc.add_color(name="lightgray", model="gray", description="0.80")
    doc_name='sec_'+event
    gen = doc.generate_pdf(doc_name, clean_tex=True)
    return os.path.join(os.path.dirname(__file__), doc_name+'.pdf')

##############################################################
# health documents
def health_docs(entity_list=None,event=None,icon_path='../static/images/logo.png',admin_name=None,dates=None,place=None):
    doc = Document('basic',geometry_options=geometry_options)
    first_page = PageStyle("firstpage")
    s_date, e_date = date_process(dates)
    
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
    # Title
    doc.change_document_style("firstpage")
    doc.append(VerticalSpace('3cm'))
    with doc.create(Center()):
        with doc.create(Section(title=bold(NoEscape("\LARGE{Saúde}")), numbering=False)):
            with doc.create(Subsection(title=NoEscape('\large{Pedido de Apoio e Cooperação}'), numbering=False)):
                pass

    # body
    with doc.create(Section(title=NoEscape('\\normalsize{Às seguintes entidades:}'), numbering=False)):
        with doc.create(Itemize()) as itemize:
            for entity in entity_list:
                itemize.add_item(entity)
        if e_date==s_date:
            doc.append('Vimos por este meio solicitar a vossa presença, com vista a garantir melhor segurança a todos os participantes do evento '+event+', que se realizará a '+s_date+', em '+place+'.')
        else:
            doc.append('Vimos por este meio solicitar a vossa presença, com vista a garantir melhor segurança a todos os participantes do evento '+event+', que se realizará entre '+s_date+' e '+e_date+', em '+place+'.')
        doc.append('\n\nEsperando contar com a vossa colaboração neste sentido, antecipadamente agradecemos e nos colocamos à disposição para qualquer dúvida.')
    
    # thank you note
    with doc.create(Center()):
        with doc.create(Section(title=NoEscape("\\normalsize{Atenciosamente,}"), numbering=False)):
            with doc.create(Subsection(title=NoEscape('\\normalsize{'+admin_name+'}'), numbering=False)):
                pass

    doc.add_color(name="lightgray", model="gray", description="0.80")
    doc_name='health_'+event
    gen = doc.generate_pdf(doc_name, clean_tex=True)
    return os.path.join(os.path.dirname(__file__), doc_name+'.pdf')

##############################################################
# invitations documents
def invitations_docs(entity=None,event=None,icon_path='../static/images/logo.png',admin_name=None,dates=None,place=None):
    doc = Document('basic',geometry_options=geometry_options)
    first_page = PageStyle("firstpage")
    s_date, e_date = date_process(dates)
    
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
    # Title
    doc.change_document_style("firstpage")
    doc.append(VerticalSpace('3cm'))
    with doc.create(Center()):
        with doc.create(Section(title=bold(NoEscape("\LARGE{Convite}")), numbering=False)):
                pass

    # body
    with doc.create(Section(title=NoEscape('\\normalsize{Caro '+entity+': }'), numbering=False)):
        if e_date==s_date:
            doc.append('Vimos por este meio convidá-lo a participar no evento '+event+', que se realizará a '+s_date+', em '+place+'.')
        else:
            doc.append('Vimos por este meio convidá-lo a participar no evento '+event+', que se realizará entre '+s_date+' e '+e_date+', em '+place+'.')
        doc.append('\n\nEsperando contar com a sua participação neste sentido, antecipadamente agradecemos e nos colocamos à disposição para qualquer dúvida.')
    
    # thank you note
    with doc.create(Center()):
        with doc.create(Section(title=NoEscape("\\normalsize{Atenciosamente,}"), numbering=False)):
            with doc.create(Subsection(title=NoEscape('\\normalsize{'+admin_name+'}'), numbering=False)):
                pass

    doc.add_color(name="lightgray", model="gray", description="0.80")
    doc_name='invitations_'+event
    gen = doc.generate_pdf(doc_name, clean_tex=True)
    return os.path.join(os.path.dirname(__file__), doc_name+'.pdf')

##############################################################
# sponsors documents
def sponsors_docs(entity_list=None,event=None,icon_path='../static/images/logo.png',admin_name=None,dates=None,place=None):
    doc = Document('basic',geometry_options=geometry_options)
    first_page = PageStyle("firstpage")
    s_date, e_date = date_process(dates)
    
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
    # Title
    doc.change_document_style("firstpage")
    doc.append(VerticalSpace('3cm'))
    with doc.create(Center()):
        with doc.create(Section(title=bold(NoEscape("\LARGE{Patrocínio}")), numbering=False)):
            with doc.create(Subsection(title=NoEscape('\large{Pedido de Apoio e Cooperação}'), numbering=False)):
                pass

    # body
    with doc.create(Section(title=NoEscape('\\normalsize{Às seguintes entidades:}'), numbering=False)):
        with doc.create(Itemize()) as itemize:
            for entity in entity_list:
                itemize.add_item(entity)
        if e_date==s_date:
            doc.append('Vimos por este meio solicitar a vosso apoio à realização do evento '+event+', que se realizará a '+s_date+', em '+place+'.')
        else:
            doc.append('Vimos por este meio solicitar a vossa apoio à realização do evento '+event+', que se realizará entre '+s_date+' e '+e_date+', em '+place+'.')
        doc.append('\n\nEsperando contar com a vossa colaboração neste sentido, antecipadamente agradecemos e nos colocamos à disposição para qualquer dúvida.')
    
    # thank you note
    with doc.create(Center()):
        with doc.create(Section(title=NoEscape("\\normalsize{Atenciosamente,}"), numbering=False)):
            with doc.create(Subsection(title=NoEscape('\\normalsize{'+admin_name+'}'), numbering=False)):
                pass

    doc.add_color(name="lightgray", model="gray", description="0.80")
    doc_name='sponsors_'+event
    gen = doc.generate_pdf(doc_name, clean_tex=True)
    return os.path.join(os.path.dirname(__file__), doc_name+'.pdf')
