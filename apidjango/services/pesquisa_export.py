from ..models import *
from ..serializers import *
from django.http import HttpResponse, JsonResponse
import openpyxl
from datetime import date, datetime
from django.db.models import Model
import json
 
def process_value(value):
    # Se for callable, chama a função
    if callable(value):
        value = value()
        
    # --- CORREÇÃO DE BUG ---
    # Verifica se é datetime.datetime (mais específico) ANTES de verificar Model ou list.
    # O original 'isinstance(value, datetime)' daria True para 'date' e 'datetime',
    # mas 'date' não tem '.tzinfo', o que causaria um erro.
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            value = value.replace(tzinfo=None)
    # Se for uma instância de Model (e não datetime), converte para string
    elif isinstance(value, Model):
        value = str(value)
    # Se for lista ou dict, converte para JSON
    elif isinstance(value, (list, dict)):
        value = json.dumps(value, ensure_ascii=False)
        
    # Deixa 'date', 'int', 'str', 'bool', 'None' passarem,
    # pois o openpyxl lida bem com eles.
    return value

def export_pesquisa_to_excel(request, pesquisa_id):
    try:
        pesquisa = Pesquisa.objects.get(id=pesquisa_id)
    except Pesquisa.DoesNotExist:
        return HttpResponse("Pesquisa não encontrada", status=404)
    
    wb = openpyxl.Workbook()
    
    # ==============================
    # Aba para os dados da Pesquisa
    # ==============================
    dados_sheet_title = f"Dados {date.today().strftime('%d-%m-%Y')}"
    ws_pesquisa = wb.active
    ws_pesquisa.title = dados_sheet_title # Este título é curto, sem problemas

    EXCLUDE_FIELDS = ['id', 'is_active', 'base_ptr', 'pesquisa']
    
    # Campos normais e ManyToMany para Pesquisa (exceto os indesejados)
    pesquisa_field_names = [field.name for field in pesquisa._meta.fields if field.name not in EXCLUDE_FIELDS]
    m2m_field_names = [field.name for field in pesquisa._meta.many_to_many if field.name not in EXCLUDE_FIELDS]
    pesquisa_field_names.extend(m2m_field_names)
    pesquisa_field_names.append("quantidadePesquisadores")
    
    ws_pesquisa.append(pesquisa_field_names)
    
    data_row = []
    for field in pesquisa._meta.fields:
        if field.name in EXCLUDE_FIELDS:
            continue
        value = getattr(pesquisa, field.name)
        data_row.append(process_value(value))
    
    for field_name in m2m_field_names:
        manager = getattr(pesquisa, field_name)
        value = ", ".join(str(obj) for obj in manager.all())
        data_row.append(value)
    
    computed_value = getattr(pesquisa, "quantidadePesquisadores")
    data_row.append(process_value(computed_value))
    
    ws_pesquisa.append(data_row)
    
    # ======================================
    # Abas para os formulários/equipamentos
    # ======================================
    MODEL_SHEET_MAP = [
        (AlimentosEBebidas, "Alimentos e Bebidas"),
        (SistemaDeSeguranca, "Sistemas de Segurança"),
        (Rodovia, "Rodovia"),
        (MeioDeHospedagem, "Meios de Hospedagem"),
        (LocadorasDeImoveis, "Locadoras de Imóveis"),
        (GuiamentoEConducaoTuristica, "Guiamento e Condução Turística"),
        (GastronomiaArtesanato, "Gastronomia e Artesanato"),
        (OutrosMeiosDeHospedagem, "Outros Meios de Hospedagem"),
        (InformacaoBasicaDoMunicipio, "Informações Básicas do Município"),
        (ComercioTuristico, "Comércio Turístico"),
        (AgenciaDeTurismo, "Agência de Turismo"),
        (TransporteTuristico, "Transporte Turístico"),
        (EspacoParaEventos, "Espaço para Eventos"),
        (ServicosParaEventos, "Serviços para Eventos"),
        (Parques, "Parques"),
        (EspacosDeDiversaoECultura, "Espaços de Diversão e Cultura"),
        (InformacoesTuristicas, "Informações Turísticas"),
        (EntidadesAssociativas, "Entidades Associativas"),
        (InstalacoesEsportivas, "Instalações Esportivas"),
        (UnidadesDeConservacao, "Unidades de Conservação"),
        (EventosProgramados, "Eventos Programados"),
    ]

    base_filters = {
        'pesquisa': pesquisa,
        'is_active': True
    }

    sheets = []

    for model_class, sheet_name in MODEL_SHEET_MAP:
        results = list(model_class.objects.filter(**base_filters))

        if results:
            sheets.append((sheet_name, results, model_class))
    
    for sheet_title, results_list, model_class in sheets:
        
        # --- CORREÇÃO DE 31 CARACTERES ---
        # Trunca o título para 31 caracteres para evitar o erro do Excel
        safe_title = sheet_title[:31]
        
        ws = wb.create_sheet(title=safe_title)
        model = model_class
        
        model_field_names = [field.name for field in model._meta.fields if field.name not in EXCLUDE_FIELDS]
        m2m_field_names = [field.name for field in model._meta.many_to_many if field.name not in EXCLUDE_FIELDS]
        all_field_names = model_field_names + m2m_field_names
        ws.append(all_field_names)
        
        for obj in results_list:
            row = []
            # Processa os campos normais
            for field in model._meta.fields:
                if field.name in EXCLUDE_FIELDS:
                    continue
                value = getattr(obj, field.name)
                row.append(process_value(value))
            # Processa os campos ManyToMany
            for field_name in m2m_field_names:
                manager = getattr(obj, field_name)
                if field_name in ["contatos", "servicos_especializados"]:
                    related_values = []
                    for related_obj in manager.all():
                        fields_dict = {
                            f.name: process_value(getattr(related_obj, f.name))
                            for f in related_obj._meta.fields if f.name not in EXCLUDE_FIELDS
                        }
                        related_values.append(fields_dict)
                    value = json.dumps(related_values, ensure_ascii=False)
                else:
                    value = ", ".join(str(related_obj) for related_obj in manager.all())
                row.append(value)
            ws.append(row)
    
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="pesquisa_{pesquisa.id}.xlsx"'
    wb.save(response)
    return response