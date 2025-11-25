from django.contrib import admin
from .models import *
 
class CustomUserAdmin(admin.ModelAdmin):
    ordering = ['id']

    list_display = ['id', 'username', 'CPF','telefone', 'acessLevel', 'status','email', 'display_pesquisas', 'is_active']

    def display_pesquisas(self, obj):
        # Exibe as pesquisas associadas ao usuário como uma string
        return ", ".join(str(pesquisa.id) for pesquisa in obj.pesquisas.all())
    display_pesquisas.short_description = "Pesquisas"
admin.site.register(CustomUser, CustomUserAdmin)

class ContatoInfoAdmin(admin.ModelAdmin):
    ordering = ['id']
    list_display = ['id', 'nome', 'endereco', 'whatsapp', 'email']
    search_fields = ['nome', 'email', 'whatsapp']
    list_filter = ['endereco']

class ServicoEspecializadoInfoAdmin(admin.ModelAdmin):
    ordering = ['id']
    list_display = ['id', 'email', 'servicos_especializados', 'outras_informacoes']
    search_fields = ['email', 'servicos_especializados']
    list_filter = ['email']

class SistemaDeSegurancaAdmin(admin.ModelAdmin):
    ordering = ['id']
    list_display = [
        'id', 'display_pesquisas', 'get_contatos_ids', 'get_servicos_ids',
        'tipo_formulario', 'uf', 'regiao_turistica', 'municipio',
        'tipo', 'observacoes', 'referencias',
        'nome_pesquisador', 'telefone_pesquisador', 'email_pesquisador',
        'nome_coordenador', 'telefone_coordenador', 'email_coordenador'
    ]
    def display_pesquisas(self, obj):
        # Exibe as pesquisas associadas ao usuário como uma string
        return str(obj.pesquisa.id) if obj.pesquisa else "Nenhuma pesquisa associada"
    display_pesquisas.short_description = "Pesquisa"    

    @admin.display(description='Contatos (IDs)')
    def get_contatos_ids(self, obj):
        return ", ".join(str(c.id) for c in obj.contatos.all())

    @admin.display(description='Serviços Especializados (IDs)')
    def get_servicos_ids(self, obj):
        return ", ".join(str(s.id) for s in obj.servicos_especializados.all())

# Registering models
admin.site.register(SistemaDeSeguranca, SistemaDeSegurancaAdmin)
admin.site.register(ContatoInfo, ContatoInfoAdmin)
admin.site.register(ServicoEspecializadoInfo, ServicoEspecializadoInfoAdmin)


class RodoviaAdmin(admin.ModelAdmin):
    ordering = ['id']
    list_display = [
        'id', 'display_pesquisas','tipo_formulario', 'uf', 'regiao_turistica', 'municipio',
        'tipo', 'subtipos', 'nome_oficial', 'nome_popular', 
        'jurisdicao', 'natureza', 'tipo_de_organizacao_instituicao', 
        'extensao_rodovia_municipio', 'faixas_de_rolamento', 'pavimentacao', 
        'pedagio', 'municipios_vizinhos_interligados_rodovia', 
        'inicio_atividade', 'whatsapp', 'instagram', 
        'sinalizacao_de_acesso', 'sinalizacao_turistica', 
        'posto_de_combustivel', 'outros_servicos', 'estruturas_ao_longo_da_via', 
        'poluicao', 'poluicao_especificacao', 'lixo', 'lixo_especificacao', 
        'desmatamento', 'desmatamento_especificacao', 'queimadas', 'queimadas_especificacao', 
        'inseguranca', 'inseguranca_especificacao', 'extrativismo', 'extrativismo_especificacao', 
        'prostituicao', 'prostituicao_especificacao', 'ocupacao_irregular_invasao', 
        'ocupacao_irregular_invasao_especificacao', 'outras', 'outras_especificacao', 
        'estado_geral_de_conservacao', 'observacoes', 'referencias', 
        'nome_pesquisador', 'telefone_pesquisador', 'email_pesquisador', 
        'nome_coordenador', 'telefone_coordenador', 'email_coordenador'
    ]
    search_fields = ['nome_oficial', 'municipio', 'uf']
    list_filter = ['jurisdicao', 'natureza', 'estado_geral_de_conservacao']

    def display_pesquisas(self, obj):
        # Exibe as pesquisas associadas ao usuário como uma string
        return str(obj.pesquisa.id) if obj.pesquisa else "Nenhuma pesquisa associada"
    display_pesquisas.short_description = "Pesquisa" 
admin.site.register(Rodovia, RodoviaAdmin)




@admin.register(AlimentosEBebidas)
class AlimentosEBebidasAdmin(admin.ModelAdmin):
    list_display = [field.name for field in AlimentosEBebidas._meta.fields]
    
    fieldsets = (
        ("Dados Gerais", {
            "fields": (
                "pesquisa",
                "is_active",
                "tipo_formulario",
                "uf",
                "regiao_turistica",
                "municipio",
                "tipo",
                "observacoes",
                "referencias",
            )
        }),
        ("Responsáveis", {
            "classes": ("collapse",),
            "fields": (
                "nome_pesquisador",
                "telefone_pesquisador",
                "email_pesquisador",
                "nome_coordenador",
                "telefone_coordenador",
                "email_coordenador",
            )
        }),
        ("Dados da Empresa", {
            "fields": (
                "razaoSocial",
                "nomeFantasia",
                "CNPJ",
                "codigoCNAE",
                "atividadeEconomica",
                "inscricaoMunicipal",
                "nomeDaRede",
                "natureza",
                "tipoDeOrganizacaoInstituicao",
                "inicioDaAtividade",
            )
        }),
        ("Funcionários", {
            "classes": ("collapse",),
            "fields": (
                "qtdeFuncionariosPermanentes",
                "qtdeFuncionariosTemporarios",
                "qtdeFuncionariosComDeficiencia",
            )
        }),
        ("Localização", {
            "fields": (
                "localizacao",
                "latitude",
                "longitude",
                "avenidaRuaEtc",
                "bairroLocalidade",
                "distrito",
                "CEP",
            )
        }),
        ("Contatos", {
            "fields": (
                "whatsapp",
                "instagram",
                "email",
                "sinalizacaoDeAcesso",
                "sinalizacaoTuristica",
            )
        }),
        ("Proximidades e Distâncias", {
            "classes": ("collapse",),
            "fields": (
                "proximidades",
                "distanciasAeroporto",
                "distanciasRodoviaria",
                "distanciaEstacaoFerroviaria",
                "distanciaEstacaoMaritima",
                "distanciaEstacaoMetroviaria",
                "distanciaPontoDeOnibus",
                "distanciaPontoDeTaxi",
                "distanciasOutraNome",
                "distanciaOutras",
                "pontosDeReferencia",
            )
        }),
        ("Pagamentos e Horários", {
            "classes": ("collapse",),
            "fields": (
                "tabelaMTUR",
                "formasDePagamento",
                "vendasEReservas",
                "atendimentoEmLinguasEstrangeiras",
                "informativosImpressos",
                "periodo",
                "tabelasHorario",
                "funcionamento24h",
                "funcionamentoEmFeriados",
            )
        }),
        ("Restrições e Informações Adicionais", {
            "classes": ("collapse",),
            "fields": (
                "restricoes",
                "outrasRegraseInformacoes",
            )
        }),
        ("Capacidades", {
            "classes": ("collapse",),
            "fields": (
                "capInstaladaPdia",
                "capInstaladasSentadas",
                "capSimultanea",
                "capSimultaneaSentadas",
            )
        }),
        ("Estacionamento e Veículos", {
            "classes": ("collapse",),
            "fields": (
                "estacionamento",
                "capacidadeVeiculos",
                "numeroAutomoveis",
                "numeroOnibus",
            )
        }),
        ("Serviços e Equipamentos", {
            "classes": ("collapse",),
            "fields": (
                "servicosEEquipamentos",
                "especificacaoDaGastronomiaPorPais",
                "seForBrasileiraPorRegiao",
                "porEspecializacao",
                "porTipoDeDieta",
                "porTipoDeServico",
            )
        }),
        ("Equipamento", {
            "classes": ("collapse",),
            "fields": (
                "doEquipamento",
                "tabelaEquipamentoEEspaco",
                "estadoGeralDeConservacao",
                "possuiFacilidade",
            )
        }),
        ("Acessibilidade", {
            "classes": ("collapse",),
            "fields": (
                "pessoalCapacitadoParaReceberPCD",
                "rotaExternaAcessível",
                "simboloInternacionalDeAcesso",
                "localDeEmbarqueEDesembarque",
                "vagaEmEstacionamento",
                "areaDeCirculacaoAcessoInternoParaCadeiraDeRodas",
                "escada",
                "rampa",
                "piso",
                "elevador",
                "equipamentoMotorizadoParaDeslocamentoInterno",
                "sinalizacaoVisual",
                "sinalizacaoTatil",
                "alarmeDeEmergencia",
                "comunicacao",
                "balcaoDeAtendimento",
                "mobiliario",
                "sanitario",
                "telefone",
                "sinalizacaoIndicativa",
                "outrosAcessibilidade",
            )
        }),
    )


class PesquisasAdmin(admin.ModelAdmin):
    ordering = ['id']

    list_display = ['id', 'dataInicio', 'dataTermino', 'admin', 'codigoIBGE', 'estado', 'municipio', 'display_usuario', 'admin_telefone', 'admin_email']

    def display_usuario(self, obj):
        return ", ".join(str(user) for user in obj.usuario.all())
    display_usuario.short_description = "Usuário"

admin.site.register(Pesquisa, PesquisasAdmin)


@admin.register(MeioDeHospedagem)
class MeiosDeHospedagemAdmin(admin.ModelAdmin):
    list_display = (
        "pesquisa",
        "tipo_formulario",
        "nome_pesquisador",
        "telefone_pesquisador",
        "email_pesquisador",
        "nome_coordenador",
        "telefone_coordenador",
        "email_coordenador",
        "sinalizacaoDeAcesso",
        "sinalizacaoTuristica",
        "funcionamento24h",
        "funcionamentoEmFeriados",
        "geradorDeEmergencia",
        "doEquipamentoEspaco",
        "daAreaOuEdificacaoEmQueEstaLocalizado",
        "possuiFacilidade",
        "sinalizacaoIndicativa",
        "tipoDeOrganizacao",
        "proximidades",
        "segmentosOuTurismoEspecializado",
        "formasDePagamento",
        "reservas",
        "atendimentoEmLinguaEstrangeira",
        "informativosImpressos",
        "restricoes",
        "mesesAltaTemporada",
        "origemDosVisitantes",
        "produtosHigienePessoal",
        "equipamentosEServicos",
        "estacionamento",
        "restaurante",
        "lanchonete",
        "instalacaoEEspacos",
        "outrosEspacosEAtividades",
        "servicos",
        "equipamentos",
        "facilidadesEServicos",
        "facilidadesParaExecutivos",
        "pessoalCapacitadoParaReceberPCD",
        "rotaExternaAcessivel",
        "simboloInternacionalDeAcesso",
        "localDeEmbarqueEDesembarque",
        "vagaEmEstacionamento",
        "areaDeCirculacaoAcessoInterno",
        "escada",
        "rampa",
        "piso",
        "elevador",
        "equipamentoMotorizadoParaDeslocamentoInterno",
        "sinalizacaoVisual",
        "sinalizacaoTatil",
        "alarmeDeEmergencia",
        "comunicacao",
        "balcaoDeAtendimento",
        "mobiliario",
        "sanitario",
        "telefone",
        "subtipo",
        "natureza",
        "localizacao",
        "tipoDeDiaria",
        "periodo",
        "tabelasHorario",
        "energiaEletrica",
        "estadoGeralDeConservacao",
        "estadosTuristas",
        "paisesTuristas",
        "uf",
        "regiao_turistica",
        "municipio",
        "razaoSocial",
        "nomeFantasia",
        "codigoCNAE",
        "atividadeEconomica",
        "inscricaoMunicipal",
        "nomeDaRede",
        "CNPJ",
        "inicioDaAtividade",
        "qtdeFuncionariosPermanentes",
        "qtdeFuncionariosTemporarios",
        "qtdeFuncionarisComDeficiencia",
        "latitude",
        "longitude",
        "avenidaRuaEtc",
        "bairroLocalidade",
        "distrito",
        "CEP",
        "whatsapp",
        "instagram",
        "email",
        "site",
        "pontosDeReferencia",
        "tabelaMTUR",
        "outrasRegrasEInformacoes",
        "nAnoOcupacao",
        "nOcupacaoAltaTemporada",
        "nTotalDeUH",
        "nTotalDeLeitos",
        "nUhAdaptadasParaPCD",
        "nCapacidadeDeVeiculos",
        "nAutomoveis",
        "nOnibus",
        "capacidadeEmKVA",
        "geradorCapacidadeEmKVA",
        "nCapacidadeInstaladaPorDia",
        "nPessoasAtendidasSentadas",
        "nCapacidadeSimultanea",
        "nPessoasAtendidasSentadasSimultanea",
        "lanchoneteCapacidadeInstaladaPorDia",
        "lanchoneteCapacidadePessoasAtendidasSentadas",
        "lanchoneteCapacidadeSimultanea",
        "lanchoneteCapacidadeSentadasSimultanea",
        "tabelaInstalacoes",
        "tabelaEquipamentoEEspaco",
        "tabelaEquipamentoEEspaco2",
        "outros",
        "observacoes",
        "referencias",
    )

    fieldsets = (
        ("Dados do formulário e pesquisador", {
            "fields": (
                "tipo_formulario",
                "nome_pesquisador",
                "telefone_pesquisador",
                "email_pesquisador",
            ),
        }),
        ("Dados do coordenador", {
            "fields": (
                "nome_coordenador",
                "telefone_coordenador",
                "email_coordenador",
            ),
        }),
        ("Sinalizações e funcionamento", {
            "fields": (
                "sinalizacaoDeAcesso",
                "sinalizacaoTuristica",
                "funcionamento24h",
                "funcionamentoEmFeriados",
                "geradorDeEmergencia",
            ),
        }),
        ("Infraestrutura e localização do equipamento/edificação", {
            "fields": (
                "doEquipamentoEspaco",
                "daAreaOuEdificacaoEmQueEstaLocalizado",
                "possuiFacilidade",
                "sinalizacaoIndicativa",
                "tipoDeOrganizacao",
                "proximidades",
            ),
        }),
        ("Dados relacionados ao turismo e pagamentos", {
            "fields": (
                "segmentosOuTurismoEspecializado",
                "formasDePagamento",
                "reservas",
                "atendimentoEmLinguaEstrangeira",
                "informativosImpressos",
                "restricoes",
                "mesesAltaTemporada",
                "origemDosVisitantes",
            ),
        }),
        ("Produtos e serviços", {
            "fields": (
                "produtosHigienePessoal",
                "equipamentosEServicos",
                "estacionamento",
                "restaurante",
                "lanchonete",
                "instalacaoEEspacos",
                "outrosEspacosEAtividades",
                "servicos",
                "equipamentos",
                "facilidadesEServicos",
                "facilidadesParaExecutivos",
                "pessoalCapacitadoParaReceberPCD",
            ),
        }),
        ("Acessibilidade", {
            "fields": (
                "rotaExternaAcessivel",
                "simboloInternacionalDeAcesso",
                "localDeEmbarqueEDesembarque",
                "vagaEmEstacionamento",
                "areaDeCirculacaoAcessoInterno",
                "escada",
                "rampa",
                "piso",
                "elevador",
                "equipamentoMotorizadoParaDeslocamentoInterno",
                "sinalizacaoVisual",
                "sinalizacaoTatil",
                "alarmeDeEmergencia",
                "comunicacao",
                "balcaoDeAtendimento",
                "mobiliario",
                "sanitario",
                "telefone",
            ),
        }),
        ("Classificação e localização do meio de hospedagem", {
            "fields": (
                "subtipo",
                "natureza",
                "localizacao",
                "tipoDeDiaria",
                "periodo",
                "tabelasHorario",
                "energiaEletrica",
                "estadoGeralDeConservacao",
            ),
        }),
        ("Dados de turismo e localização geográfica", {
            "fields": (
                "estadosTuristas",
                "paisesTuristas",
                "uf",
                "regiao_turistica",
                "municipio",
            ),
        }),
        ("Dados empresariais", {
            "fields": (
                "razaoSocial",
                "nomeFantasia",
                "codigoCNAE",
                "atividadeEconomica",
                "inscricaoMunicipal",
                "nomeDaRede",
                "CNPJ",
                "inicioDaAtividade",
            ),
        }),
        ("Dados de quantitativos e capacidade", {
            "fields": (
                "qtdeFuncionariosPermanentes",
                "qtdeFuncionariosTemporarios",
                "qtdeFuncionarisComDeficiencia",
                "latitude",
                "longitute",
            ),
        }),
        ("Endereço e contato", {
            "fields": (
                "avenidaRuaEtc",
                "bairroLocalidade",
                "distrito",
                "CEP",
                "whatsapp",
                "instagram",
                "email",
                "site",
                "pontosDeReferencia",
            ),
        }),
        ("Dados de tabelas e informações adicionais", {
            "fields": (
                "tabelaMTUR",
                "outrasRegrasEInformacoes",
                "nAnoOcupacao",
                "nOcupacaoAltaTemporada",
                "nTotalDeUH",
                "nTotalDeLeitos",
                "nUhAdaptadasParaPCD",
                "nCapacidadeDeVeiculos",
                "nAutomoveis",
                "nOnibus",
                "capacidadeEmKVA",
                "geradorCapacidadeEmKVA",
                "nCapacidadeInstaladaPorDia",
                "nPessoasAtendidasSentadas",
                "nCapacidadeSimultanea",
                "nPessoasAtendidasSentadasSimultanea",
                "lanchoneteCapacidadeInstaladaPorDia",
                "lanchoneteCapacidadePessoasAtendidasSentadas",
                "lanchoneteCapacidadeSimultanea",
                "lanchoneteCapacidadeSentadasSimultanea",
            ),
        }),
        ("Tabelas de instalações e equipamentos/espaços", {
            "fields": (
                "tabelaInstalacoes",
                "tabelaEquipamentoEEspaco",
                "tabelaEquipamentoEEspaco2",
            ),
        }),
        ("Observações e referências", {
            "fields": (
                "outros",
                "observacoes",
                "referencias",
            ),
        }),
    )

@admin.register(InformacaoBasicaDoMunicipio)
class InfoBasicaAdmin(admin.ModelAdmin):
    list_display = [field.name for field in InformacaoBasicaDoMunicipio._meta.fields]

@admin.register(ComercioTuristico)
class ComercioTuristicoAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ComercioTuristico._meta.fields]

@admin.register(LocadorasDeImoveis)
class LocadorasDeImoveisAdmin(admin.ModelAdmin):
    list_display = [field.name for field in LocadorasDeImoveis._meta.fields]


@admin.register(InfoGerais)
class InfoGeraisAdmin(admin.ModelAdmin):
    list_display = [field.name for field in InfoGerais._meta.fields]

@admin.register(EnderecoInfo)
class EnderecoInfoAdmin(admin.ModelAdmin):
    list_display = [field.name for field in EnderecoInfo._meta.fields]

@admin.register(OutrosMeiosDeHospedagem)
class OutrosMeiosDeHospedagemAdmin(admin.ModelAdmin):
    list_display = [field.name for field in OutrosMeiosDeHospedagem._meta.fields]

@admin.register(AgenciaDeTurismo)
class AgenciaDeTurismoAdmin(admin.ModelAdmin):
    list_display = [field.name for field in AgenciaDeTurismo._meta.fields]
    

@admin.register(EspacoParaEventos)
class EspacoParaEventosAdmin(admin.ModelAdmin):
    list_display = [field.name for field in EspacoParaEventos._meta.fields]

@admin.register(Parques)
class ParquesAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Parques._meta.fields]

@admin.register(GuiamentoEConducaoTuristica)
class GuiamentoEConducaoTuristicaAdmin(admin.ModelAdmin):
    list_display = [field.name for field in GuiamentoEConducaoTuristica._meta.fields]

@admin.register(InformacoesGuiamento)
class InformacoesGuiamentoAdmin(admin.ModelAdmin):
    list_display = [field.name for field in InformacoesGuiamento._meta.fields]
@admin.register(InformacoesGuiamentoCadastur)
class InformacoesGuiamentoCadasturAdmin(admin.ModelAdmin):
    list_display = [field.name for field in InformacoesGuiamentoCadastur._meta.fields]
    
@admin.register(EspacosDeDiversaoECultura)
class EspacosDeDiversaoECulturaAdmin(admin.ModelAdmin):
    list_display = [field.name for field in EspacosDeDiversaoECultura._meta.fields]  
    
@admin.register(InstalacoesEsportivas)
class InstalacoesEsportivasAdmin(admin.ModelAdmin):
    list_display = [field.name for field in InstalacoesEsportivas._meta.fields]  

@admin.register(InformacoesTuristicas)
class InformacoesTuristicasAdmin(admin.ModelAdmin):
    list_display = [field.name for field in InformacoesTuristicas._meta.fields]  
    
@admin.register(EntidadesAssociativas)
class EntidadesAssociativasAdmin(admin.ModelAdmin):
    list_display = [field.name for field in EntidadesAssociativas._meta.fields]  

@admin.register(UnidadesDeConservacao)
class UnidadesDeConservacaoAdmin(admin.ModelAdmin):
    list_display = [field.name for field in UnidadesDeConservacao._meta.fields]  

@admin.register(EventosProgramados)
class EventosProgramadosAdmin(admin.ModelAdmin):
    list_display = [field.name for field in EventosProgramados._meta.fields] 
    
@admin.register(GastronomiaArtesanato)
class GastronomiaArtesanatoAdmin(admin.ModelAdmin):
    list_display = [field.name for field in GastronomiaArtesanato._meta.fields] 