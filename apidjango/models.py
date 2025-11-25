from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
import uuid 
from django.utils import timezone
from datetime import timedelta 
from django.core.mail import send_mail, EmailMessage
import random
from datetime import timedelta
from django.utils import timezone



def validate_cpf(cpf):
    cpf = ''.join(filter(str.isdigit, cpf))

    if len(cpf) != 11:
        raise ValidationError("O CPF deve ter 11 digítos")
    
    if cpf == cpf[0] * len(cpf):
        raise ValidationError("O CPF não pode ter todos os dígitos iguais")

    def calcular_digito(cpf, peso):
        soma = sum(int(d) * peso for d, peso in zip(cpf[:-2], range(peso, 1, -1)))
        resto = 11 - (soma % 11)
        return '0' if resto >= 10 else str(resto)
    
    digito1 = calcular_digito(cpf, 10)
    digito2 = calcular_digito(cpf + digito1, 11)

    if cpf[-2:] != digito1 + digito2:
        raise ValidationError("O CPF é inválido")
    
class CustomUser(AbstractUser):

    pesquisas = models.ManyToManyField("Pesquisa", related_name="pesquisas", blank=True, null=True)
    email = models.EmailField(unique=True)
    CPF = models.CharField(max_length=11, unique=True)
    username = models.CharField(
        max_length = 150,
        unique=False,
         validators=[
            RegexValidator(
                regex=r'^[\w\sáéíóúãõâêîôûçÁÉÍÓÚÃÕÂÊÎÔÛÇ]+$',
                message="O nome de usuário pode conter letras, números e espaços."
            )
        ],
    )

    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_exp = models.DateTimeField(blank=True, null=True)
    otp_verified = models.BooleanField(default=False)

    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.otp_exp = timezone.now() + timedelta(minutes=10)
        self.otp_verified = False
        self.save()

    acessLevel = models.CharField(max_length=22, default='Pesquisador');
    status = models.CharField(max_length=50, default='Ativo');
    telefone = models.CharField(max_length=25);
    def clean(self):
        super().clean()
        validate_cpf(self.CPF)
# Create your models here.
class Pesquisa(models.Model):

    usuario = models.ManyToManyField("CustomUser", related_name="usuario")
    admin = models.ForeignKey("CustomUser", on_delete=models.SET_NULL, null=True, blank=True, related_name="pesquisas_criadas", help_text="Administrador que criou esta pesquisa")
    

    criacao = models.DateField(auto_now_add=True)
    atualizacao = models.DateTimeField(auto_now = True)

    dataInicio = models.DateField()
    dataTermino = models.DateField()

    codigoIBGE = models.CharField(max_length=255)
    estado = models.CharField(max_length=255)
    municipio = models.CharField(max_length=255)

    status = models.CharField(max_length=50, default='Não Iniciado')
    

    is_active = models.BooleanField(default=True)

    @property
    def admin_email(self):
        return self.admin.email if self.admin else None
    
    @property
    def admin_telefone(self):
        return self.admin.telefone if self.admin else None

    @property
    def quantidadePesquisadores(self):
        return self.usuario.count()

    @property
    def quantidadeLocais(self):
        return self.bases.filter(is_active=True).count()

class Base(models.Model):
    
    pesquisa = models.ForeignKey(Pesquisa, on_delete=models.CASCADE, related_name="bases")
    
    is_active = models.BooleanField(default=True)
   
    tipo_formulario = models.CharField(max_length=100, blank=True, null=True)
    uf = models.CharField(max_length=255, blank=True, null=True)
    regiao_turistica = models.CharField(max_length=255, blank=True, null=True)
    municipio = models.CharField(max_length=255, blank=True, null=True)

    tipo = models.CharField(max_length=255, blank=True, null=True)
  
 
    observacoes = models.TextField(blank=True, null=True)
    referencias = models.TextField(blank=True, null=True)

    nome_pesquisador = models.CharField(max_length=255)
    telefone_pesquisador = models.CharField(max_length=255)
    email_pesquisador = models.CharField(max_length=255)

    nome_coordenador = models.CharField(max_length=255)
    telefone_coordenador = models.CharField(max_length=255)
    email_coordenador = models.CharField(max_length=255)

class Inventariacao(models.Model):

    usuarios = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    equipamento = models.OneToOneField(Base, on_delete=models.SET_NULL, blank=True, null=True)

    criacao = models.DateField(auto_now_add=True)
    atualizacao = models.DateTimeField(auto_now = True)

class SistemaDeSeguranca(Base):
    contatos = models.ManyToManyField("ContatoInfo", related_name="sistemas_de_seguranca")
    servicos_especializados = models.ManyToManyField("ServicoEspecializadoInfo", related_name="sistemas_de_servicos_especializados")

class ContatoInfo(models.Model):

    sistema_de_seguranca = models.ManyToManyField("SistemaDeSeguranca", related_name="contatos_info")


    nome = models.CharField(max_length=255,null=True, blank=True)
    endereco = models.CharField(max_length=255,null=True, blank=True)
    whatsapp = models.CharField(max_length=255,null=True, blank=True)
    email = models.CharField(max_length=255,null=True, blank=True)

class ServicoEspecializadoInfo(models.Model):
    
    sistema_de_seguranca = models.ManyToManyField("SistemaDeSeguranca", related_name="servicos_info")


    email = models.CharField(max_length=255,null=True, blank=True)
    servicos_especializados = models.TextField(null=True, blank=True)
    outras_informacoes = models.TextField(null=True, blank=True)
    
class LocadorasDeImoveis(Base):
    contatos = models.ManyToManyField("InfoGerais", related_name="sistemas_de_seguranca")
    servicos_especializados = models.ManyToManyField("EnderecoInfo", related_name="sistemas_de_servicos_especializados")

class InfoGerais(models.Model):
    locadora_de_imoveis = models.ManyToManyField("LocadorasDeImoveis", related_name="info_gerais")

    razao_social = models.CharField(max_length=255, null=True, blank=True)
    nome_fantasia = models.CharField(max_length=255, null=True, blank=True)
    cnpj = models.CharField(max_length=255, null=True, blank=True)
    endereco = models.CharField(max_length=255, null=True, blank=True)
    telefone = models.CharField(max_length=255, null=True, blank=True)

class EnderecoInfo(models.Model):
    locadora_de_imoveis = models.ManyToManyField("LocadorasDeImoveis", related_name="endereco_info")

    email = models.CharField(max_length=255, null=True, blank=True)
    site = models.CharField(max_length=255, null=True, blank=True)
    tipoImoveis = models.CharField(max_length=255, null=True, blank=True)
    outrasInfo = models.CharField(max_length=255, null=True, blank=True)
    
class GuiamentoEConducaoTuristica(Base):
    contatos = models.ManyToManyField("InformacoesGuiamento", related_name="sistemas_de_seguranca")
    servicos_especializados = models.ManyToManyField("InformacoesGuiamentoCadastur", related_name="sistemas_de_servicos_especializados")
    subtipos = models.JSONField(null=True, blank=True)
class InformacoesGuiamento(models.Model):
    guiamento_e_conducao = models.ManyToManyField("GuiamentoEConducaoTuristica", related_name="info_gerais")

    nome_completo = models.CharField(max_length=255, null=True, blank=True)
    cpf = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    endereco = models.CharField(max_length=255, null=True, blank=True)
    telefone = models.CharField(max_length=255, null=True, blank=True)

class InformacoesGuiamentoCadastur(models.Model):
    guiamento_e_conducao = models.ManyToManyField("GuiamentoEConducaoTuristica", related_name="endereco_info")

    escolaridade = models.CharField(max_length=255, null=True, blank=True)
    servicos_especializados_formulario = models.CharField(max_length=255, null=True, blank=True)
    numero_cadastur = models.CharField(max_length=255, null=True, blank=True)
    outras_informacoes = models.CharField(max_length=255, null=True, blank=True)
    outros_cadastros = models.CharField(max_length=255, null=True, blank=True)
    
class GastronomiaArtesanato(Base):
    contatos = models.ManyToManyField("GastronomiaArtesanatoInfo", related_name="sistemas_de_seguranca")
    servicos_especializados = models.ManyToManyField("GastronomiaArtesanatoInfoAtelie", related_name="sistemas_de_servicos_especializados")
    subtipos = models.JSONField(null=True, blank=True)
    nomeProduto = models.CharField(max_length=255, blank=True, null=True)
    historicoProduto01 = models.CharField(max_length=255, blank=True, null=True)
    historicoProduto02 = models.CharField(max_length=255, blank=True, null=True)
    historicoProduto03 = models.CharField(max_length=255, blank=True, null=True)
    historicoProduto04 = models.CharField(max_length=255, blank=True, null=True)
    modoPreparo01 = models.CharField(max_length=255, blank=True, null=True)
    modoPreparo02 = models.CharField(max_length=255, blank=True, null=True)
    modoPreparo03 = models.CharField(max_length=255, blank=True, null=True)
    modoPreparo04 = models.CharField(max_length=255, blank=True, null=True)
    
    integraRoteiros = models.CharField(max_length=255, blank=True, null=True)
    integraGuiaTuristico = models.CharField(max_length=255, blank=True, null=True)
    roteiro1 = models.CharField(max_length=255, blank=True, null=True)
    siteRoteiro1 = models.CharField(max_length=255, blank=True, null=True)
    roteiro2 = models.CharField(max_length=255, blank=True, null=True)
    siteRoteiro2 = models.CharField(max_length=255, blank=True, null=True)
    roteiro3 = models.CharField(max_length=255, blank=True, null=True)
    siteRoteiro3 = models.CharField(max_length=255, blank=True, null=True)
    roteiro4 = models.CharField(max_length=255, blank=True, null=True)
    siteRoteiro4 = models.CharField(max_length=255, blank=True, null=True)
    roteiro5 = models.CharField(max_length=255, blank=True, null=True)
    siteRoteiro5 = models.CharField(max_length=255, blank=True, null=True)
    Guia1 = models.CharField(max_length=255, blank=True, null=True)
    siteGuia1 = models.CharField(max_length=255, blank=True, null=True)
    Guia2 = models.CharField(max_length=255, blank=True, null=True)
    siteGuia2 = models.CharField(max_length=255, blank=True, null=True)
    Guia3 = models.CharField(max_length=255, blank=True, null=True)
    siteGuia3 = models.CharField(max_length=255, blank=True, null=True)
    Guia4 = models.CharField(max_length=255, blank=True, null=True)
    siteGuia4 = models.CharField(max_length=255, blank=True, null=True)
    Guia5 = models.CharField(max_length=255, blank=True, null=True)
    siteGuia5 = models.CharField(max_length=255, blank=True, null=True)
    locaisDeComercializacao = models.JSONField(blank=True, null=True)
    descritivoEspecialidades = models.CharField(max_length=255, blank=True, null=True)
    
    tabelaEquipamentoEEspaco = models.JSONField(blank=True, null=True)
    tabelaEquipamentoEEspaco2 = models.JSONField(blank=True, null=True)
    doEquipamentoEspaco = models.CharField(max_length=255, blank=True, null=True)
    daAreaOuEdificacaoEmQueEstaLocalizado = models.CharField(max_length=255, blank=True, null=True)
    
class GastronomiaArtesanatoInfo(models.Model):
    guiamento_e_conducao = models.ManyToManyField("GastronomiaArtesanato", related_name="info_gerais")

    nome_completo = models.CharField(max_length=255, null=True, blank=True)
    atelie_aberto = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    endereco = models.CharField(max_length=255, null=True, blank=True)
    telefone = models.CharField(max_length=255, null=True, blank=True)

class GastronomiaArtesanatoInfoAtelie(models.Model):
    guiamento_e_conducao = models.ManyToManyField("GastronomiaArtesanato", related_name="endereco_info")

    ano_inicio_atividade = models.CharField(max_length=255, null=True, blank=True)
    premiacao = models.CharField(max_length=255, null=True, blank=True)
    outras_informacoes = models.CharField(max_length=255, null=True, blank=True)

class AlimentosEBebidas(Base):
    areaOuEdificacao =  models.CharField(max_length=255,blank=True, null=True)

    latitude = models.CharField(max_length=255,blank=True, null=True)
    longitude = models.CharField(max_length=255,blank=True, null=True)
    displayName = models.CharField(max_length=255,blank=True, null=True)
    rua = models.CharField(max_length=255,blank=True, null=True)
    bairro = models.CharField(max_length=255,blank=True, null=True)
    cidade = models.CharField(max_length=255,blank=True, null=True)
    estado = models.CharField(max_length=255,blank=True, null=True)
    pais = models.CharField(max_length=255,blank=True, null=True)
    razaoSocial = models.CharField(max_length=255, null=True, blank=True)
    nomeFantasia = models.CharField(max_length=255, null=True, blank=True)
    CNPJ = models.CharField(max_length=255, null=True, blank=True)
    codigoCNAE = models.CharField(max_length=255, null=True, blank=True)
    atividadeEconomica =models.CharField(max_length=255, null=True, blank=True)
    inscricaoMunicipal = models.CharField(max_length=255, null=True, blank=True)
    nomeDaRede =models.CharField(max_length=255, null=True, blank=True)

    natureza = models.CharField(max_length=255, null=True, blank=True)
    tipoDeOrganizacaoInstituicao = models.JSONField(null=True, blank=True)
    inicioDaAtividade = models.CharField(max_length=255, null=True, blank=True)
    qtdeFuncionariosPermanentes = models.CharField(max_length=255, null=True, blank=True)
    qtdeFuncionariosTemporarios = models.CharField(max_length=255, null=True, blank=True)
    qtdeFuncionariosComDeficiencia = models.CharField(max_length=255, null=True, blank=True)
    localizacao = models.CharField(max_length=255, null=True, blank=True)
    avenidaRuaEtc = models.CharField(max_length=255, null=True, blank=True)
    bairroLocalidade = models.CharField(max_length=255, null=True, blank=True)
    distrito = models.CharField(max_length=255, null=True, blank=True)
    CEP = models.CharField(max_length=255, null=True, blank=True)

    
    whatsapp = models.CharField(max_length=50, null=True, blank=True)
    instagram = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=50, null=True, blank=True)
    sinalizacaoDeAcesso = models.CharField(max_length=50, null=True, blank=True)
    sinalizacaoTuristica = models.CharField(max_length=50, null=True, blank=True)

    proximidades = models.JSONField(null=True, blank=True)

    distanciasAeroporto = models.CharField(max_length=255, null=True, blank=True)
    distanciasRodoviaria  = models.CharField(max_length=255, null=True, blank=True)
    distanciaEstacaoFerroviaria  = models.CharField(max_length=255, null=True, blank=True)
    distanciaEstacaoMaritima  = models.CharField(max_length=255, null=True, blank=True)
    distanciaEstacaoMetroviaria  = models.CharField(max_length=255, null=True, blank=True)
    distanciaPontoDeOnibus  = models.CharField(max_length=255, null=True, blank=True)
    distanciaPontoDeTaxi  = models.CharField(max_length=255, null=True, blank=True)
    distanciasOutraNome  = models.CharField(max_length=255, null=True, blank=True)
    distanciaOutras  = models.CharField(max_length=255, null=True, blank=True)

    pontosDeReferencia  = models.CharField(max_length=255, null=True, blank=True)

    tabelaMTUR = models.JSONField(null=True, blank=True)

    formasDePagamento = models.JSONField(null=True, blank=True)
    vendasEReservas = models.JSONField(null=True, blank=True)
    atendimentoEmLinguasEstrangeiras = models.JSONField(null=True, blank=True)
    informativosImpressos = models.JSONField(null=True, blank=True)

    periodo = models.JSONField(null=True, blank=True)
    tabelasHorario = models.JSONField(null=True, blank=True)

    funcionamento24h = models.CharField(max_length=255, null=True, blank=True)
    funcionamentoEmFeriados = models.CharField(max_length=255, null=True, blank=True)

    restricoes = models.JSONField(null=True, blank=True)

    outrasRegrasEInformacoes  = models.CharField(max_length=255, null=True, blank=True)

    capInstaladaPdia  = models.CharField(max_length=255, null=True, blank=True)
    capInstaladasSentadas  = models.CharField(max_length=255, null=True, blank=True)
    capSimultanea  = models.CharField(max_length=255, null=True, blank=True)
    capSimultaneaSentadas  = models.CharField(max_length=255, null=True, blank=True)

    estacionamento = models.JSONField(null=True, blank=True)

    capacidadeVeiculos  = models.CharField(max_length=255, null=True, blank=True)

    numeroAutomoveis  = models.CharField(max_length=255, null=True, blank=True)

    numeroOnibus  = models.CharField(max_length=255, null=True, blank=True)

    servicosEEquipamentos = models.JSONField(null=True, blank=True)

    especificacaoDaGastronomiaPorPais = models.JSONField(null=True, blank=True)

    seForBrasileiraPorRegiao = models.JSONField(null=True, blank=True)
    porEspecializacao = models.JSONField(null=True, blank=True)
    porTipoDeDieta = models.JSONField(null=True, blank=True)
    porTipoDeServico = models.JSONField(null=True, blank=True)

    doEquipamento = models.CharField(max_length=255, null=True, blank=True)

    tabelaEquipamentoEEspaco = models.JSONField(null=True, blank=True)

    estadoGeralDeConservacao = models.CharField(max_length=255, null=True, blank=True)

    possuiFacilidade = models.CharField(max_length=255, null=True, blank=True)

    pessoalCapacitadoParaReceberPCD = models.JSONField(null=True, blank=True)

    rotaExternaAcessível  = models.JSONField(null=True, blank=True)

    simboloInternacionalDeAcesso  = models.JSONField(null=True, blank=True)

    localDeEmbarqueEDesembarque  = models.JSONField(null=True, blank=True)

    vagaEmEstacionamento  = models.JSONField(null=True, blank=True)

    areaDeCirculacaoAcessoInternoParaCadeiraDeRodas  = models.JSONField(null=True, blank=True)

    escada  = models.JSONField(null=True, blank=True)

    rampa  = models.JSONField(null=True, blank=True)

    piso  = models.JSONField(null=True, blank=True)

    elevador =  models.JSONField(null=True, blank=True)

    equipamentoMotorizadoParaDeslocamentoInterno = models.JSONField(null=True, blank=True)

    sinalizacaoVisual = models.JSONField(null=True, blank=True)

    sinalizacaoTatil = models.JSONField(null=True, blank=True)

    alarmeDeEmergencia = models.JSONField(null=True, blank=True)

    comunicacao = models.JSONField(null=True, blank=True)

    balcaoDeAtendimento = models.JSONField(null=True, blank=True)

    mobiliario = models.JSONField(null=True, blank=True)

    sanitario = models.JSONField(null=True, blank=True)

    telefone = models.JSONField(null=True, blank=True)

    sinalizacaoIndicativa = models.CharField(max_length=255, null=True, blank=True)
    
    tabelaAreaOuEdificacao = models.JSONField(blank=True, null=True)
    rotaExternaAcessivel = models.JSONField("Rota Externa Acessível",blank=True, null=True)

    outrosAcessibilidade = models.CharField(max_length=255, null=True, blank=True)
    
class Rodovia(Base):

    subtipos = models.CharField(max_length=100, blank=True, null=True)

    nome_oficial = models.CharField(max_length=255,blank=True, null=True)
    nome_popular = models.CharField(max_length=255,blank=True, null=True)

    jurisdicao = models.CharField(max_length=50,blank=True, null=True)
    natureza = models.CharField(max_length=50,blank=True, null=True)
    
    tipo_de_organizacao_instituicao = models.JSONField(blank=True, null=True)
    

    extensao_rodovia_municipio = models.CharField(max_length=255,blank=True, null=True)

    faixas_de_rolamento = models.CharField(max_length=255,blank=True, null=True)

    pavimentacao = models.CharField(max_length=255,blank=True, null=True)

    pedagio = models.CharField(max_length=255,blank=True, null=True)

    municipios_vizinhos_interligados_rodovia = models.CharField(max_length=255,blank=True, null=True)

    inicio_atividade = models.CharField(max_length=255,blank=True, null=True)
    ##Entidade mantedora

    whatsapp = models.CharField(max_length=255,blank=True, null=True)
    instagram = models.CharField(max_length=255,blank=True, null=True)

    ##Sinalização

    sinalizacao_de_acesso = models.CharField(max_length=255,blank=True, null=True)
    sinalizacao_turistica = models.CharField(max_length=255,blank=True, null=True)

    ##Características

    posto_de_combustivel = models.JSONField(blank=True, null=True)
    outros_servicos = models.JSONField(blank=True, null=True)
    estruturas_ao_longo_da_via = models.JSONField(blank=True, null=True)

    ##Questões ambientais/Sociais

    poluicao = models.CharField(max_length=255,blank=True, null=True)
    poluicao_especificacao = models.CharField(max_length=255,blank=True, null=True)

    lixo = models.CharField(max_length=255,blank=True, null=True)
    lixo_especificacao = models.CharField(max_length=255,blank=True, null=True)

    desmatamento = models.CharField(max_length=255,blank=True, null=True)
    desmatamento_especificacao = models.CharField(max_length=255,blank=True, null=True)

    queimadas = models.CharField(max_length=255,blank=True, null=True)
    queimadas_especificacao = models.CharField(max_length=255,blank=True, null=True)

    inseguranca = models.CharField(max_length=255,blank=True, null=True)
    inseguranca_especificacao = models.CharField(max_length=255,blank=True, null=True)

    extrativismo = models.CharField(max_length=255,blank=True, null=True)
    extrativismo_especificacao = models.CharField(max_length=255,blank=True, null=True)

    prostituicao = models.CharField(max_length=255,blank=True, null=True)
    prostituicao_especificacao = models.CharField(max_length=255,blank=True, null=True)

    ocupacao_irregular_invasao = models.CharField(max_length=255,blank=True, null=True)
    ocupacao_irregular_invasao_especificacao = models.CharField(max_length=255,blank=True, null=True)

    outras = models.CharField(max_length=255,blank=True, null=True)
    outras_especificacao = models.CharField(max_length=255,blank=True, null=True)

    ##Estado geral de conservação

    estado_geral_de_conservacao = models.CharField(max_length=255,blank=True, null=True)

    ##Observações

class MeioDeHospedagem(Base):
   
    # Dados do formulário e pesquisador
    
    # Dados do coordenador
    
    # Sinalizações e funcionamento
    sinalizacaoDeAcesso = models.CharField("Sinalização de Acesso",max_length=255,blank=True, null=True)
    sinalizacaoTuristica = models.CharField("Sinalização Turística",max_length=255,blank=True, null=True)
    funcionamento24h = models.CharField("Funcionamento 24h",max_length=255,blank=True, null=True)
    funcionamentoEmFeriados = models.CharField("Funcionamento em Feriados",max_length=255,blank=True, null=True)
    geradorDeEmergencia = models.CharField("Gerador de Emergência",max_length=255,blank=True, null=True)
    
    # Infraestrutura e localização do equipamento/edificação
    doEquipamentoEspaco = models.TextField("Do Equipamento/Espaço", blank=True, null=True)
    daAreaOuEdificacaoEmQueEstaLocalizado = models.TextField("Da Área/Edificação em que Está Localizado", blank=True, null=True)
    possuiFacilidade = models.CharField("Possui Facilidade",max_length=255,blank=True, null=True)
    sinalizacaoIndicativa = models.CharField("Sinalização Indicativa", max_length=255,blank=True, null=True)
    tipoDeOrganizacao = models.JSONField("Tipo de Organização",blank=True, null=True)
    proximidades = models.JSONField("Proximidades",blank=True, null=True)
    
    # Dados relacionados ao turismo e pagamentos
    segmentosOuTurismoEspecializado = models.JSONField("Segmentos ou Turismo Especializado",blank=True, null=True)
    formasDePagamento = models.JSONField("Formas de Pagamento",blank=True, null=True)
    reservas = models.JSONField("Reservas",blank=True, null=True)
    atendimentoEmLinguaEstrangeira = models.JSONField("Atendimento em Língua Estrangeira",blank=True, null=True)
    informativosImpressos = models.JSONField("Informativos Impressos",blank=True, null=True)
    restricoes = models.JSONField("Restrições",blank=True, null=True)
    mesesAltaTemporada = models.JSONField("Meses de Alta Temporada",blank=True, null=True)
    origemDosVisitantes = models.JSONField("Origem dos Visitantes",blank=True, null=True)
    
    # Produtos e serviços
    produtosHigienePessoal = models.JSONField("Produtos de Higiene Pessoal",blank=True, null=True)
    equipamentosEServicos = models.JSONField("Equipamentos e Serviços",blank=True, null=True)
    estacionamento = models.JSONField("Estacionamento",blank=True, null=True)
    restaurante = models.JSONField("Restaurante",blank=True, null=True)
    lanchonete = models.JSONField("Lanchonete",blank=True, null=True)
    instalacaoEEspacos = models.JSONField("Instalação e Espaços",blank=True, null=True)
    outrosEspacosEAtividades = models.JSONField("Outros Espaços e Atividades",blank=True, null=True)
    servicos = models.JSONField("Serviços",blank=True, null=True)
    equipamentos = models.JSONField("Equipamentos",blank=True, null=True)
    facilidadesEServicos = models.JSONField("Facilidades e Serviços",blank=True, null=True)
    facilidadesParaExecutivos = models.JSONField("Facilidades para Executivos",blank=True, null=True)
    pessoalCapacitadoParaReceberPCD = models.JSONField("Pessoal Capacitado para Receber PCD",blank=True, null=True)
    
    # Acessibilidade
    rotaExternaAcessivel = models.JSONField("Rota Externa Acessível",blank=True, null=True)
    simboloInternacionalDeAcesso = models.JSONField("Símbolo Internacional de Acesso",blank=True, null=True)
    localDeEmbarqueEDesembarque = models.JSONField("Local de Embarque e Desembarque",blank=True, null=True)
    vagaEmEstacionamento = models.JSONField("Vaga em Estacionamento",blank=True, null=True)
    areaDeCirculacaoAcessoInterno = models.JSONField("Área de Circulação/Acesso Interno",blank=True, null=True)
    escada = models.JSONField("Escada",blank=True, null=True)
    rampa = models.JSONField("Rampa",blank=True, null=True)
    piso = models.JSONField("Piso",blank=True, null=True)
    elevador = models.JSONField("Elevador",blank=True, null=True)
    equipamentoMotorizadoParaDeslocamentoInterno = models.JSONField("Equipamento Motorizado para Deslocamento Interno",blank=True, null=True)
    sinalizacaoVisual = models.JSONField("Sinalização Visual",blank=True, null=True)
    sinalizacaoTatil = models.JSONField("Sinalização Tátil",blank=True, null=True)
    alarmeDeEmergencia = models.JSONField("Alarme de Emergência",blank=True, null=True)
    comunicacao = models.JSONField("Comunicação",blank=True, null=True)
    balcaoDeAtendimento = models.JSONField("Balcão de Atendimento",blank=True, null=True)
    mobiliario = models.JSONField("Mobiliário",blank=True, null=True)
    sanitario = models.JSONField("Sanitário",blank=True, null=True)
    telefone = models.JSONField("Telefone",blank=True, null=True)
    
    # Classificação e localização do meio de hospedagem
    subtipo = models.JSONField(blank=True, null=True)
    natureza = models.CharField("Natureza", max_length=255, blank=True, null=True)
    localizacao = models.TextField("Localização", blank=True, null=True)
    tipoDeDiaria = models.CharField("Tipo de Diária", max_length=255, blank=True, null=True)
    periodo = models.JSONField(blank=True, null=True)
    tabelasHorario = models.JSONField("Tabelas de Horário",blank=True,null=True)
    energiaEletrica = models.TextField("Energia Elétrica", blank=True, null=True)
    estadoGeralDeConservacao = models.CharField("Estado Geral de Conservação", max_length=255, blank=True, null=True)
    
    # Dados de turismo e localização geográfica
    estadosTuristas = models.JSONField("Estados Turistas", blank=True, null=True)
    paisesTuristas = models.JSONField("Países Turistas", blank=True,null=True)
    
    # Dados empresariais
    razaoSocial = models.CharField("Razão Social", max_length=255, blank=True, null=True)
    nomeFantasia = models.CharField("Nome Fantasia", max_length=255, blank=True, null=True)
    codigoCNAE = models.CharField("Código CNAE", max_length=50, blank=True, null=True)
    atividadeEconomica = models.TextField("Atividade Econômica", blank=True, null=True)
    inscricaoMunicipal = models.CharField("Inscrição Municipal", max_length=50, blank=True, null=True)
    nomeDaRede = models.CharField("Nome da Rede", max_length=255, blank=True, null=True)
    CNPJ = models.CharField("CNPJ", max_length=20, blank=True, null=True)
    inicioDaAtividade = models.CharField("Início da Atividade",max_length=255, blank=True, null=True)
    
    # Dados de quantitativos e capacidade
    qtdeFuncionariosPermanentes = models.CharField("Qtd. Funcionários Permanentes", max_length = 254, blank=True, null=True)
    qtdeFuncionariosTemporarios = models.CharField("Qtd. Funcionários Temporários", max_length = 254, blank=True, null=True)
    qtdeFuncionarisComDeficiencia = models.CharField("Qtd. Funcionários com Deficiência", max_length = 254, blank=True, null=True)
    latitude = models.CharField(max_length=255,blank=True, null=True)
    longitude = models.CharField(max_length=255,blank=True, null=True)
    
    # Endereço e contato
    avenidaRuaEtc = models.CharField("Avenida/Rua/etc.", max_length=255, blank=True, null=True)
    bairroLocalidade = models.CharField("Bairro/Localidade", max_length=255, blank=True, null=True)
    distrito = models.CharField("Distrito", max_length=255, blank=True, null=True)
    CEP = models.CharField("CEP", max_length=20, blank=True, null=True)
    whatsapp = models.CharField("WhatsApp", max_length=50, blank=True, null=True)
    instagram = models.CharField("Instagram", max_length=100, blank=True, null=True)
    email = models.CharField("Email", max_length=254, blank=True, null=True)
    site = models.CharField("Site", max_length=255,blank=True, null=True)
    pontosDeReferencia = models.TextField("Pontos de Referência", blank=True, null=True)
    
    # Dados de tabelas e informações adicionais
    tabelaMTUR = models.JSONField("Tabela MTUR",blank=True,null=True)
    outrasRegrasEInformacoes = models.TextField("Outras Regras e Informações", blank=True, null=True)
    nAnoOcupacao = models.CharField("Ano de Ocupação", max_length=255,blank=True, null=True)
    nOcupacaoAltaTemporada = models.CharField("Ocupação em Alta Temporada", max_length=255,blank=True, null=True)
    nTotalDeUH = models.CharField("Total de UH", max_length = 254, blank=True, null=True)
    nTotalDeLeitos = models.CharField("Total de Leitos", max_length = 254, blank=True, null=True)
    nUhAdaptadasParaPCD = models.CharField("UH Adaptadas para PCD", max_length = 254, blank=True, null=True)
    nCapacidadeDeVeiculos = models.CharField("Capacidade de Veículos", max_length = 254, blank=True, null=True)
    nAutomoveis = models.CharField("Número de Automóveis", max_length = 254, blank=True, null=True)
    nOnibus = models.CharField("Número de Ônibus", max_length = 254, blank=True, null=True)
    capacidadeEmKVA = models.DecimalField("Capacidade (KVA)", max_digits=10, decimal_places=2, blank=True, null=True)
    geradorCapacidadeEmKVA = models.DecimalField("Capacidade do Gerador (KVA)", max_digits=10, decimal_places=2, blank=True, null=True)
    nCapacidadeInstaladaPorDia = models.CharField("Capacidade Instalada por Dia", max_length = 254, blank=True, null=True)
    nPessoasAtendidasSentadas = models.CharField("Qtd. de Pessoas Atendidas Sentadas", max_length = 254, blank=True, null=True)
    nCapacidadeSimultanea = models.CharField("Capacidade Simultânea", max_length = 254, blank=True, null=True)
    nPessoasAtendidasSentadasSimultanea = models.CharField("Qtd. de Pessoas Atendidas Sentadas (Simultânea)", max_length = 254, blank=True, null=True)
    lanchoneteCapacidadeInstaladaPorDia = models.CharField("Lanchonete - Capacidade Instalada por Dia", max_length = 254, blank=True, null=True)
    lanchoneteCapacidadePessoasAtendidasSentadas = models.CharField("Lanchonete - Pessoas Atendidas Sentadas", max_length = 254, blank=True, null=True)
    lanchoneteCapacidadeSimultanea = models.CharField("Lanchonete - Capacidade Simultânea", max_length = 254, blank=True, null=True)
    lanchoneteCapacidadeSentadasSimultanea = models.CharField("Lanchonete - Pessoas Sentadas Simultânea", max_length = 254, blank=True, null=True)
    outrasAcessibilidade = models.CharField(max_length=255,blank=True, null=True)
    
    # Tabelas de instalações e equipamentos/espaços
    tabelaInstalacoes = models.JSONField("Tabela Instalações",blank=True,null=True)
    tabelaEquipamentoEEspaco = models.JSONField("Tabela Equipamento e Espaço",blank=True,null=True)
    tabelaEquipamentoEEspaco2 = models.JSONField("Tabela Equipamento e Espaço 2",blank=True,null=True )
    
    # Observações e referências
    outros = models.TextField("Outros", blank=True, null=True)

class OutrosMeiosDeHospedagem(Base):
   
    # Dados do formulário e pesquisador
    
    # Dados do coordenador
    
    # Sinalizações e funcionamento
    sinalizacaoDeAcesso = models.CharField("Sinalização de Acesso",max_length=255,blank=True, null=True)
    sinalizacaoTuristica = models.CharField("Sinalização Turística",max_length=255,blank=True, null=True)
    funcionamento24h = models.CharField("Funcionamento 24h",max_length=255,blank=True, null=True)
    funcionamentoEmFeriados = models.CharField("Funcionamento em Feriados",max_length=255,blank=True, null=True)
    geradorDeEmergencia = models.CharField("Gerador de Emergência",max_length=255,blank=True, null=True)
    
    # Infraestrutura e localização do equipamento/edificação
    doEquipamentoEspaco = models.TextField("Do Equipamento/Espaço", blank=True, null=True)
    daAreaOuEdificacaoEmQueEstaLocalizado = models.TextField("Da Área/Edificação em que Está Localizado", blank=True, null=True)
    possuiFacilidade = models.CharField("Possui Facilidade",max_length=255,blank=True, null=True)
    sinalizacaoIndicativa = models.CharField("Sinalização Indicativa", max_length=255,blank=True, null=True)
    tipoDeOrganizacao = models.JSONField("Tipo de Organização",blank=True, null=True)
    proximidades = models.JSONField("Proximidades",blank=True, null=True)
    
    # Dados relacionados ao turismo e pagamentos
    segmentosOuTurismoEspecializado = models.JSONField("Segmentos ou Turismo Especializado",blank=True, null=True)
    formasDePagamento = models.JSONField("Formas de Pagamento",blank=True, null=True)
    reservas = models.JSONField("Reservas",blank=True, null=True)
    atendimentoEmLinguaEstrangeira = models.JSONField("Atendimento em Língua Estrangeira",blank=True, null=True)
    informativosImpressos = models.JSONField("Informativos Impressos",blank=True, null=True)
    restricoes = models.JSONField("Restrições",blank=True, null=True)
    mesesAltaTemporada = models.JSONField("Meses de Alta Temporada",blank=True, null=True)
    origemDosVisitantes = models.JSONField("Origem dos Visitantes",blank=True, null=True)

    barraca = models.CharField(max_length=255,blank=True, null=True)
    barracaCapacidadeEquipamentos = models.CharField(max_length=255,blank=True, null=True)
    barracaCapacidadePessoas = models.CharField(max_length=255,blank=True, null=True)

    trailer = models.CharField(max_length=255,blank=True, null=True)
    trailerCapacidadeEquipamentos = models.CharField(max_length=255,blank=True, null=True)
    trailerCapacidadePessoas = models.CharField(max_length=255,blank=True, null=True)

    motorHome = models.CharField(max_length=255,blank=True, null=True)
    motorHomeCapacidadeEquipamentos = models.CharField(max_length=255,blank=True, null=True)
    motorHomeCapacidadePessoas = models.CharField(max_length=255,blank=True, null=True)

    carretaBarraca = models.CharField(max_length=255,blank=True, null=True)
    carretaBarracaCapacidadeEquipamentos = models.CharField(max_length=255,blank=True, null=True)
    carretaBarracaCapacidadePessoas = models.CharField(max_length=255,blank=True, null=True)

    campers = models.CharField(max_length=255,blank=True, null=True)
    campersCapacidadeEquipamentos = models.CharField(max_length=255,blank=True, null=True)
    campersCapacidadePessoas = models.CharField(max_length=255,blank=True, null=True)

    areaAcampamento = models.JSONField(blank=True, null=True)

    sanitarioEspec = models.CharField(max_length=255,blank=True, null=True)
    chuveiroQuente = models.CharField(max_length=255,blank=True, null=True)
    chuveiroFrio = models.CharField(max_length=255,blank=True, null=True)
    piaParaLouca = models.CharField(max_length=255,blank=True, null=True)
    tanqueParaRoupas = models.CharField(max_length=255,blank=True, null=True)
    lavatorio = models.CharField(max_length=255,blank=True, null=True)
    lixeira = models.CharField(max_length=255,blank=True, null=True)
    cantina = models.CharField(max_length=255,blank=True, null=True)

    pontosDeAgua = models.CharField(max_length=255,blank=True, null=True)
    aguaPotavel = models.CharField(max_length=255,blank=True, null=True)
    instalacoesHidraulicas = models.CharField(max_length=255,blank=True, null=True)
    instalacoesEletricas = models.CharField(max_length=255,blank=True, null=True)
    pontosDeEnergia = models.CharField(max_length=255,blank=True, null=True)
    pontosDeEnergiaIdentificados = models.CharField(max_length=255,blank=True, null=True)
    tomadasDeEnergiaIdentificadas = models.CharField(max_length=255,blank=True, null=True)
    medidoresIndividuais = models.CharField(max_length=255,blank=True, null=True)

    utilizacao = models.JSONField(blank=True, null=True)

    # Produtos e serviços
    equipamentosEServicos = models.JSONField("Equipamentos e Serviços",blank=True, null=True)
    estacionamento = models.JSONField("Estacionamento",blank=True, null=True)
    restaurante = models.JSONField("Restaurante",blank=True, null=True)
    lanchonete = models.JSONField("Lanchonete",blank=True, null=True)
    instalacaoEEspacos = models.JSONField("Instalação e Espaços",blank=True, null=True)
    outrosEspacosEAtividades = models.JSONField("Outros Espaços e Atividades",blank=True, null=True)
    servicos = models.JSONField("Serviços",blank=True, null=True)
    equipamentos = models.JSONField("Equipamentos",blank=True, null=True)
    facilidadesEServicos = models.JSONField("Facilidades e Serviços",blank=True, null=True)
    facilidadesParaExecutivos = models.JSONField("Facilidades para Executivos",blank=True, null=True)
    pessoalCapacitadoParaReceberPCD = models.JSONField("Pessoal Capacitado para Receber PCD",blank=True, null=True)
    
    # Acessibilidade
    rotaExternaAcessivel = models.JSONField("Rota Externa Acessível",blank=True, null=True)
    simboloInternacionalDeAcesso = models.JSONField("Símbolo Internacional de Acesso",blank=True, null=True)
    localDeEmbarqueEDesembarque = models.JSONField("Local de Embarque e Desembarque",blank=True, null=True)
    vagaEmEstacionamento = models.JSONField("Vaga em Estacionamento",blank=True, null=True)
    areaDeCirculacaoAcessoInterno = models.JSONField("Área de Circulação/Acesso Interno",blank=True, null=True)
    escada = models.JSONField("Escada",blank=True, null=True)
    rampa = models.JSONField("Rampa",blank=True, null=True)
    piso = models.JSONField("Piso",blank=True, null=True)
    elevador = models.JSONField("Elevador",blank=True, null=True)
    equipamentoMotorizadoParaDeslocamentoInterno = models.JSONField("Equipamento Motorizado para Deslocamento Interno",blank=True, null=True)
    sinalizacaoVisual = models.JSONField("Sinalização Visual",blank=True, null=True)
    sinalizacaoTatil = models.JSONField("Sinalização Tátil",blank=True, null=True)
    alarmeDeEmergencia = models.JSONField("Alarme de Emergência",blank=True, null=True)
    comunicacao = models.JSONField("Comunicação",blank=True, null=True)
    balcaoDeAtendimento = models.JSONField("Balcão de Atendimento",blank=True, null=True)
    mobiliario = models.JSONField("Mobiliário",blank=True, null=True)
    sanitario = models.JSONField("Sanitário",blank=True, null=True)
    telefone = models.JSONField("Telefone",blank=True, null=True)
    
    # Classificação e localização do meio de hospedagem
    subtipo = models.JSONField(blank=True, null=True)
    natureza = models.CharField("Natureza", max_length=255, blank=True, null=True)
    localizacao = models.TextField("Localização", blank=True, null=True)
    tipoDeDiaria = models.CharField("Tipo de Diária", max_length=255, blank=True, null=True)
    periodo = models.JSONField(blank=True, null=True)
    tabelasHorario = models.JSONField("Tabelas de Horário",blank=True,null=True)
    energiaEletrica = models.TextField("Energia Elétrica", blank=True, null=True)
    estadoGeralDeConservacao = models.CharField("Estado Geral de Conservação", max_length=255, blank=True, null=True)
    
    # Dados de turismo e localização geográfica
    estadosTuristas = models.JSONField("Estados Turistas", blank=True, null=True)
    paisesTuristas = models.JSONField("Países Turistas", blank=True,null=True)
    
    # Dados empresariais
    razaoSocial = models.CharField("Razão Social", max_length=255, blank=True, null=True)
    nomeFantasia = models.CharField("Nome Fantasia", max_length=255, blank=True, null=True)
    codigoCNAE = models.CharField("Código CNAE", max_length=50, blank=True, null=True)
    atividadeEconomica = models.TextField("Atividade Econômica", blank=True, null=True)
    inscricaoMunicipal = models.CharField("Inscrição Municipal", max_length=50, blank=True, null=True)
    nomeDaRede = models.CharField("Nome da Rede", max_length=255, blank=True, null=True)
    CNPJ = models.CharField("CNPJ", max_length=20, blank=True, null=True)
    inicioDaAtividade = models.CharField("Início da Atividade",max_length=255, blank=True, null=True)
    
    # Dados de quantitativos e capacidade
    qtdeFuncionariosPermanentes = models.CharField("Qtd. Funcionários Permanentes", max_length = 254, blank=True, null=True)
    qtdeFuncionariosTemporarios = models.CharField("Qtd. Funcionários Temporários", max_length = 254, blank=True, null=True)
    qtdeFuncionarisComDeficiencia = models.CharField("Qtd. Funcionários com Deficiência", max_length = 254, blank=True, null=True)
    latitude = models.CharField(max_length=255,blank=True, null=True)
    longitude = models.CharField(max_length=255,blank=True, null=True)
    
    # Endereço e contato
    avenidaRuaEtc = models.CharField("Avenida/Rua/etc.", max_length=255, blank=True, null=True)
    bairroLocalidade = models.CharField("Bairro/Localidade", max_length=255, blank=True, null=True)
    distrito = models.CharField("Distrito", max_length=255, blank=True, null=True)
    CEP = models.CharField("CEP", max_length=20, blank=True, null=True)
    whatsapp = models.CharField("WhatsApp", max_length=50, blank=True, null=True)
    instagram = models.CharField("Instagram", max_length=100, blank=True, null=True)
    email = models.CharField("Email", max_length=254, blank=True, null=True)
    site = models.CharField("Site", max_length=255,blank=True, null=True)
    pontosDeReferencia = models.TextField("Pontos de Referência", blank=True, null=True)
    
    # Dados de tabelas e informações adicionais
    tabelaMTUR = models.JSONField("Tabela MTUR",blank=True,null=True)
    outrasRegrasEInformacoes = models.TextField("Outras Regras e Informações", blank=True, null=True)
    nAnoOcupacao = models.CharField("Ano de Ocupação", max_length=255,blank=True, null=True)
    nOcupacaoAltaTemporada = models.CharField("Ocupação em Alta Temporada", max_length=255,blank=True, null=True)
    nCapacidadeDeVeiculos = models.CharField("Capacidade de Veículos", max_length = 254, blank=True, null=True)
    nAutomoveis = models.CharField("Número de Automóveis", max_length = 254, blank=True, null=True)
    nOnibus = models.CharField("Número de Ônibus", max_length = 254, blank=True, null=True)
    capacidadeEmKVA = models.DecimalField("Capacidade (KVA)", max_digits=10, decimal_places=2, blank=True, null=True)
    geradorCapacidadeEmKVA = models.DecimalField("Capacidade do Gerador (KVA)", max_digits=10, decimal_places=2, blank=True, null=True)
    nCapacidadeInstaladaPorDia = models.CharField("Capacidade Instalada por Dia", max_length = 254, blank=True, null=True)
    nPessoasAtendidasSentadas = models.CharField("Qtd. de Pessoas Atendidas Sentadas", max_length = 254, blank=True, null=True)
    nCapacidadeSimultanea = models.CharField("Capacidade Simultânea", max_length = 254, blank=True, null=True)
    nPessoasAtendidasSentadasSimultanea = models.CharField("Qtd. de Pessoas Atendidas Sentadas (Simultânea)", max_length = 254, blank=True, null=True)
    lanchoneteCapacidadeInstaladaPorDia = models.CharField("Lanchonete - Capacidade Instalada por Dia", max_length = 254, blank=True, null=True)
    lanchoneteCapacidadePessoasAtendidasSentadas = models.CharField("Lanchonete - Pessoas Atendidas Sentadas", max_length = 254, blank=True, null=True)
    lanchoneteCapacidadeSimultanea = models.CharField("Lanchonete - Capacidade Simultânea", max_length = 254, blank=True, null=True)
    lanchoneteCapacidadeSentadasSimultanea = models.CharField("Lanchonete - Pessoas Sentadas Simultânea", max_length = 254, blank=True, null=True)
    outrasAcessibilidade = models.CharField(max_length=255,blank=True, null=True)
    
    # Tabelas de instalações e equipamentos/espaços
    tabelaInstalacoes = models.JSONField("Tabela Instalações",blank=True,null=True)
    tabelaEquipamentoEEspaco = models.JSONField("Tabela Equipamento e Espaço",blank=True,null=True)
    tabelaEquipamentoEEspaco2 = models.JSONField("Tabela Equipamento e Espaço 2",blank=True,null=True )
    
    # Observações e referências
    outros = models.TextField("Outros", blank=True, null=True)

class InformacaoBasicaDoMunicipio(Base):
    latitude = models.CharField(max_length=255,blank=True, null=True)
    longitude = models.CharField(max_length=255,blank=True, null=True)
    displayName = models.CharField(max_length=255,blank=True, null=True)
    rua = models.CharField(max_length=255,blank=True, null=True)
    bairro = models.CharField(max_length=255,blank=True, null=True)
    cidade = models.CharField(max_length=255,blank=True, null=True)
    estado = models.CharField(max_length=255,blank=True, null=True)
    pais = models.CharField(max_length=255,blank=True, null=True)
    enderecoPrefeitura = models.CharField(max_length=255,blank=True, null=True)
    bairroPrefeitura = models.CharField(max_length=255,blank=True, null=True)
    cepPrefeitura = models.CharField(max_length=255,blank=True, null=True)
    numeroPrefeitura = models.CharField(max_length=255,blank=True, null=True)
    instagramPrefeitura = models.CharField(max_length=255,blank=True, null=True)
    emailPrefeitura = models.CharField(max_length=255,blank=True, null=True)
    sitePrefeitura = models.CharField(max_length=255,blank=True, null=True)
    cnpjPrefeitura = models.CharField(max_length=255,blank=True, null=True)
    latitudePrefeitura = models.CharField(max_length=255,blank=True, null=True)
    longitudePrefeitura = models.CharField(max_length=255,blank=True, null=True)
    municipiosLimitrofes = models.CharField(max_length=255,blank=True, null=True)
    distanciaDaCapital = models.CharField(max_length=255,blank=True, null=True)
    totalFuncionariosPrefeitura = models.CharField(max_length=255,blank=True, null=True)
    pessoasComDeficienciaPrefeitura = models.CharField(max_length=255,blank=True, null=True)
    nomeDoPrefeito = models.CharField(max_length=255,blank=True, null=True)
    nomeDasSecretariasEtc = models.CharField(max_length=255,blank=True, null=True)
    nomeOrgaoOficialTurismo = models.CharField(max_length=255,blank=True, null=True)
    enderecoOrgaoOfcTurismo = models.CharField(max_length=255,blank=True, null=True)
    avenidaRuaOfcTurismo = models.CharField(max_length=255,blank=True, null=True)
    distritoOrgaoOfcTurismo = models.CharField(max_length=255,blank=True, null=True)
    cepOrgaoOfcTurismo = models.CharField(max_length=255,blank=True, null=True)
    numeroOrgaoOfcTurismo = models.CharField(max_length=255,blank=True, null=True)
    instagramOrgaoOfcTurismo = models.CharField(max_length=255,blank=True, null=True)
    siteOrgaoOfcTurismo = models.CharField(max_length=255,blank=True, null=True)
    emailOrgaoOfcTurismo = models.CharField(max_length=255,blank=True, null=True)
    qtdeFuncionariosOrgaoOfcTurismo = models.CharField(max_length=255,blank=True, null=True)
    qtdeFormacaoSuperiorEmTurismoOrgaoOfcturismo = models.CharField(max_length=255,blank=True, null=True)
    instanciaGovernancaMunicipal = models.CharField(max_length=255,blank=True, null=True)
    instanciaGovernancaEstadual = models.CharField(max_length=255,blank=True, null=True)
    instanciaGovernancaRegional = models.CharField(max_length=255,blank=True, null=True)
    instanciaGovernancaNacional = models.CharField(max_length=255,blank=True, null=True)
    instanciaGovernancaInternacional = models.CharField(max_length=255,blank=True, null=True)
    instanciaGovernancaOutras = models.CharField(max_length=255,blank=True, null=True)
    aniversarioMunicipio = models.CharField(max_length=255,blank=True, null=True)
    santoPadroeiro = models.CharField(max_length=255,blank=True, null=True)
    diaDoSantoPadroeiro = models.CharField(max_length=255,blank=True, null=True)
    feriadoMunicipal01 = models.CharField(max_length=255,blank=True, null=True)
    dataFeriadoMunicipal01 = models.CharField(max_length=255,blank=True, null=True)
    feriadoMunicipal02 = models.CharField(max_length=255,blank=True, null=True)
    dataFeriadoMunicipal02 = models.CharField(max_length=255,blank=True, null=True)
    feriadoMunicipal03 = models.CharField(max_length=255,blank=True, null=True)
    dataFeriadoMunicipal03 =models.CharField(max_length=255,blank=True, null=True)
    origemDoNome =models.CharField(max_length=255,blank=True, null=True)
    dataFundacao = models.CharField(max_length=255,blank=True, null=True)
    dataEmancipacao = models.CharField(max_length=255,blank=True, null=True)
    fundadores = models.CharField(max_length=255,blank=True, null=True)
    outrosFatosDeImportanciaHistorica = models.CharField(max_length=255,blank=True, null=True)

    areaTotalMunicipio = models.CharField(max_length=255,blank=True, null=True)
    areaUrbana = models.CharField(max_length=255,blank=True, null=True)
    areaRural = models.CharField(max_length=255,blank=True, null=True)
    anoBase = models.CharField(max_length=255,blank=True, null=True)
    populacaoTotal = models.CharField(max_length=255,blank=True, null=True)
    populacaoUrbana = models.CharField(max_length=255,blank=True, null=True)
    populacaoRural = models.CharField(max_length=255,blank=True, null=True)
    anoBasePopulacao = models.CharField(max_length=255,blank=True, null=True)
    temperaturaMedia = models.CharField(max_length=255,blank=True, null=True)
    temperaturaMinima = models.CharField(max_length=255,blank=True, null=True)
    temperaturaMaxima = models.CharField(max_length=255,blank=True, null=True)
    altitudeMedia = models.CharField(max_length=255,blank=True, null=True)
    qtdeDomiciliosAtendidos = models.CharField(max_length=255,blank=True, null=True)
    empresaResponsavel = models.CharField(max_length=255,blank=True, null=True)
    esgotoTotalAtendidos = models.CharField(max_length=255,blank=True, null=True)
    esgotoDomiciliosAtendidos = models.CharField(max_length=255,blank=True, null=True)
    esgotoRuraisAtendidos = models.CharField(max_length=255,blank=True, null=True)
    esgotoEntidadeResponsavel = models.CharField(max_length=255,blank=True, null=True)
    fossaSepticaTotalAtendidos = models.CharField(max_length=255,blank=True, null=True)
    fossaSepticaDomiciliosAtendidos = models.CharField(max_length=255,blank=True, null=True)
    fossaSepticaRuraisAtendidos = models.CharField(max_length=255,blank=True, null=True)
    fossaSepticaEntidadeResponsavel = models.CharField(max_length=255,blank=True, null=True)
    fossaRudimentarTotalAtendidos = models.CharField(max_length=255,blank=True, null=True)
    fossaRudimentarDomiciliosAtendidos = models.CharField(max_length=255,blank=True, null=True)
    fossaRudimentarRuraisAtendidos = models.CharField(max_length=255,blank=True, null=True)
    fossaRudimentarEntidadeResponsavel = models.CharField(max_length=255,blank=True, null=True)
    valaTotalAtendidos = models.CharField(max_length=255,blank=True, null=True)
    valaDomiciliosAtendidos = models.CharField(max_length=255,blank=True, null=True)
    valaRuraisAtendidos = models.CharField(max_length=255,blank=True, null=True)
    valaEntidadeResponsavel = models.CharField(max_length=255,blank=True, null=True)
    estacaoDeTratamentoTotalAtendidos = models.CharField(max_length=255,blank=True, null=True)
    estacaoDeTratamentoDomiciliosAtendidos  = models.CharField(max_length=255,blank=True, null=True)
    estacaoDeTratamentoRuraisAtendidos = models.CharField(max_length=255,blank=True, null=True)
    estacaoDeTratamentoEntidadeResponsavel  = models.CharField(max_length=255,blank=True, null=True)
    esgotoTratadoTotalAtendidos = models.CharField(max_length=255,blank=True, null=True)
    esgotoTratadoDomiciliosAtendidos = models.CharField(max_length=255,blank=True, null=True)
    esgotoTratadoRuraisAtendidos = models.CharField(max_length=255,blank=True, null=True)
    esgotoTratadoEntidadeResponsavel = models.CharField(max_length=255,blank=True, null=True)
    servicoDeEsgotoOutroTotalNome = models.CharField(max_length=255,blank=True, null=True)
    servicoDeEsgotoOutroTotalAtendidos = models.CharField(max_length=255,blank=True, null=True)
    servicoDeEsgotoOutroDomiciliosAtendidos = models.CharField(max_length=255,blank=True, null=True)
    servicoDeEsgotoOutroRuraisAtendidos = models.CharField(max_length=255,blank=True, null=True)
    servicoDeEsgotoOutroEntidadeResponsavel = models.CharField(max_length=255,blank=True, null=True)
    capacidadeEmKVA = models.CharField(max_length=255,blank=True, null=True)
    geradorDeEmergenciaCapacidadeEmKVA = models.CharField(max_length=255,blank=True, null=True)
    redeUrbanaTotalAbastecido = models.CharField(max_length=255,blank=True, null=True)
    redeUrbanaEntidadeResponsavel = models.CharField(max_length=255,blank=True, null=True)
    redeRuralTotalAbastecido  = models.CharField(max_length=255,blank=True, null=True)
    redeRuralEntidadeResponsavel  = models.CharField(max_length=255,blank=True, null=True)
    abastecimentoProprioTotalAtendidos = models.CharField(max_length=255,blank=True, null=True)
    abastecimentoProprioDomiciliosAtendidos = models.CharField(max_length=255,blank=True, null=True)
    abastecimentoProprioRuraisAtendidos = models.CharField(max_length=255,blank=True, null=True)
    abastecimentoProprioEntidadeResponsavel = models.CharField(max_length=255,blank=True, null=True)

    servicosDeEnergiaOutroTotalNome = models.CharField(max_length=255,blank=True, null=True)
    servicosDeEnergiaOutroTotalAtendidos  = models.CharField(max_length=255,blank=True, null=True)
    servicosDeEnergiaOutroDomiciliosAtendidos  = models.CharField(max_length=255,blank=True, null=True)
    servicosDeEnergiaOutroEntidadeResponsavel  = models.CharField(max_length=255,blank=True, null=True)
    coletaSeletivaTotalAtendidos  = models.CharField(max_length=255,blank=True, null=True)
    coletaSeletivaDomiciliosAtendidos  = models.CharField(max_length=255,blank=True, null=True)
    coletaSeletivaRuraisAtendidos  = models.CharField(max_length=255,blank=True, null=True)
    coletaSeletivaEntidadeResponsavel  = models.CharField(max_length=255,blank=True, null=True)
    coletaNaoSeletivaTotalAtendidos  = models.CharField(max_length=255,blank=True, null=True)
    coletaNaoSeletivaDomiciliosAtendidos  = models.CharField(max_length=255,blank=True, null=True)
    coletaNaoSeletivaRuraisAtendidos  = models.CharField(max_length=255,blank=True, null=True)
    coletaNaoSeletivaEntidadeResponsavel  = models.CharField(max_length=255,blank=True, null=True)
    coletaSemColetaTotal  = models.CharField(max_length=255,blank=True, null=True)
    coletaSemColetaDomicilios  = models.CharField(max_length=255,blank=True, null=True)
    coletaSemColetaRurais  = models.CharField(max_length=255,blank=True, null=True)
    deposicaoAterroSanitarioTotalAtendidos  = models.CharField(max_length=255,blank=True, null=True)
    deposicaoAterroSanitarioDomiciliosAtendidos  = models.CharField(max_length=255,blank=True, null=True)
    deposicaoAterroSanitarioRuraisAtendidos  = models.CharField(max_length=255,blank=True, null=True)
    deposicaoAterroSanitarioEntidadeResponsavel  = models.CharField(max_length=255,blank=True, null=True)
    deposicaoCompostagemTotalAtendidos  = models.CharField(max_length=255,blank=True, null=True)
    deposicaoCompostagemDomiciliosAtendidos  = models.CharField(max_length=255,blank=True, null=True)
    deposicaoCompostagemRuraisAtendidos  = models.CharField(max_length=255,blank=True, null=True)
    deposicaoCompostagemEntidadeResponsavel  = models.CharField(max_length=255,blank=True, null=True)
    deposicaoACeuAbertoTotalAtendidos  = models.CharField(max_length=255,blank=True, null=True)
    deposicaoACeuAbertoDomiciliosAtendidos = models.CharField(max_length=255,blank=True, null=True)
    deposicaoACeuAbertoRuraisAtendidos  = models.CharField(max_length=255,blank=True, null=True)
    deposicaoACeuAbertoEntidadeResponsavel  = models.CharField(max_length=255,blank=True, null=True)
    deposicaoOutroTotalNome  = models.CharField(max_length=255,blank=True, null=True)
    deposicaoOutroTotalAtendidos  = models.CharField(max_length=255,blank=True, null=True)
    deposicaoOutroDomiciliosAtendidos  = models.CharField(max_length=255,blank=True, null=True)
    deposicaoOutroEntidadeResponsavel  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDeAcoTotalReciclado  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDeAcoEntidadeResponsavel  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDeAluminioTotalReciclado  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDeAluminioEntidadeResponsavel  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDeFerroTotalReciclado  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDeFerroEntidadeResponsavel  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemOutroNome  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemOutroTotalReciclado  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemOutroEntidadeResponsavel  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDeBateriasPilhasTotalReciclado  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDeBateriasPilhasEntidadeResponsavel = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDeBorrachaTotalReciclado  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDeBorrachaEntidadeResponsavel  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDeEletronicosTotalReciclado  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDeEletronicosEntidadeResponsavel = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDeEmbalagensLongaVidaTotalReciclado  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDeEmbalagensLongaVidaEntidadeResponsavel  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDeEntulhoTotalReciclado  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDeEntulhoEntidadeResponsavel  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDeMadeiraTotalReciclado = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDeMadeiraEntidadeResponsavel  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDePapelTotalReciclado = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDePapelEntidadeResponsavel  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDePlasticoEEmbalagensTotalReciclado  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDePlasticoEEmbalagensEntidadeResponsavel = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDeVidroTotalReciclado  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDeVidroEntidadeResponsavel  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDeOleoDeCozinhaTotalReciclado  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDeOleoDeCozinhaEntidadeResponsavel = models.CharField(max_length=255,blank=True, null=True)
    reciclagemOutrosNome  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemOutrosTotalReciclado  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemOutrosEntidadeResponsavel  = models.CharField(max_length=255,blank=True, null=True)
    divulgacaoImpressaFolder  = models.CharField(max_length=255,blank=True, null=True)
    divulgacaoImpressaRevista  = models.CharField(max_length=255,blank=True, null=True)
    divulgacaoImpressaJornal  = models.CharField(max_length=255,blank=True, null=True)
    divulgacaoImpressaOutros  = models.CharField(max_length=255,blank=True, null=True)
    visitantesAno  = models.CharField(max_length=255,blank=True, null=True)
    visitantesAnoAltaTemporada  = models.CharField(max_length=255,blank=True, null=True)
    origemInternacionalAnoBase  = models.CharField(max_length=255,blank=True, null=True)
    atrativosMaisVisitados = models.CharField(max_length=255,blank=True, null=True)
    redeDeEsgoto = models.CharField(max_length=255,blank=True, null=True)
    fossaSeptica  = models.CharField(max_length=255,blank=True, null=True)
    fossaRudimentar  = models.CharField(max_length=255,blank=True, null=True)
    vala  = models.CharField(max_length=255,blank=True, null=True)
    estacaoDeTratamento = models.CharField(max_length=255,blank=True, null=True)
    esgotoTratado  = models.CharField(max_length=255,blank=True, null=True)
    servicoDeEsgotoOutros = models.CharField(max_length=255,blank=True, null=True)
    geradorDeEmergencia  = models.CharField(max_length=255,blank=True, null=True)
    redeUrbana  = models.CharField(max_length=255,blank=True, null=True)
    redeRural  = models.CharField(max_length=255,blank=True, null=True)
    abastecimentoProprio = models.CharField(max_length=255,blank=True, null=True)
    servicosDeEnergiaOutro = models.CharField(max_length=255,blank=True, null=True)
    coletaSeletiva = models.CharField(max_length=255,blank=True, null=True)
    coletaNaoSeletiva = models.CharField(max_length=255,blank=True, null=True)
    coletaSemColeta  = models.CharField(max_length=255,blank=True, null=True)
    deposicaoAterroSanitario = models.CharField(max_length=255,blank=True, null=True)
    deposicaoCompostagem  = models.CharField(max_length=255,blank=True, null=True)
    deposicaoACeuAberto  = models.CharField(max_length=255,blank=True, null=True)
    deposicaoOutro  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDeAco  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDeAluminio = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDeFerro  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemOutro  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDeBateriasPilhas = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDeBorracha  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDeEletronicos = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDeEmbalagensLongaVida = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDeEntulho  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDeMadeira  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDePapel  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDePlasticoEEmbalagens = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDeVidro = models.CharField(max_length=255,blank=True, null=True)
    reciclagemDeOleoDeCozinha  = models.CharField(max_length=255,blank=True, null=True)
    reciclagemOutros  = models.CharField(max_length=255,blank=True, null=True)
    servicosDeComunicacaoTelefoniaMovel  = models.CharField(max_length=255,blank=True, null=True)
    servicosDeComunicacaoTelefoniaFixa  = models.CharField(max_length=255,blank=True, null=True)
    promocaoTuristicaDivulgacaoImpressa  = models.CharField(max_length=255,blank=True, null=True)
    promocaoTuristicaDivulgacaoTelevisiva  = models.CharField(max_length=255,blank=True, null=True)
    mesesMaisFrios = models.JSONField(blank=True, null=True)
    mesesMaisQuentes  = models.JSONField(blank=True, null=True)
    mesesMaisChuvosos  = models.JSONField(blank=True, null=True)
    mesesMenosChuvosos  = models.JSONField(blank=True, null=True)
    tipoDeAbastecimento  = models.CharField(max_length=255,blank=True, null=True)
    energiaEletrica  = models.CharField(max_length=255,blank=True, null=True)
    servicosDeComunicacaoAcessoAInternet  = models.CharField(max_length=255,blank=True, null=True)
    telefoniaFixaAreaDeCobertura = models.CharField(max_length=255,blank=True, null=True)
    telefoniaMovelAreaDeCobertura = models.CharField(max_length=255,blank=True, null=True)
    atendimentoEmLinguaEstrangeira  = models.CharField(max_length=255,blank=True, null=True)
    atendimentoAoVisitanteInformativosImpressos  = models.CharField(max_length=255,blank=True, null=True)
    mesesAltaTemporada  = models.JSONField(blank=True, null=True)
    origemDosVisitantesTuristas  = models.JSONField(blank=True, null=True)
    origemNacional  = models.JSONField(blank=True, null=True)
    origemInternacional  = models.JSONField(blank=True, null=True)
    segmentosTurismoEspecializado  = models.JSONField(blank=True, null=True)
    leiOrganica   = models.CharField(max_length=255,blank=True, null=True)
    ocupacaoDoSolo  = models.CharField(max_length=255,blank=True, null=True)
    planoDeDesenvolvimentoDoTurismo   = models.CharField(max_length=255,blank=True, null=True)
    protecaoAmbiental  = models.CharField(max_length=255,blank=True, null=True)
    apoioACultura   = models.CharField(max_length=255,blank=True, null=True)
    incentivosFiscaisAoTurismo   = models.CharField(max_length=255,blank=True, null=True)
    planoDiretor = models.CharField(max_length=255,blank=True, null=True)
    fundoMunicipalDeTurismo  = models.CharField(max_length=255,blank=True, null=True)
    legislacaoOutras  = models.CharField(max_length=255,blank=True, null=True)
    
class ComercioTuristico(Base):
     latitude = models.CharField(max_length=255,blank=True, null=True)
     longitude = models.CharField(max_length=255,blank=True, null=True)
     sinalizacaoDeAcesso =  models.CharField(max_length=255,blank=True, null=True)
     sinalizacaoTuristica = models.CharField(max_length=255,blank=True, null=True)
     subtipo =  models.JSONField(blank=True, null=True) 
     natureza =  models.CharField(max_length=255,blank=True, null=True) 
     tipoDeOrganizacao =  models.CharField(max_length=255,blank=True, null=True) 
     localizacao =  models.CharField(max_length=255,blank=True, null=True) 
     razaoSocial = models.CharField(max_length=255,blank=True, null=True)  
     nomeFantasia = models.CharField(max_length=255,blank=True, null=True)  
     CNPJ =  models.CharField(max_length=255,blank=True, null=True) 
     codigoCNAE =  models.CharField(max_length=255,blank=True, null=True) 
     atividadeEconomica = models.CharField(max_length=255,blank=True, null=True)  
     inscricaoMunicipal =  models.CharField(max_length=255,blank=True, null=True) 
     nomeDaRedeFranquia =  models.CharField(max_length=255,blank=True, null=True) 
     avenidaRuaTravessa =  models.CharField(max_length=255,blank=True, null=True) 
     bairroLocalidade =   models.CharField(max_length=255,blank=True, null=True)
     distrito =   models.CharField(max_length=255,blank=True, null=True)
     CEP =   models.CharField(max_length=255,blank=True, null=True)
     whatsapp =   models.CharField(max_length=255,blank=True, null=True)
     instagram =   models.CharField(max_length=255,blank=True, null=True)
     email =   models.CharField(max_length=255,blank=True, null=True)
     site =   models.CharField(max_length=255,blank=True, null=True)
     pontosDeReferencia =   models.CharField(max_length=255,blank=True, null=True)
     outrasRegrasEInformacoes = models.CharField(max_length=255,blank=True, null=True)  
     capacidadeDeVeiculos =   models.CharField(max_length=255,blank=True, null=True)
     automoveis =   models.CharField(max_length=255,blank=True, null=True)
     onibus =   models.CharField(max_length=255,blank=True, null=True)
     outrasAcessibilidade = models.CharField(max_length=255,blank=True, null=True)
     funcionamento24h =  models.CharField(max_length=255,blank=True, null=True)
     funcionamentoEmFeriados =  models.CharField(max_length=255,blank=True, null=True)
     formasDePagamento =  models.JSONField(blank=True, null=True)
     atendimentoEmLinguaEstrangeira =   models.CharField(max_length=255,blank=True, null=True)
     informativosImpressos = models.JSONField(blank=True, null=True)
     regrasDeFuncionamentoPeriodo =   models.JSONField(blank=True, null=True)
     estacionamento =   models.CharField(max_length=255,blank=True, null=True)
     produtosEServicos =   models.JSONField(blank=True, null=True)
     outrosServicos =   models.JSONField(blank=True, null=True) 
     doEquipamentoEspaco =   models.CharField(max_length=255,blank=True, null=True)
     areaOuEdificacaoEmQueEstaInstalado =   models.CharField(max_length=255,blank=True, null=True)
     possuiFacilidade =   models.CharField(max_length=255,blank=True, null=True)
     estadoGeralConservacao =   models.CharField(max_length=255,blank=True, null=True)
     sinalizacaoIndicativaPreferencial =   models.CharField(max_length=255,blank=True, null=True)
     pessoalCapacitado =   models.JSONField(blank=True, null=True)
     rotaExternaAcessivel =   models.JSONField(blank=True, null=True)
     simboloInternacionalDeAcesso =   models.JSONField(blank=True, null=True)
     localDeEmbarqueEDesembarque =   models.JSONField(blank=True, null=True)
     vagaEmEstacionamento =   models.JSONField(blank=True, null=True)
     areaDeCirculacao =   models.JSONField(blank=True, null=True)
     escada =   models.JSONField(blank=True, null=True)
     rampa =   models.JSONField(blank=True, null=True)
     piso =   models.JSONField(blank=True, null=True)
     elevador =   models.JSONField(blank=True, null=True)
     equipamentoMotorizado =   models.JSONField(blank=True, null=True)
     sinalizacaoVisual =   models.JSONField(blank=True, null=True)
     sinalizacaoTatil =   models.JSONField(blank=True, null=True)
     alarmeDeEmergencia =   models.JSONField(blank=True, null=True)
     comunicacao =   models.JSONField(blank=True, null=True)
     balcaoDeAtendimento =   models.JSONField(blank=True, null=True)
     mobiliario =   models.JSONField(blank=True, null=True)
     sanitario =   models.JSONField(blank=True, null=True)
     telefone =   models.JSONField(blank=True, null=True)
     tabelEquipamentoEEspaco =  models.JSONField(blank=True, null=True)
     tabelaAreaOuEdificacao = models.JSONField(blank=True, null=True)
     tabelaHorarios = models.JSONField(blank=True, null=True)

class AgenciaDeTurismo(Base):
    segmentosEspecializado = models.JSONField(null=True, blank=True)
    latitude = models.CharField(max_length=255,blank=True, null=True)
    longitude = models.CharField(max_length=255,blank=True, null=True)
    displayName = models.CharField(max_length=255,blank=True, null=True)
    rua = models.CharField(max_length=255,blank=True, null=True)
    bairro = models.CharField(max_length=255,blank=True, null=True)
    cidade = models.CharField(max_length=255,blank=True, null=True)
    estado = models.CharField(max_length=255,blank=True, null=True)
    pais = models.CharField(max_length=255,blank=True, null=True)
    razaoSocial = models.CharField(max_length=255, null=True, blank=True)
    nomeFantasia = models.CharField(max_length=255, null=True, blank=True)
    CNPJ = models.CharField(max_length=255, null=True, blank=True)
    codigoCNAE = models.CharField(max_length=255, null=True, blank=True)
    atividadeEconomica =models.CharField(max_length=255, null=True, blank=True)
    inscricaoMunicipal = models.CharField(max_length=255, null=True, blank=True)
    nomeDaRede =models.CharField(max_length=255, null=True, blank=True)

    natureza = models.CharField(max_length=255, null=True, blank=True)
    tipoDeOrganizacaoInstituicao = models.JSONField(null=True, blank=True)
    inicioDaAtividade = models.CharField(max_length=255, null=True, blank=True)
    qtdeFuncionariosPermanentes = models.CharField(max_length=255, null=True, blank=True)
    qtdeFuncionariosTemporarios = models.CharField(max_length=255, null=True, blank=True)
    qtdeFuncionariosComDeficiencia = models.CharField(max_length=255, null=True, blank=True)
    localizacao = models.CharField(max_length=255, null=True, blank=True)
    avenidaRuaEtc = models.CharField(max_length=255, null=True, blank=True)
    bairroLocalidade = models.CharField(max_length=255, null=True, blank=True)
    distrito = models.CharField(max_length=255, null=True, blank=True)
    CEP = models.CharField(max_length=255, null=True, blank=True)

    
    whatsapp = models.CharField(max_length=50, null=True, blank=True)
    instagram = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=50, null=True, blank=True)
    sinalizacaoDeAcesso = models.CharField(max_length=50, null=True, blank=True)
    sinalizacaoTuristica = models.CharField(max_length=50, null=True, blank=True)

    proximidades = models.JSONField(null=True, blank=True)

    distanciasAeroporto = models.CharField(max_length=255, null=True, blank=True)
    distanciasRodoviaria  = models.CharField(max_length=255, null=True, blank=True)
    distanciaEstacaoFerroviaria  = models.CharField(max_length=255, null=True, blank=True)
    distanciaEstacaoMaritima  = models.CharField(max_length=255, null=True, blank=True)
    distanciaEstacaoMetroviaria  = models.CharField(max_length=255, null=True, blank=True)
    distanciaPontoDeOnibus  = models.CharField(max_length=255, null=True, blank=True)
    distanciaPontoDeTaxi  = models.CharField(max_length=255, null=True, blank=True)
    distanciasOutraNome  = models.CharField(max_length=255, null=True, blank=True)
    distanciaOutras  = models.CharField(max_length=255, null=True, blank=True)

    pontosDeReferencia  = models.CharField(max_length=255, null=True, blank=True)

    tabelaMTUR = models.JSONField(null=True, blank=True)

    formasDePagamento = models.JSONField(null=True, blank=True)
    atendimentoEmLinguasEstrangeiras = models.JSONField(null=True, blank=True)
    informativosImpressos = models.JSONField(null=True, blank=True)

    periodo = models.JSONField(null=True, blank=True)
    tabelasHorario = models.JSONField(null=True, blank=True)

    funcionamento24h = models.CharField(max_length=255, null=True, blank=True)
    funcionamentoEmFeriados = models.CharField(max_length=255, null=True, blank=True)
    totalVendasEmissivos = models.CharField(max_length=255, null=True, blank=True)
    totalVendasReceptivos = models.CharField(max_length=255, null=True, blank=True)
    outrasRegrasEInformacoes  = models.CharField(max_length=255, null=True, blank=True)
    anoBaseEmissivos  = models.CharField(max_length=255, null=True, blank=True)
    origemEmissivosInternacionais = models.JSONField( blank=True, null=True)
    origemEmissivosNacionais = models.JSONField( blank=True, null=True)
    destinosEmissivosNacionais = models.JSONField( blank=True, null=True)
    destinosEmissivosInternacionais = models.JSONField(blank=True,null=True)
    vendasAltaTemporada = models.CharField(max_length=255, null=True, blank=True)
    vendasBaixaTemporada = models.CharField(max_length=255, null=True, blank=True)
    mesesAltaTemporada  = models.JSONField(null=True, blank=True)
    mesesBaixaTemporada  = models.JSONField(null=True, blank=True)
    cambio = models.CharField(max_length=255, null=True, blank=True)

    bilhetesTerrestres = models.JSONField(null=True, blank=True)
    bilhetesAereos = models.JSONField(null=True, blank=True)
    pacotesTuristicos = models.JSONField(null=True, blank=True)
    cruzeirosMaritimos = models.JSONField(null=True, blank=True)
    meiosDeHospedagem = models.JSONField(null=True, blank=True)
    servicosTraslados = models.JSONField(null=True, blank=True)
    seguroDeViagem = models.JSONField(null=True, blank=True)
    locacaoDeAutomoveis = models.JSONField(null=True, blank=True)
    servicosBasicosOutros = models.CharField(max_length=255, null=True, blank=True)
    apoioADespachos = models.CharField(max_length=255, null=True, blank=True)
    servicosEAtividadesEspecializadas = models.JSONField(null=True, blank=True)
    transporteTerrestre = models.CharField(max_length=255, null=True, blank=True)
    aumovelDePasseio = models.CharField(max_length=255, null=True, blank=True)
    buggy = models.CharField(max_length=255, null=True, blank=True)
    motocicleta = models.CharField(max_length=255, null=True, blank=True)
    caminhao = models.CharField(max_length=255, null=True, blank=True)
    caminhonete = models.CharField(max_length=255, null=True, blank=True)
    onibus = models.CharField(max_length=255, null=True, blank=True)
    utilitario = models.CharField(max_length=255, null=True, blank=True)
    trem = models.CharField(max_length=255, null=True, blank=True)
    outrosTipoVeiculo = models.CharField(max_length=255, null=True, blank=True)
    totalDeVeiculos = models.CharField(max_length=255, null=True, blank=True)
    totalDeVeiculosAdaptados = models.CharField(max_length=255, null=True, blank=True)
    tipoDeServico = models.JSONField(null=True, blank=True)
    transporteAquatico = models.CharField(max_length=255, null=True, blank=True)
    iate = models.CharField(max_length=255, null=True, blank=True)
    chalana = models.CharField(max_length=255, null=True, blank=True)
    navio = models.CharField(max_length=255, null=True, blank=True)
    saveiro = models.CharField(max_length=255, null=True, blank=True)
    escuna = models.CharField(max_length=255, null=True, blank=True)
    jangada = models.CharField(max_length=255, null=True, blank=True)
    traineira = models.CharField(max_length=255, null=True, blank=True)
    catarama = models.CharField(max_length=255, null=True, blank=True)
    veleiro = models.CharField(max_length=255, null=True, blank=True)
    ferryBoat = models.CharField(max_length=255, null=True, blank=True)
    lancha = models.CharField(max_length=255, null=True, blank=True)
    outrosEmbarcacao = models.CharField(max_length=255, null=True, blank=True)
    totalDeVeiculosAquaticos = models.CharField(max_length=255, null=True, blank=True)
    totalDeVeiculosAquaticosAdaptados = models.CharField(max_length=255, null=True, blank=True)
    tipoDeServicoAquatico = models.JSONField(null=True, blank=True)
    caracterizacaoServico = models.CharField(max_length=255, null=True, blank=True)
    transporteAereo = models.CharField(max_length=255, null=True, blank=True)
    helicoptero = models.CharField(max_length=255, null=True, blank=True)
    aviao = models.CharField(max_length=255, null=True, blank=True)
    outrosAeronave = models.CharField(max_length=255, null=True, blank=True)
    totalDeVeiculosAeronaves = models.CharField(max_length=255, null=True, blank=True)
    totalDeVeiculosAeronavesAdaptados = models.CharField(max_length=255, null=True, blank=True)
    tipoDeServicoAeronave = models.JSONField(null=True, blank=True)

    doEquipamento = models.CharField(max_length=255, null=True, blank=True)
    areaOuEdificacao = models.CharField(max_length=255, null=True, blank=True)
    tabelaEquipamentoEEspaco = models.JSONField(null=True, blank=True)

    estadoGeralDeConservacao = models.CharField(max_length=255, null=True, blank=True)

    possuiFacilidade = models.CharField(max_length=255, null=True, blank=True)

    pessoalCapacitadoParaReceberPCD = models.JSONField(null=True, blank=True)

    rotaExternaAcessível  = models.JSONField(null=True, blank=True)

    simboloInternacionalDeAcesso  = models.JSONField(null=True, blank=True)

    localDeEmbarqueEDesembarque  = models.JSONField(null=True, blank=True)

    vagaEmEstacionamento  = models.JSONField(null=True, blank=True)

    areaDeCirculacaoAcessoInternoParaCadeiraDeRodas  = models.JSONField(null=True, blank=True)

    escada  = models.JSONField(null=True, blank=True)

    rampa  = models.JSONField(null=True, blank=True)

    piso  = models.JSONField(null=True, blank=True)

    elevador =  models.JSONField(null=True, blank=True)

    equipamentoMotorizadoParaDeslocamentoInterno = models.JSONField(null=True, blank=True)

    sinalizacaoVisual = models.JSONField(null=True, blank=True)

    sinalizacaoTatil = models.JSONField(null=True, blank=True)

    alarmeDeEmergencia = models.JSONField(null=True, blank=True)

    comunicacao = models.JSONField(null=True, blank=True)

    balcaoDeAtendimento = models.JSONField(null=True, blank=True)

    mobiliario = models.JSONField(null=True, blank=True)

    sanitario = models.JSONField(null=True, blank=True)

    telefone = models.JSONField(null=True, blank=True)

    sinalizacaoIndicativa = models.CharField(max_length=255, null=True, blank=True)
    
    tabelaAreaOuEdificacao = models.JSONField(blank=True, null=True)
    rotaExternaAcessivel = models.JSONField("Rota Externa Acessível",blank=True, null=True)

    outrosAcessibilidade = models.CharField(max_length=255, null=True, blank=True)

class TransporteTuristico(Base):
    latitude = models.CharField(max_length=255,blank=True, null=True)
    longitude = models.CharField(max_length=255,blank=True, null=True)
    displayName = models.CharField(max_length=255,blank=True, null=True)
    rua = models.CharField(max_length=255,blank=True, null=True)
    bairro = models.CharField(max_length=255,blank=True, null=True)
    cidade = models.CharField(max_length=255,blank=True, null=True)
    estado = models.CharField(max_length=255,blank=True, null=True)
    pais = models.CharField(max_length=255,blank=True, null=True)
    razaoSocial = models.CharField(max_length=255, null=True, blank=True)
    nomeFantasia = models.CharField(max_length=255, null=True, blank=True)
    CNPJ = models.CharField(max_length=255, null=True, blank=True)
    codigoCNAE = models.CharField(max_length=255, null=True, blank=True)
    atividadeEconomica =models.CharField(max_length=255, null=True, blank=True)
    inscricaoMunicipal = models.CharField(max_length=255, null=True, blank=True)
    nomeDaRede =models.CharField(max_length=255, null=True, blank=True)

    natureza = models.CharField(max_length=255, null=True, blank=True)
    tipoDeOrganizacaoInstituicao = models.JSONField(null=True, blank=True)
    inicioDaAtividade = models.CharField(max_length=255, null=True, blank=True)
    qtdeFuncionariosPermanentes = models.CharField(max_length=255, null=True, blank=True)
    qtdeFuncionariosTemporarios = models.CharField(max_length=255, null=True, blank=True)
    qtdeFuncionariosComDeficiencia = models.CharField(max_length=255, null=True, blank=True)
    localizacao = models.CharField(max_length=255, null=True, blank=True)
    avenidaRuaEtc = models.CharField(max_length=255, null=True, blank=True)
    bairroLocalidade = models.CharField(max_length=255, null=True, blank=True)
    distrito = models.CharField(max_length=255, null=True, blank=True)
    CEP = models.CharField(max_length=255, null=True, blank=True)
    mediaAnualPassageiros = models.CharField(max_length=255, null=True, blank=True)
    entidadeAmbitoMunicipal = models.CharField(max_length=255, null=True, blank=True) 
    categoriaAmbitoMunicipal = models.CharField(max_length=255, null=True, blank=True) 
    entidadeAmbitoEstadual = models.CharField(max_length=255, null=True, blank=True) 
    categoriaAmbitoEstadual = models.CharField(max_length=255, null=True, blank=True) 
    entidadeAmbitoFederal = models.CharField(max_length=255, null=True, blank=True) 
    categoriaAmbitoFederal = models.CharField(max_length=255, null=True, blank=True) 
    entidadeAmbitoInternacional = models.CharField(max_length=255, null=True, blank=True) 
    categoriaAmbitoInternacional = models.CharField(max_length=255, null=True, blank=True) 
    abrangencia = models.CharField(max_length=255, null=True, blank=True)
    whatsapp = models.CharField(max_length=50, null=True, blank=True)
    instagram = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=50, null=True, blank=True)
    sinalizacaoDeAcesso = models.CharField(max_length=50, null=True, blank=True)
    sinalizacaoTuristica = models.CharField(max_length=50, null=True, blank=True)

    proximidades = models.JSONField(null=True, blank=True)



    distanciasAeroporto = models.CharField(max_length=255, null=True, blank=True)
    distanciasRodoviaria  = models.CharField(max_length=255, null=True, blank=True)
    distanciaEstacaoFerroviaria  = models.CharField(max_length=255, null=True, blank=True)
    distanciaEstacaoMaritima  = models.CharField(max_length=255, null=True, blank=True)
    distanciaEstacaoMetroviaria  = models.CharField(max_length=255, null=True, blank=True)
    distanciaPontoDeOnibus  = models.CharField(max_length=255, null=True, blank=True)
    distanciaPontoDeTaxi  = models.CharField(max_length=255, null=True, blank=True)
    distanciasOutraNome  = models.CharField(max_length=255, null=True, blank=True)
    distanciaOutras  = models.CharField(max_length=255, null=True, blank=True)

    pontosDeReferencia  = models.CharField(max_length=255, null=True, blank=True)

    tabelaMTUR = models.JSONField(null=True, blank=True)

    formasDePagamento = models.JSONField(null=True, blank=True)
    atendimentoEmLinguasEstrangeiras = models.JSONField(null=True, blank=True)
    informativosImpressos = models.JSONField(null=True, blank=True)

    periodo = models.JSONField(null=True, blank=True)
    tabelasHorario = models.JSONField(null=True, blank=True)
    outrosServicos = models.JSONField(null=True, blank=True)
    idadeMediaVeiculos = models.CharField(max_length=255, null=True, blank=True)
    quantidadeVeiculosAdaptados = models.CharField(max_length=255, null=True, blank=True)

    funcionamento24h = models.CharField(max_length=255, null=True, blank=True)
    funcionamentoEmFeriados = models.CharField(max_length=255, null=True, blank=True)
    outrasRegrasEInformacoes  = models.CharField(max_length=255, null=True, blank=True)
    transporteTerrestre = models.CharField(max_length=255, null=True, blank=True)
    aumovelDePasseio = models.CharField(max_length=255, null=True, blank=True)
    buggy = models.CharField(max_length=255, null=True, blank=True)
    motocicleta = models.CharField(max_length=255, null=True, blank=True)
    caminhao = models.CharField(max_length=255, null=True, blank=True)
    caminhonete = models.CharField(max_length=255, null=True, blank=True)
    onibus = models.CharField(max_length=255, null=True, blank=True)
    utilitario = models.CharField(max_length=255, null=True, blank=True)
    trem = models.CharField(max_length=255, null=True, blank=True)
    outrosTipoVeiculo = models.CharField(max_length=255, null=True, blank=True)
    totalDeVeiculos = models.CharField(max_length=255, null=True, blank=True)
    totalDeVeiculosAdaptados = models.CharField(max_length=255, null=True, blank=True)
    tipoDeServico = models.JSONField(null=True, blank=True)
    transporteAquatico = models.CharField(max_length=255, null=True, blank=True)
    iate = models.CharField(max_length=255, null=True, blank=True)
    chalana = models.CharField(max_length=255, null=True, blank=True)
    navio = models.CharField(max_length=255, null=True, blank=True)
    saveiro = models.CharField(max_length=255, null=True, blank=True)
    escuna = models.CharField(max_length=255, null=True, blank=True)
    jangada = models.CharField(max_length=255, null=True, blank=True)
    traineira = models.CharField(max_length=255, null=True, blank=True)
    catarama = models.CharField(max_length=255, null=True, blank=True)
    veleiro = models.CharField(max_length=255, null=True, blank=True)
    ferryBoat = models.CharField(max_length=255, null=True, blank=True)
    lancha = models.CharField(max_length=255, null=True, blank=True)
    outrosEmbarcacao = models.CharField(max_length=255, null=True, blank=True)
    totalDeVeiculosAquaticos = models.CharField(max_length=255, null=True, blank=True)
    totalDeVeiculosAquaticosAdaptados = models.CharField(max_length=255, null=True, blank=True)
    tipoDeServicoAquatico = models.JSONField(null=True, blank=True)
    caracterizacaoServico = models.CharField(max_length=255, null=True, blank=True)
    transporteAereo = models.CharField(max_length=255, null=True, blank=True)
    helicoptero = models.CharField(max_length=255, null=True, blank=True)
    aviao = models.CharField(max_length=255, null=True, blank=True)
    outrosAeronave = models.CharField(max_length=255, null=True, blank=True)
    totalDeVeiculosAeronaves = models.CharField(max_length=255, null=True, blank=True)
    totalDeVeiculosAeronavesAdaptados = models.CharField(max_length=255, null=True, blank=True)
    tipoDeServicoAeronave = models.JSONField(null=True, blank=True)

    doEquipamento = models.CharField(max_length=255, null=True, blank=True)
    areaOuEdificacao = models.CharField(max_length=255, null=True, blank=True)
    tabelaEquipamentoEEspaco = models.JSONField(null=True, blank=True)

    estadoGeralDeConservacao = models.CharField(max_length=255, null=True, blank=True)

    possuiFacilidade = models.CharField(max_length=255, null=True, blank=True)

    pessoalCapacitadoParaReceberPCD = models.JSONField(null=True, blank=True)

    rotaExternaAcessível  = models.JSONField(null=True, blank=True)

    simboloInternacionalDeAcesso  = models.JSONField(null=True, blank=True)

    localDeEmbarqueEDesembarque  = models.JSONField(null=True, blank=True)

    vagaEmEstacionamento  = models.JSONField(null=True, blank=True)

    areaDeCirculacaoAcessoInternoParaCadeiraDeRodas  = models.JSONField(null=True, blank=True)

    escada  = models.JSONField(null=True, blank=True)

    rampa  = models.JSONField(null=True, blank=True)

    piso  = models.JSONField(null=True, blank=True)

    elevador =  models.JSONField(null=True, blank=True)

    equipamentoMotorizadoParaDeslocamentoInterno = models.JSONField(null=True, blank=True)

    sinalizacaoVisual = models.JSONField(null=True, blank=True)

    sinalizacaoTatil = models.JSONField(null=True, blank=True)

    alarmeDeEmergencia = models.JSONField(null=True, blank=True)

    comunicacao = models.JSONField(null=True, blank=True)

    balcaoDeAtendimento = models.JSONField(null=True, blank=True)

    mobiliario = models.JSONField(null=True, blank=True)

    sanitario = models.JSONField(null=True, blank=True)

    telefone = models.JSONField(null=True, blank=True)

    sinalizacaoIndicativa = models.CharField(max_length=255, null=True, blank=True)
    
    tabelaAreaOuEdificacao = models.JSONField(blank=True, null=True)
    rotaExternaAcessivel = models.JSONField("Rota Externa Acessível",blank=True, null=True)
    vendasEReservas = models.JSONField(null=True, blank=True)

    outrosAcessibilidade = models.CharField(max_length=255, null=True, blank=True)

class EspacoParaEventos(Base):

    sinalizacaoDeAcesso = models.CharField("Sinalização de Acesso",max_length=255,blank=True, null=True)
    sinalizacaoTuristica = models.CharField("Sinalização Turística",max_length=255,blank=True, null=True)
    funcionamento24h = models.CharField("Funcionamento 24h",max_length=255,blank=True, null=True)
    funcionamentoEmFeriados = models.CharField("Funcionamento em Feriados",max_length=255,blank=True, null=True)
    geradorDeEmergencia = models.CharField("Gerador de Emergência",max_length=255,blank=True, null=True)
    
    # Infraestrutura e localização do equipamento/edificação
    doEquipamentoEspaco = models.TextField("Do Equipamento/Espaço", blank=True, null=True)
    daAreaOuEdificacaoEmQueEstaLocalizado = models.TextField("Da Área/Edificação em que Está Localizado", blank=True, null=True)
    possuiFacilidade = models.CharField("Possui Facilidade",max_length=255,blank=True, null=True)
    sinalizacaoIndicativa = models.CharField("Sinalização Indicativa", max_length=255,blank=True, null=True)
    tipoDeOrganizacao = models.JSONField("Tipo de Organização",blank=True, null=True)
    proximidades = models.JSONField("Proximidades",blank=True, null=True)
    
    # Dados relacionados ao turismo e pagamentos
    formasDePagamento = models.JSONField("Formas de Pagamento",blank=True, null=True)
    reservas = models.JSONField("Reservas",blank=True, null=True)
    atendimentoEmLinguaEstrangeira = models.JSONField("Atendimento em Língua Estrangeira",blank=True, null=True)
    informativosImpressos = models.JSONField("Informativos Impressos",blank=True, null=True)
    restricoes = models.JSONField("Restrições",blank=True, null=True)
    mesesAltaTemporada = models.JSONField("Meses de Alta Temporada",blank=True, null=True)


    sanitarioEspec = models.CharField(max_length=255,blank=True, null=True)
    chuveiroQuente = models.CharField(max_length=255,blank=True, null=True)
    chuveiroFrio = models.CharField(max_length=255,blank=True, null=True)
    piaParaLouca = models.CharField(max_length=255,blank=True, null=True)


    # Produtos e serviços
    estacionamento = models.JSONField("Estacionamento",blank=True, null=True)
    lanchonete = models.JSONField("Lanchonete",blank=True, null=True)
    servicos = models.JSONField("Serviços",blank=True, null=True)
    equipamentos = models.JSONField("Equipamentos",blank=True, null=True)
    facilidadesEServicos = models.JSONField("Facilidades e Serviços",blank=True, null=True)
    facilidadesParaExecutivos = models.JSONField("Facilidades para Executivos",blank=True, null=True)
    pessoalCapacitadoParaReceberPCD = models.JSONField("Pessoal Capacitado para Receber PCD",blank=True, null=True)
    
    # Acessibilidade
    rotaExternaAcessivel = models.JSONField("Rota Externa Acessível",blank=True, null=True)
    simboloInternacionalDeAcesso = models.JSONField("Símbolo Internacional de Acesso",blank=True, null=True)
    localDeEmbarqueEDesembarque = models.JSONField("Local de Embarque e Desembarque",blank=True, null=True)
    vagaEmEstacionamento = models.JSONField("Vaga em Estacionamento",blank=True, null=True)
    areaDeCirculacaoAcessoInterno = models.JSONField("Área de Circulação/Acesso Interno",blank=True, null=True)
    escada = models.JSONField("Escada",blank=True, null=True)
    rampa = models.JSONField("Rampa",blank=True, null=True)
    piso = models.JSONField("Piso",blank=True, null=True)
    elevador = models.JSONField("Elevador",blank=True, null=True)
    equipamentoMotorizadoParaDeslocamentoInterno = models.JSONField("Equipamento Motorizado para Deslocamento Interno",blank=True, null=True)
    sinalizacaoVisual = models.JSONField("Sinalização Visual",blank=True, null=True)
    sinalizacaoTatil = models.JSONField("Sinalização Tátil",blank=True, null=True)
    alarmeDeEmergencia = models.JSONField("Alarme de Emergência",blank=True, null=True)
    comunicacao = models.JSONField("Comunicação",blank=True, null=True)
    balcaoDeAtendimento = models.JSONField("Balcão de Atendimento",blank=True, null=True)
    mobiliario = models.JSONField("Mobiliário",blank=True, null=True)
    sanitario = models.JSONField("Sanitário",blank=True, null=True)
    telefone = models.JSONField("Telefone",blank=True, null=True)
    
    # Classificação e localização do meio de hospedagem
    subtipo = models.JSONField(blank=True, null=True)
    natureza = models.CharField("Natureza", max_length=255, blank=True, null=True)
    localizacao = models.TextField("Localização", blank=True, null=True)
    tipoDeDiaria = models.CharField("Tipo de Diária", max_length=255, blank=True, null=True)
    periodo = models.JSONField(blank=True, null=True)
    tabelasHorario = models.JSONField("Tabelas de Horário",blank=True,null=True)
    estadoGeralDeConservacao = models.CharField("Estado Geral de Conservação", max_length=255, blank=True, null=True)
    
    # Dados de turismo e localização geográfica
    
    # Dados empresariais
    razaoSocial = models.CharField("Razão Social", max_length=255, blank=True, null=True)
    nomeFantasia = models.CharField("Nome Fantasia", max_length=255, blank=True, null=True)
    codigoCNAE = models.CharField("Código CNAE", max_length=50, blank=True, null=True)
    atividadeEconomica = models.TextField("Atividade Econômica", blank=True, null=True)
    inscricaoMunicipal = models.CharField("Inscrição Municipal", max_length=50, blank=True, null=True)
    nomeDaRede = models.CharField("Nome da Rede", max_length=255, blank=True, null=True)
    CNPJ = models.CharField("CNPJ", max_length=20, blank=True, null=True)
    inicioDaAtividade = models.CharField("Início da Atividade",max_length=255, blank=True, null=True)
    
    # Dados de quantitativos e capacidade
    qtdeFuncionariosPermanentes = models.CharField("Qtd. Funcionários Permanentes", max_length = 254, blank=True, null=True)
    qtdeFuncionariosTemporarios = models.CharField("Qtd. Funcionários Temporários", max_length = 254, blank=True, null=True)
    qtdeFuncionarisComDeficiencia = models.CharField("Qtd. Funcionários com Deficiência", max_length = 254, blank=True, null=True)
    latitude = models.CharField(max_length=255,blank=True, null=True)
    longitude = models.CharField(max_length=255,blank=True, null=True)
    
    # Endereço e contato
    avenidaRuaEtc = models.CharField("Avenida/Rua/etc.", max_length=255, blank=True, null=True)
    bairroLocalidade = models.CharField("Bairro/Localidade", max_length=255, blank=True, null=True)
    distrito = models.CharField("Distrito", max_length=255, blank=True, null=True)
    CEP = models.CharField("CEP", max_length=20, blank=True, null=True)
    whatsapp = models.CharField("WhatsApp", max_length=50, blank=True, null=True)
    instagram = models.CharField("Instagram", max_length=100, blank=True, null=True)
    email = models.CharField("Email", max_length=254, blank=True, null=True)
    site = models.CharField("Site", max_length=255,blank=True, null=True)
    pontosDeReferencia = models.TextField("Pontos de Referência", blank=True, null=True)
    
    # Dados de tabelas e informações adicionais
    tabelaMTUR = models.JSONField("Tabela MTUR",blank=True,null=True)
    outrasRegrasEInformacoes = models.TextField("Outras Regras e Informações", blank=True, null=True)
    nAnoOcupacao = models.CharField("Ano de Ocupação", max_length=255,blank=True, null=True)
    nOcupacaoAltaTemporada = models.CharField("Ocupação em Alta Temporada", max_length=255,blank=True, null=True)
    nCapacidadeDeVeiculos = models.CharField("Capacidade de Veículos", max_length = 254, blank=True, null=True)
    nAutomoveis = models.CharField("Número de Automóveis", max_length = 254, blank=True, null=True)
    nOnibus = models.CharField("Número de Ônibus", max_length = 254, blank=True, null=True)
    outrasAcessibilidade = models.CharField(max_length=255,blank=True, null=True)
    
    # Tabelas de instalações e equipamentos/espaços
    tabelaEquipamentoEEspaco = models.JSONField("Tabela Equipamento e Espaço",blank=True,null=True)
    tabelaEquipamentoEEspaco2 = models.JSONField("Tabela Equipamento e Espaço 2",blank=True,null=True )
    
    # Observações e referências
    outros = models.TextField("Outros", blank=True, null=True)
    
    areaTotalConstruida = models.CharField(max_length=255, blank=True, null=True)
    areaLocavel = models.CharField(max_length=255, blank=True, null=True)
    
    quantidadeAreaDeCarga = models.CharField("Quantidade area de carga", max_length=255, blank=True, null=True)
    areaTotalAreaDeCarga = models.CharField("Area total area de carga", max_length=255, blank=True, null=True)
    capacidadeeAreaDeCarga = models.CharField("Capacidadee area de carga", max_length=255, blank=True, null=True)
    quantidadeAreaDeExposicaoCoberta = models.CharField("Quantidade area de exposicao coberta", max_length=255, blank=True, null=True)
    areaTotalAreaDeExposicaoCoberta = models.CharField("Area total area de exposicao coberta", max_length=255, blank=True, null=True)
    capacidadeeAreaDeExposicaoCoberta = models.CharField("Capacidadee area de exposicao coberta", max_length=255, blank=True, null=True)
    quantidadeAreaDeExposicaoNaoCoberta = models.CharField("Quantidade area de exposicao nao coberta", max_length=255, blank=True, null=True)
    areaTotalAreaDeExposicaoNaoCoberta = models.CharField("Area total area de exposicao nao coberta", max_length=255, blank=True, null=True)
    capacidadeeAreaDeExposicaoNaoCoberta = models.CharField("Capacidadee area de exposicao nao coberta", max_length=255, blank=True, null=True)
    quantidadeAreaParaCozinha = models.CharField("Quantidade area para cozinha", max_length=255, blank=True, null=True)
    areaTotalAreaParaCozinha = models.CharField("Area total area para cozinha", max_length=255, blank=True, null=True)
    capacidadeeAreaParaCozinha = models.CharField("Capacidadee area para cozinha", max_length=255, blank=True, null=True)
    quantidadeAuditorio = models.CharField("Quantidade auditorio", max_length=255, blank=True, null=True)
    areaTotalAuditorio = models.CharField("Area total auditorio", max_length=255, blank=True, null=True)
    capacidadeeAuditorio = models.CharField("Capacidadee auditorio", max_length=255, blank=True, null=True) 
    quantidadeBarELanchonete = models.CharField("Quantidade bar e lanchonete", max_length=255, blank=True, null=True)
    areaTotalBarELanchonete = models.CharField("Area total bar e lanchonete", max_length=255, blank=True, null=True)
    capacidadeeBarELanchonete = models.CharField("Capacidadee bar e lanchonete", max_length=255, blank=True, null=True)
    quantidadeCabineDeSom = models.CharField("Quantidade cabine de som", max_length=255, blank=True, null=True)
    areaTotalCabineDeSom = models.CharField("Area total cabine de som", max_length=255, blank=True, null=True)
    capacidadeeCabineDeSom = models.CharField("Capacidadee cabine de som", max_length=255, blank=True, null=True)
    quantidadeElevador = models.CharField("Quantidade elevador", max_length=255, blank=True, null=True)
    areaTotalElevador = models.CharField("Area total elevador", max_length=255, blank=True, null=True)
    capacidadeeElevador = models.CharField("Capacidadee elevador", max_length=255, blank=True, null=True)
    quantidadeEscaninho = models.CharField("Quantidade escaninho", max_length=255, blank=True, null=True)
    areaTotalEscaninho = models.CharField("Area total escaninho", max_length=255, blank=True, null=True)
    capacidadeeEscaninho = models.CharField("Capacidadee escaninho", max_length=255, blank=True, null=True)
    quantidadeEspacoMultiuso = models.CharField("Quantidade espaco multiuso", max_length=255, blank=True, null=True)
    areaTotalEspacoMultiuso = models.CharField("Area total espaco multiuso", max_length=255, blank=True, null=True)
    capacidadeeEspacoMultiuso = models.CharField("Capacidadee espaco multiuso", max_length=255, blank=True, null=True)
    quantidadeInstalacoesSanitarias = models.CharField("Quantidade instalacoes sanitarias", max_length=255, blank=True, null=True)
    areaTotalInstalacoesSanitarias = models.CharField("Area total instalacoes sanitarias", max_length=255, blank=True, null=True)
    capacidadeeInstalacoesSanitarias = models.CharField("Capacidadee instalacoes sanitarias", max_length=255, blank=True, null=True)
    quantidadePavilhaoDeFeiras = models.CharField("Quantidade pavilhao de feiras", max_length=255, blank=True, null=True)
    areaTotalPavilhaoDeFeiras = models.CharField("Area total pavilhao de feiras", max_length=255, blank=True, null=True)
    capacidadeePavilhaoDeFeiras = models.CharField("Capacidadee pavilhao de feiras", max_length=255, blank=True, null=True)
    quantidadePracaDeAlimentacao = models.CharField("Quantidade praca de alimentacao", max_length=255, blank=True, null=True)
    areaTotalPracaDeAlimentacao = models.CharField("Area total praca de alimentacao", max_length=255, blank=True, null=True)
    capacidadeePracaDeAlimentacao = models.CharField("Capacidadee praca de alimentacao", max_length=255, blank=True, null=True)
    quantidadeRestaurante = models.CharField("Quantidade restaurante", max_length=255, blank=True, null=True)
    areaTotalRestaurante = models.CharField("Area total restaurante", max_length=255, blank=True, null=True)
    capacidadeeRestaurante = models.CharField("Capacidadee restaurante", max_length=255, blank=True, null=True)
    quantidadeSala = models.CharField("Quantidade sala", max_length=255, blank=True, null=True)
    areaTotalSala = models.CharField("Area total sala", max_length=255, blank=True, null=True)
    capacidadeeSala = models.CharField("Capacidadee sala", max_length=255, blank=True, null=True)
    quantidadeSalasModulares = models.CharField("Quantidade salas modulares", max_length=255, blank=True, null=True)
    areaTotalSalasModulares = models.CharField("Area total salas modulares", max_length=255, blank=True, null=True)
    capacidadeeSalasModulares = models.CharField("Capacidadee salas modulares", max_length=255, blank=True, null=True)
    quantidadeSistemaDeSom = models.CharField("Quantidade sistema de som", max_length=255, blank=True, null=True)
    areaTotalSistemaDeSom = models.CharField("Area total sistema de som", max_length=255, blank=True, null=True)
    capacidadeeSistemaDeSom = models.CharField("Capacidadee sistema de som", max_length=255, blank=True, null=True)
    quantidadeTeatro = models.CharField("Quantidade teatro", max_length=255, blank=True, null=True)
    areaTotalTeatro = models.CharField("Area total teatro", max_length=255, blank=True, null=True)
    capacidadeeTeatro = models.CharField("Capacidadee teatro", max_length=255, blank=True, null=True)
    quantidadeDetectorDeMetais = models.CharField("Quantidade detector de metais", max_length=255, blank=True, null=True)
    areaTotalDetectorDeMetais = models.CharField("Area total detector de metais", max_length=255, blank=True, null=True)
    capacidadeeDetectorDeMetais = models.CharField("Capacidadee detector de metais", max_length=255, blank=True, null=True)
    quantidadeSaidaDeEmergencia = models.CharField("Quantidade saida de emergencia", max_length=255, blank=True, null=True)
    areaTotalSaidaDeEmergencia = models.CharField("Area total saida de emergencia", max_length=255, blank=True, null=True)
    capacidadeeSaidaDeEmergencia = models.CharField("Capacidadee saida de emergencia", max_length=255, blank=True, null=True)
    quantidadeOutros = models.CharField("Quantidade outros", max_length=255, blank=True, null=True)
    areaTotalOutros = models.CharField("Area total outros", max_length=255, blank=True, null=True)
    capacidadeeOutros = models.CharField("Capacidadee outros", max_length=255, blank=True, null=True)
    cadeiraMovel = models.CharField("Cadeira movel", max_length=255, blank=True, null=True)
    cadeiraMovelQuantidade = models.CharField("Cadeira movel quantidade", max_length=255, blank=True, null=True)
    cadeiraComPrancheta = models.CharField("Cadeira com prancheta", max_length=255, blank=True, null=True)
    cadeiraComPranchetaQuantidade = models.CharField("Cadeira com prancheta quantidade", max_length=255, blank=True, null=True)
    cadeiraComBraco = models.CharField("Cadeira com braco", max_length=255, blank=True, null=True)
    cadeiraComBracoQuantidade = models.CharField("Cadeira com braco quantidade", max_length=255, blank=True, null=True)
    cadeiraSemBraco = models.CharField("Cadeira sem braco", max_length=255, blank=True, null=True)
    cadeiraSemBracoQuantidade = models.CharField("Cadeira sem braco quantidade", max_length=255, blank=True, null=True)
    mesa = models.CharField("Mesa", max_length=255, blank=True, null=True)
    mesaQuantidade = models.CharField("Mesa quantidade", max_length=255, blank=True, null=True)
    poltrona = models.CharField("Poltrona", max_length=255, blank=True, null=True)
    poltronaQuantidade = models.CharField("Poltrona quantidade", max_length=255,blank=True, null=True)
    energiaEletrica = models.CharField(max_length=255, blank=True, null=True)
    capacidadeEmKVA = models.CharField(max_length=255, blank=True, null=True)
    geradorCapacidadeEmKVA = models.CharField(max_length=255, blank=True, null=True)
    outrosOutros = models.CharField(max_length=255, blank=True, null=True)
    equipamentosEServicos = models.JSONField(blank=True, null=True)
    
class ServicosParaEventos(Base):

    sinalizacaoDeAcesso = models.CharField("Sinalização de Acesso",max_length=255,blank=True, null=True)
    sinalizacaoTuristica = models.CharField("Sinalização Turística",max_length=255,blank=True, null=True)
    funcionamento24h = models.CharField("Funcionamento 24h",max_length=255,blank=True, null=True)
    funcionamentoEmFeriados = models.CharField("Funcionamento em Feriados",max_length=255,blank=True, null=True)
    geradorDeEmergencia = models.CharField("Gerador de Emergência",max_length=255,blank=True, null=True)
    
    # Infraestrutura e localização do equipamento/edificação
    doEquipamentoEspaco = models.TextField("Do Equipamento/Espaço", blank=True, null=True)
    daAreaOuEdificacaoEmQueEstaLocalizado = models.TextField("Da Área/Edificação em que Está Localizado", blank=True, null=True)
    possuiFacilidade = models.CharField("Possui Facilidade",max_length=255,blank=True, null=True)
    sinalizacaoIndicativa = models.CharField("Sinalização Indicativa", max_length=255,blank=True, null=True)
    tipoDeOrganizacao = models.JSONField("Tipo de Organização",blank=True, null=True)
    proximidades = models.JSONField("Proximidades",blank=True, null=True)
    
    # Dados relacionados ao turismo e pagamentos
    formasDePagamento = models.JSONField("Formas de Pagamento",blank=True, null=True)
    reservas = models.JSONField("Reservas",blank=True, null=True)
    atendimentoEmLinguaEstrangeira = models.JSONField("Atendimento em Língua Estrangeira",blank=True, null=True)
    informativosImpressos = models.JSONField("Informativos Impressos",blank=True, null=True)
    restricoes = models.JSONField("Restrições",blank=True, null=True)
    mesesAltaTemporada = models.JSONField("Meses de Alta Temporada",blank=True, null=True)


    sanitarioEspec = models.CharField(max_length=255,blank=True, null=True)
    chuveiroQuente = models.CharField(max_length=255,blank=True, null=True)
    chuveiroFrio = models.CharField(max_length=255,blank=True, null=True)
    piaParaLouca = models.CharField(max_length=255,blank=True, null=True)


    # Produtos e serviços
    estacionamento = models.JSONField("Estacionamento",blank=True, null=True)
    lanchonete = models.JSONField("Lanchonete",blank=True, null=True)
    servicos = models.JSONField("Serviços",blank=True, null=True)
    equipamentos = models.JSONField("Equipamentos",blank=True, null=True)
    facilidadesEServicos = models.JSONField("Facilidades e Serviços",blank=True, null=True)
    facilidadesParaExecutivos = models.JSONField("Facilidades para Executivos",blank=True, null=True)
    pessoalCapacitadoParaReceberPCD = models.JSONField("Pessoal Capacitado para Receber PCD",blank=True, null=True)
    
    # Acessibilidade
    rotaExternaAcessivel = models.JSONField("Rota Externa Acessível",blank=True, null=True)
    simboloInternacionalDeAcesso = models.JSONField("Símbolo Internacional de Acesso",blank=True, null=True)
    localDeEmbarqueEDesembarque = models.JSONField("Local de Embarque e Desembarque",blank=True, null=True)
    vagaEmEstacionamento = models.JSONField("Vaga em Estacionamento",blank=True, null=True)
    areaDeCirculacaoAcessoInterno = models.JSONField("Área de Circulação/Acesso Interno",blank=True, null=True)
    escada = models.JSONField("Escada",blank=True, null=True)
    rampa = models.JSONField("Rampa",blank=True, null=True)
    piso = models.JSONField("Piso",blank=True, null=True)
    elevador = models.JSONField("Elevador",blank=True, null=True)
    equipamentoMotorizadoParaDeslocamentoInterno = models.JSONField("Equipamento Motorizado para Deslocamento Interno",blank=True, null=True)
    sinalizacaoVisual = models.JSONField("Sinalização Visual",blank=True, null=True)
    sinalizacaoTatil = models.JSONField("Sinalização Tátil",blank=True, null=True)
    alarmeDeEmergencia = models.JSONField("Alarme de Emergência",blank=True, null=True)
    comunicacao = models.JSONField("Comunicação",blank=True, null=True)
    balcaoDeAtendimento = models.JSONField("Balcão de Atendimento",blank=True, null=True)
    mobiliario = models.JSONField("Mobiliário",blank=True, null=True)
    sanitario = models.JSONField("Sanitário",blank=True, null=True)
    telefone = models.JSONField("Telefone",blank=True, null=True)
    
    # Classificação e localização do meio de hospedagem
    subtipo = models.JSONField(blank=True, null=True)
    natureza = models.CharField("Natureza", max_length=255, blank=True, null=True)
    localizacao = models.TextField("Localização", blank=True, null=True)
    tipoDeDiaria = models.CharField("Tipo de Diária", max_length=255, blank=True, null=True)
    periodo = models.JSONField(blank=True, null=True)
    tabelasHorario = models.JSONField("Tabelas de Horário",blank=True,null=True)
    estadoGeralDeConservacao = models.CharField("Estado Geral de Conservação", max_length=255, blank=True, null=True)
    
    # Dados de turismo e localização geográfica
    
    # Dados empresariais
    razaoSocial = models.CharField("Razão Social", max_length=255, blank=True, null=True)
    nomeFantasia = models.CharField("Nome Fantasia", max_length=255, blank=True, null=True)
    codigoCNAE = models.CharField("Código CNAE", max_length=50, blank=True, null=True)
    atividadeEconomica = models.TextField("Atividade Econômica", blank=True, null=True)
    inscricaoMunicipal = models.CharField("Inscrição Municipal", max_length=50, blank=True, null=True)
    nomeDaRede = models.CharField("Nome da Rede", max_length=255, blank=True, null=True)
    CNPJ = models.CharField("CNPJ", max_length=20, blank=True, null=True)
    inicioDaAtividade = models.CharField("Início da Atividade",max_length=255, blank=True, null=True)
    
    # Dados de quantitativos e capacidade
    qtdeFuncionariosPermanentes = models.CharField("Qtd. Funcionários Permanentes", max_length = 254, blank=True, null=True)
    qtdeFuncionariosTemporarios = models.CharField("Qtd. Funcionários Temporários", max_length = 254, blank=True, null=True)
    qtdeFuncionarisComDeficiencia = models.CharField("Qtd. Funcionários com Deficiência", max_length = 254, blank=True, null=True)
    latitude = models.CharField(max_length=255,blank=True, null=True)
    longitude = models.CharField(max_length=255,blank=True, null=True)
    
    # Endereço e contato
    avenidaRuaEtc = models.CharField("Avenida/Rua/etc.", max_length=255, blank=True, null=True)
    bairroLocalidade = models.CharField("Bairro/Localidade", max_length=255, blank=True, null=True)
    distrito = models.CharField("Distrito", max_length=255, blank=True, null=True)
    CEP = models.CharField("CEP", max_length=20, blank=True, null=True)
    whatsapp = models.CharField("WhatsApp", max_length=50, blank=True, null=True)
    instagram = models.CharField("Instagram", max_length=100, blank=True, null=True)
    email = models.CharField("Email", max_length=254, blank=True, null=True)
    site = models.CharField("Site", max_length=255,blank=True, null=True)
    pontosDeReferencia = models.TextField("Pontos de Referência", blank=True, null=True)
    
    # Dados de tabelas e informações adicionais
    tabelaMTUR = models.JSONField("Tabela MTUR",blank=True,null=True)
    outrasRegrasEInformacoes = models.TextField("Outras Regras e Informações", blank=True, null=True)
    nAnoOcupacao = models.CharField("Ano de Ocupação", max_length=255,blank=True, null=True)
    nOcupacaoAltaTemporada = models.CharField("Ocupação em Alta Temporada", max_length=255,blank=True, null=True)
    nCapacidadeDeVeiculos = models.CharField("Capacidade de Veículos", max_length = 254, blank=True, null=True)
    nAutomoveis = models.CharField("Número de Automóveis", max_length = 254, blank=True, null=True)
    nOnibus = models.CharField("Número de Ônibus", max_length = 254, blank=True, null=True)
    outrasAcessibilidade = models.CharField(max_length=255,blank=True, null=True)
    
    # Tabelas de instalações e equipamentos/espaços
    tabelaEquipamentoEEspaco = models.JSONField("Tabela Equipamento e Espaço",blank=True,null=True)
    tabelaEquipamentoEEspaco2 = models.JSONField("Tabela Equipamento e Espaço 2",blank=True,null=True )
    
    # Observações e referências
    outros = models.TextField("Outros", blank=True, null=True)
    
    equipamentosEServicos = models.JSONField(blank=True, null=True)
    atividadesBasicas = models.JSONField(blank=True, null=True)
      
class Parques(Base):
   
    # Dados do formulário e pesquisador
    
    # Dados do coordenador
    
    # Sinalizações e funcionamento
    sinalizacaoDeAcesso = models.CharField("Sinalização de Acesso",max_length=255,blank=True, null=True)
    sinalizacaoTuristica = models.CharField("Sinalização Turística",max_length=255,blank=True, null=True)
    funcionamento24h = models.CharField("Funcionamento 24h",max_length=255,blank=True, null=True)
    funcionamentoEmFeriados = models.CharField("Funcionamento em Feriados",max_length=255,blank=True, null=True)
    
    # Infraestrutura e localização do equipamento/edificação
    doEquipamentoEspaco = models.TextField("Do Equipamento/Espaço", blank=True, null=True)
    daAreaOuEdificacaoEmQueEstaLocalizado = models.TextField("Da Área/Edificação em que Está Localizado", blank=True, null=True)
    possuiFacilidade = models.CharField("Possui Facilidade",max_length=255,blank=True, null=True)
    sinalizacaoIndicativa = models.CharField("Sinalização Indicativa", max_length=255,blank=True, null=True)
    tipoDeOrganizacao = models.JSONField("Tipo de Organização",blank=True, null=True)
    proximidades = models.JSONField("Proximidades",blank=True, null=True)
    
    # Dados relacionados ao turismo e pagamentos
    formasDePagamento = models.JSONField("Formas de Pagamento",blank=True, null=True)
    reservas = models.JSONField("Reservas",blank=True, null=True)
    atendimentoEmLinguaEstrangeira = models.JSONField("Atendimento em Língua Estrangeira",blank=True, null=True)
    informativosImpressos = models.JSONField("Informativos Impressos",blank=True, null=True)
    restricoes = models.JSONField("Restrições",blank=True, null=True)
    mesesAltaTemporada = models.JSONField("Meses de Alta Temporada",blank=True, null=True)
    origemDosVisitantes = models.JSONField("Origem dos Visitantes",blank=True, null=True)
    
    # Produtos e serviços
    estacionamento = models.JSONField("Estacionamento",blank=True, null=True)
    pessoalCapacitadoParaReceberPCD = models.JSONField("Pessoal Capacitado para Receber PCD",blank=True, null=True)
    
    # Acessibilidade
    rotaExternaAcessivel = models.JSONField("Rota Externa Acessível",blank=True, null=True)
    simboloInternacionalDeAcesso = models.JSONField("Símbolo Internacional de Acesso",blank=True, null=True)
    localDeEmbarqueEDesembarque = models.JSONField("Local de Embarque e Desembarque",blank=True, null=True)
    vagaEmEstacionamento = models.JSONField("Vaga em Estacionamento",blank=True, null=True)
    areaDeCirculacaoAcessoInterno = models.JSONField("Área de Circulação/Acesso Interno",blank=True, null=True)
    escada = models.JSONField("Escada",blank=True, null=True)
    rampa = models.JSONField("Rampa",blank=True, null=True)
    piso = models.JSONField("Piso",blank=True, null=True)
    elevador = models.JSONField("Elevador",blank=True, null=True)
    equipamentoMotorizadoParaDeslocamentoInterno = models.JSONField("Equipamento Motorizado para Deslocamento Interno",blank=True, null=True)
    sinalizacaoVisual = models.JSONField("Sinalização Visual",blank=True, null=True)
    sinalizacaoTatil = models.JSONField("Sinalização Tátil",blank=True, null=True)
    alarmeDeEmergencia = models.JSONField("Alarme de Emergência",blank=True, null=True)
    comunicacao = models.JSONField("Comunicação",blank=True, null=True)
    balcaoDeAtendimento = models.JSONField("Balcão de Atendimento",blank=True, null=True)
    mobiliario = models.JSONField("Mobiliário",blank=True, null=True)
    sanitario = models.JSONField("Sanitário",blank=True, null=True)
    telefone = models.JSONField("Telefone",blank=True, null=True)
    
    # Classificação e localização do meio de hospedagem
    subtipo = models.JSONField(blank=True, null=True)
    natureza = models.CharField("Natureza", max_length=255, blank=True, null=True)
    localizacao = models.TextField("Localização", blank=True, null=True)
    periodo = models.JSONField(blank=True, null=True)
    tabelasHorario = models.JSONField("Tabelas de Horário",blank=True,null=True)
    estadoGeralDeConservacao = models.CharField("Estado Geral de Conservação", max_length=255, blank=True, null=True)
    
    # Dados de turismo e localização geográfica
    estadosTuristas = models.JSONField("Estados Turistas", blank=True, null=True)
    paisesTuristas = models.JSONField("Países Turistas", blank=True,null=True)
    
    # Dados empresariais
    razaoSocial = models.CharField("Razão Social", max_length=255, blank=True, null=True)
    nomeFantasia = models.CharField("Nome Fantasia", max_length=255, blank=True, null=True)
    codigoCNAE = models.CharField("Código CNAE", max_length=50, blank=True, null=True)
    atividadeEconomica = models.TextField("Atividade Econômica", blank=True, null=True)
    inscricaoMunicipal = models.CharField("Inscrição Municipal", max_length=50, blank=True, null=True)
    nomeDaRede = models.CharField("Nome da Rede", max_length=255, blank=True, null=True)
    CNPJ = models.CharField("CNPJ", max_length=20, blank=True, null=True)
    inicioDaAtividade = models.CharField("Início da Atividade",max_length=255, blank=True, null=True)
    
    # Dados de quantitativos e capacidade
    qtdeFuncionariosPermanentes = models.CharField("Qtd. Funcionários Permanentes", max_length = 254, blank=True, null=True)
    qtdeFuncionariosTemporarios = models.CharField("Qtd. Funcionários Temporários", max_length = 254, blank=True, null=True)
    qtdeFuncionarisComDeficiencia = models.CharField("Qtd. Funcionários com Deficiência", max_length = 254, blank=True, null=True)
    latitude = models.CharField(max_length=255,blank=True, null=True)
    longitude = models.CharField(max_length=255,blank=True, null=True)
    
    # Endereço e contato
    avenidaRuaEtc = models.CharField("Avenida/Rua/etc.", max_length=255, blank=True, null=True)
    bairroLocalidade = models.CharField("Bairro/Localidade", max_length=255, blank=True, null=True)
    distrito = models.CharField("Distrito", max_length=255, blank=True, null=True)
    CEP = models.CharField("CEP", max_length=20, blank=True, null=True)
    whatsapp = models.CharField("WhatsApp", max_length=50, blank=True, null=True)
    instagram = models.CharField("Instagram", max_length=100, blank=True, null=True)
    email = models.CharField("Email", max_length=254, blank=True, null=True)
    site = models.CharField("Site", max_length=255,blank=True, null=True)
    pontosDeReferencia = models.TextField("Pontos de Referência", blank=True, null=True)
    
    # Dados de tabelas e informações adicionais
    tabelaMTUR = models.JSONField("Tabela MTUR",blank=True,null=True)
    outrasRegrasEInformacoes = models.TextField("Outras Regras e Informações", blank=True, null=True)
    nAnoOcupacao = models.CharField("Ano de Ocupação", max_length=255,blank=True, null=True)
    nOcupacaoAltaTemporada = models.CharField("Ocupação em Alta Temporada", max_length=255,blank=True, null=True)
    nCapacidadeDeVeiculos = models.CharField("Capacidade de Veículos", max_length = 254, blank=True, null=True)
    nAutomoveis = models.CharField("Número de Automóveis", max_length = 254, blank=True, null=True)
    nOnibus = models.CharField("Número de Ônibus", max_length = 254, blank=True, null=True)
    outrasAcessibilidade = models.CharField(max_length=255,blank=True, null=True)
    
    # Tabelas de instalações e equipamentos/espaços
    tabelaEquipamentoEEspaco = models.JSONField("Tabela Equipamento e Espaço",blank=True,null=True)
    tabelaEquipamentoEEspaco2 = models.JSONField("Tabela Equipamento e Espaço 2",blank=True,null=True )
    
    # Observações e referências
    outros = models.TextField("Outros", blank=True, null=True)
    
    areaTotalDoEstabelecimento = models.CharField(max_length = 254, blank=True, null=True)
    ambientacaoTematica = models.CharField(max_length = 254, blank=True, null=True)
    entidadeManetedora = models.CharField(max_length = 254, blank=True, null=True)
    entidadeManetedoraEmail = models.CharField(max_length = 254, blank=True, null=True)
    entidadeManetedoraSite = models.CharField(max_length = 254, blank=True, null=True)
    entradaGratuita = models.CharField(max_length = 254, blank=True, null=True)
    entradaPaga = models.CharField(max_length = 254, blank=True, null=True)
    outrasIntalacoes = models.JSONField(blank=True,null=True)
    outrosEquipamentosEEspacos = models.JSONField(blank=True,null=True)
       
class EspacosDeDiversaoECultura(Base):
   
    # Dados do formulário e pesquisador
    
    # Dados do coordenador
    
    # Sinalizações e funcionamento
    sinalizacaoDeAcesso = models.CharField("Sinalização de Acesso",max_length=255,blank=True, null=True)
    sinalizacaoTuristica = models.CharField("Sinalização Turística",max_length=255,blank=True, null=True)
    funcionamento24h = models.CharField("Funcionamento 24h",max_length=255,blank=True, null=True)
    funcionamentoEmFeriados = models.CharField("Funcionamento em Feriados",max_length=255,blank=True, null=True)
    
    # Infraestrutura e localização do equipamento/edificação
    doEquipamentoEspaco = models.TextField("Do Equipamento/Espaço", blank=True, null=True)
    daAreaOuEdificacaoEmQueEstaLocalizado = models.TextField("Da Área/Edificação em que Está Localizado", blank=True, null=True)
    possuiFacilidade = models.CharField("Possui Facilidade",max_length=255,blank=True, null=True)
    sinalizacaoIndicativa = models.CharField("Sinalização Indicativa", max_length=255,blank=True, null=True)
    tipoDeOrganizacao = models.JSONField("Tipo de Organização",blank=True, null=True)
    proximidades = models.JSONField("Proximidades",blank=True, null=True)
    
    # Dados relacionados ao turismo e pagamentos
    formasDePagamento = models.JSONField("Formas de Pagamento",blank=True, null=True)
    reservas = models.JSONField("Reservas",blank=True, null=True)
    atendimentoEmLinguaEstrangeira = models.JSONField("Atendimento em Língua Estrangeira",blank=True, null=True)
    informativosImpressos = models.JSONField("Informativos Impressos",blank=True, null=True)
    restricoes = models.JSONField("Restrições",blank=True, null=True)
    mesesAltaTemporada = models.JSONField("Meses de Alta Temporada",blank=True, null=True)
    origemDosVisitantes = models.JSONField("Origem dos Visitantes",blank=True, null=True)
    
    # Produtos e serviços
    estacionamento = models.JSONField("Estacionamento",blank=True, null=True)
    pessoalCapacitadoParaReceberPCD = models.JSONField("Pessoal Capacitado para Receber PCD",blank=True, null=True)
    
    # Acessibilidade
    rotaExternaAcessivel = models.JSONField("Rota Externa Acessível",blank=True, null=True)
    simboloInternacionalDeAcesso = models.JSONField("Símbolo Internacional de Acesso",blank=True, null=True)
    localDeEmbarqueEDesembarque = models.JSONField("Local de Embarque e Desembarque",blank=True, null=True)
    vagaEmEstacionamento = models.JSONField("Vaga em Estacionamento",blank=True, null=True)
    areaDeCirculacaoAcessoInterno = models.JSONField("Área de Circulação/Acesso Interno",blank=True, null=True)
    escada = models.JSONField("Escada",blank=True, null=True)
    rampa = models.JSONField("Rampa",blank=True, null=True)
    piso = models.JSONField("Piso",blank=True, null=True)
    elevador = models.JSONField("Elevador",blank=True, null=True)
    equipamentoMotorizadoParaDeslocamentoInterno = models.JSONField("Equipamento Motorizado para Deslocamento Interno",blank=True, null=True)
    sinalizacaoVisual = models.JSONField("Sinalização Visual",blank=True, null=True)
    sinalizacaoTatil = models.JSONField("Sinalização Tátil",blank=True, null=True)
    alarmeDeEmergencia = models.JSONField("Alarme de Emergência",blank=True, null=True)
    comunicacao = models.JSONField("Comunicação",blank=True, null=True)
    balcaoDeAtendimento = models.JSONField("Balcão de Atendimento",blank=True, null=True)
    mobiliario = models.JSONField("Mobiliário",blank=True, null=True)
    sanitario = models.JSONField("Sanitário",blank=True, null=True)
    telefone = models.JSONField("Telefone",blank=True, null=True)
    
    # Classificação e localização do meio de hospedagem
    subtipo = models.JSONField(blank=True, null=True)
    natureza = models.CharField("Natureza", max_length=255, blank=True, null=True)
    localizacao = models.TextField("Localização", blank=True, null=True)
    periodo = models.JSONField(blank=True, null=True)
    tabelasHorario = models.JSONField("Tabelas de Horário",blank=True,null=True)
    estadoGeralDeConservacao = models.CharField("Estado Geral de Conservação", max_length=255, blank=True, null=True)
    
    
    # Dados empresariais
    razaoSocial = models.CharField("Razão Social", max_length=255, blank=True, null=True)
    nomeFantasia = models.CharField("Nome Fantasia", max_length=255, blank=True, null=True)
    codigoCNAE = models.CharField("Código CNAE", max_length=50, blank=True, null=True)
    atividadeEconomica = models.TextField("Atividade Econômica", blank=True, null=True)
    inscricaoMunicipal = models.CharField("Inscrição Municipal", max_length=50, blank=True, null=True)
    nomeDaRede = models.CharField("Nome da Rede", max_length=255, blank=True, null=True)
    CNPJ = models.CharField("CNPJ", max_length=20, blank=True, null=True)
    inicioDaAtividade = models.CharField("Início da Atividade",max_length=255, blank=True, null=True)
    
    # Dados de quantitativos e capacidade
    qtdeFuncionariosPermanentes = models.CharField("Qtd. Funcionários Permanentes", max_length = 254, blank=True, null=True)
    qtdeFuncionariosTemporarios = models.CharField("Qtd. Funcionários Temporários", max_length = 254, blank=True, null=True)
    qtdeFuncionarisComDeficiencia = models.CharField("Qtd. Funcionários com Deficiência", max_length = 254, blank=True, null=True)
    latitude = models.CharField(max_length=255,blank=True, null=True)
    longitude = models.CharField(max_length=255,blank=True, null=True)
    
    # Endereço e contato
    avenidaRuaEtc = models.CharField("Avenida/Rua/etc.", max_length=255, blank=True, null=True)
    bairroLocalidade = models.CharField("Bairro/Localidade", max_length=255, blank=True, null=True)
    distrito = models.CharField("Distrito", max_length=255, blank=True, null=True)
    CEP = models.CharField("CEP", max_length=20, blank=True, null=True)
    whatsapp = models.CharField("WhatsApp", max_length=50, blank=True, null=True)
    instagram = models.CharField("Instagram", max_length=100, blank=True, null=True)
    email = models.CharField("Email", max_length=254, blank=True, null=True)
    site = models.CharField("Site", max_length=255,blank=True, null=True)
    pontosDeReferencia = models.TextField("Pontos de Referência", blank=True, null=True)
    
    # Dados de tabelas e informações adicionais
    tabelaMTUR = models.JSONField("Tabela MTUR",blank=True,null=True)
    outrasRegrasEInformacoes = models.TextField("Outras Regras e Informações", blank=True, null=True)
    nAnoOcupacao = models.CharField("Ano de Ocupação", max_length=255,blank=True, null=True)
    nCapacidadeDeVeiculos = models.CharField("Capacidade de Veículos", max_length = 254, blank=True, null=True)
    nAutomoveis = models.CharField("Número de Automóveis", max_length = 254, blank=True, null=True)
    nOnibus = models.CharField("Número de Ônibus", max_length = 254, blank=True, null=True)
    outrasAcessibilidade = models.CharField(max_length=255,blank=True, null=True)
    
    # Tabelas de instalações e equipamentos/espaços
    tabelaEquipamentoEEspaco = models.JSONField("Tabela Equipamento e Espaço",blank=True,null=True)
    tabelaEquipamentoEEspaco2 = models.JSONField("Tabela Equipamento e Espaço 2",blank=True,null=True )
    
    # Observações e referências
    outros = models.TextField("Outros", blank=True, null=True)
    
    ambientacaoTematica = models.CharField(max_length = 254, blank=True, null=True)
    entidadeManetedora = models.CharField(max_length = 254, blank=True, null=True)
    entidadeManetedoraEmail = models.CharField(max_length = 254, blank=True, null=True)
    entidadeManetedoraSite = models.CharField(max_length = 254, blank=True, null=True)
    entradaGratuita = models.CharField(max_length = 254, blank=True, null=True)
    entradaPaga = models.CharField(max_length = 254, blank=True, null=True)
    outrasIntalacoes = models.JSONField(blank=True,null=True)
    permissaoDeAcesso = models.CharField(max_length =255, blank=True, null=True)
    servicos = models.JSONField(blank=True, null=True)
     
class InformacoesTuristicas(Base):
   
    # Dados do formulário e pesquisador
    
    # Dados do coordenador
    
    # Sinalizações e funcionamento
    sinalizacaoDeAcesso = models.CharField("Sinalização de Acesso",max_length=255,blank=True, null=True)
    sinalizacaoTuristica = models.CharField("Sinalização Turística",max_length=255,blank=True, null=True)
    funcionamento24h = models.CharField("Funcionamento 24h",max_length=255,blank=True, null=True)
    funcionamentoEmFeriados = models.CharField("Funcionamento em Feriados",max_length=255,blank=True, null=True)
    
    # Infraestrutura e localização do equipamento/edificação
    doEquipamentoEspaco = models.TextField("Do Equipamento/Espaço", blank=True, null=True)
    daAreaOuEdificacaoEmQueEstaLocalizado = models.TextField("Da Área/Edificação em que Está Localizado", blank=True, null=True)
    possuiFacilidade = models.CharField("Possui Facilidade",max_length=255,blank=True, null=True)
    sinalizacaoIndicativa = models.CharField("Sinalização Indicativa", max_length=255,blank=True, null=True)
    tipoDeOrganizacao = models.JSONField("Tipo de Organização",blank=True, null=True)
    proximidades = models.JSONField("Proximidades",blank=True, null=True)
    
    # Dados relacionados ao turismo e pagamentos
    formasDePagamento = models.JSONField("Formas de Pagamento",blank=True, null=True)
    reservas = models.JSONField("Reservas",blank=True, null=True)
    atendimentoEmLinguaEstrangeira = models.JSONField("Atendimento em Língua Estrangeira",blank=True, null=True)
    informativosImpressos = models.JSONField("Informativos Impressos",blank=True, null=True)
    restricoes = models.JSONField("Restrições",blank=True, null=True)
    mesesAltaTemporada = models.JSONField("Meses de Alta Temporada",blank=True, null=True)
    origemDosVisitantes = models.JSONField("Origem dos Visitantes",blank=True, null=True)
    
    # Produtos e serviços
    estacionamento = models.JSONField("Estacionamento",blank=True, null=True)
    pessoalCapacitadoParaReceberPCD = models.JSONField("Pessoal Capacitado para Receber PCD",blank=True, null=True)
    
    # Acessibilidade
    rotaExternaAcessivel = models.JSONField("Rota Externa Acessível",blank=True, null=True)
    simboloInternacionalDeAcesso = models.JSONField("Símbolo Internacional de Acesso",blank=True, null=True)
    localDeEmbarqueEDesembarque = models.JSONField("Local de Embarque e Desembarque",blank=True, null=True)
    vagaEmEstacionamento = models.JSONField("Vaga em Estacionamento",blank=True, null=True)
    areaDeCirculacaoAcessoInterno = models.JSONField("Área de Circulação/Acesso Interno",blank=True, null=True)
    escada = models.JSONField("Escada",blank=True, null=True)
    rampa = models.JSONField("Rampa",blank=True, null=True)
    piso = models.JSONField("Piso",blank=True, null=True)
    elevador = models.JSONField("Elevador",blank=True, null=True)
    equipamentoMotorizadoParaDeslocamentoInterno = models.JSONField("Equipamento Motorizado para Deslocamento Interno",blank=True, null=True)
    sinalizacaoVisual = models.JSONField("Sinalização Visual",blank=True, null=True)
    sinalizacaoTatil = models.JSONField("Sinalização Tátil",blank=True, null=True)
    alarmeDeEmergencia = models.JSONField("Alarme de Emergência",blank=True, null=True)
    comunicacao = models.JSONField("Comunicação",blank=True, null=True)
    balcaoDeAtendimento = models.JSONField("Balcão de Atendimento",blank=True, null=True)
    mobiliario = models.JSONField("Mobiliário",blank=True, null=True)
    sanitario = models.JSONField("Sanitário",blank=True, null=True)
    telefone = models.JSONField("Telefone",blank=True, null=True)
    
    # Classificação e localização do meio de hospedagem
    subtipo = models.JSONField(blank=True, null=True)
    natureza = models.CharField("Natureza", max_length=255, blank=True, null=True)
    localizacao = models.TextField("Localização", blank=True, null=True)
    periodo = models.JSONField(blank=True, null=True)
    tabelasHorario = models.JSONField("Tabelas de Horário",blank=True,null=True)
    estadoGeralDeConservacao = models.CharField("Estado Geral de Conservação", max_length=255, blank=True, null=True)
    
    
    # Dados empresariais
    nomeOficial = models.CharField( max_length=255, blank=True, null=True)
    nomePopular = models.CharField( max_length=255, blank=True, null=True)
    codigoCNAE = models.CharField("Código CNAE", max_length=50, blank=True, null=True)
    atividadeEconomica = models.TextField("Atividade Econômica", blank=True, null=True)
    inscricaoMunicipal = models.CharField("Inscrição Municipal", max_length=50, blank=True, null=True)
    inicioDaAtividade = models.CharField("Início da Atividade",max_length=255, blank=True, null=True)
    
    # Dados de quantitativos e capacidade
    qtdeFuncionariosPermanentes = models.CharField("Qtd. Funcionários Permanentes", max_length = 254, blank=True, null=True)
    qtdeFuncionariosTemporarios = models.CharField("Qtd. Funcionários Temporários", max_length = 254, blank=True, null=True)
    qtdeFuncionarisComDeficiencia = models.CharField("Qtd. Funcionários com Deficiência", max_length = 254, blank=True, null=True)
    latitude = models.CharField(max_length=255,blank=True, null=True)
    longitude = models.CharField(max_length=255,blank=True, null=True)
    
    # Endereço e contato
    avenidaRuaEtc = models.CharField("Avenida/Rua/etc.", max_length=255, blank=True, null=True)
    bairroLocalidade = models.CharField("Bairro/Localidade", max_length=255, blank=True, null=True)
    distrito = models.CharField("Distrito", max_length=255, blank=True, null=True)
    CEP = models.CharField("CEP", max_length=20, blank=True, null=True)
    whatsapp = models.CharField("WhatsApp", max_length=50, blank=True, null=True)
    instagram = models.CharField("Instagram", max_length=100, blank=True, null=True)
    email = models.CharField("Email", max_length=254, blank=True, null=True)
    site = models.CharField("Site", max_length=255,blank=True, null=True)
    pontosDeReferencia = models.TextField("Pontos de Referência", blank=True, null=True)
    
    # Dados de tabelas e informações adicionais
    outrasRegrasEInformacoes = models.TextField("Outras Regras e Informações", blank=True, null=True)
    nAnoOcupacao = models.CharField("Ano de Ocupação", max_length=255,blank=True, null=True)
    nCapacidadeDeVeiculos = models.CharField("Capacidade de Veículos", max_length = 254, blank=True, null=True)
    nAutomoveis = models.CharField("Número de Automóveis", max_length = 254, blank=True, null=True)
    nOnibus = models.CharField("Número de Ônibus", max_length = 254, blank=True, null=True)
    outrasAcessibilidade = models.CharField(max_length=255,blank=True, null=True)
    
    # Tabelas de instalações e equipamentos/espaços
    tabelaEquipamentoEEspaco = models.JSONField("Tabela Equipamento e Espaço",blank=True,null=True)
    tabelaEquipamentoEEspaco2 = models.JSONField("Tabela Equipamento e Espaço 2",blank=True,null=True )
    
    # Observações e referências
    outros = models.TextField("Outros", blank=True, null=True)
    
    ambientacaoTematica = models.CharField(max_length = 254, blank=True, null=True)
    entidadeManetedora = models.CharField(max_length = 254, blank=True, null=True)
    entidadeManetedoraEmail = models.CharField(max_length = 254, blank=True, null=True)
    entidadeManetedoraSite = models.CharField(max_length = 254, blank=True, null=True)
    entradaGratuita = models.CharField(max_length = 254, blank=True, null=True)
    entradaPaga = models.CharField(max_length = 254, blank=True, null=True)
    outrasIntalacoes = models.JSONField(blank=True,null=True)
    permissaoDeAcesso = models.CharField(max_length =255, blank=True, null=True)
    servicos = models.JSONField(blank=True, null=True)
  
class EntidadesAssociativas(Base):
   
    # Dados do formulário e pesquisador
    
    # Dados do coordenador
    
    # Sinalizações e funcionamento
    sinalizacaoDeAcesso = models.CharField("Sinalização de Acesso",max_length=255,blank=True, null=True)
    sinalizacaoTuristica = models.CharField("Sinalização Turística",max_length=255,blank=True, null=True)
    funcionamento24h = models.CharField("Funcionamento 24h",max_length=255,blank=True, null=True)
    funcionamentoEmFeriados = models.CharField("Funcionamento em Feriados",max_length=255,blank=True, null=True)
    
    # Infraestrutura e localização do equipamento/edificação
    doEquipamentoEspaco = models.TextField("Do Equipamento/Espaço", blank=True, null=True)
    daAreaOuEdificacaoEmQueEstaLocalizado = models.TextField("Da Área/Edificação em que Está Localizado", blank=True, null=True)
    possuiFacilidade = models.CharField("Possui Facilidade",max_length=255,blank=True, null=True)
    sinalizacaoIndicativa = models.CharField("Sinalização Indicativa", max_length=255,blank=True, null=True)
    tipoDeOrganizacao = models.JSONField("Tipo de Organização",blank=True, null=True)
    proximidades = models.JSONField("Proximidades",blank=True, null=True)
    
    # Dados relacionados ao turismo e pagamentos
    formasDePagamento = models.JSONField("Formas de Pagamento",blank=True, null=True)
    reservas = models.JSONField("Reservas",blank=True, null=True)
    atendimentoEmLinguaEstrangeira = models.JSONField("Atendimento em Língua Estrangeira",blank=True, null=True)
    informativosImpressos = models.JSONField("Informativos Impressos",blank=True, null=True)
    restricoes = models.JSONField("Restrições",blank=True, null=True)
    mesesAltaTemporada = models.JSONField("Meses de Alta Temporada",blank=True, null=True)
    origemDosVisitantes = models.JSONField("Origem dos Visitantes",blank=True, null=True)
    
    # Produtos e serviços
    estacionamento = models.JSONField("Estacionamento",blank=True, null=True)
    pessoalCapacitadoParaReceberPCD = models.JSONField("Pessoal Capacitado para Receber PCD",blank=True, null=True)
    
    # Acessibilidade
    rotaExternaAcessivel = models.JSONField("Rota Externa Acessível",blank=True, null=True)
    simboloInternacionalDeAcesso = models.JSONField("Símbolo Internacional de Acesso",blank=True, null=True)
    localDeEmbarqueEDesembarque = models.JSONField("Local de Embarque e Desembarque",blank=True, null=True)
    vagaEmEstacionamento = models.JSONField("Vaga em Estacionamento",blank=True, null=True)
    areaDeCirculacaoAcessoInterno = models.JSONField("Área de Circulação/Acesso Interno",blank=True, null=True)
    escada = models.JSONField("Escada",blank=True, null=True)
    rampa = models.JSONField("Rampa",blank=True, null=True)
    piso = models.JSONField("Piso",blank=True, null=True)
    elevador = models.JSONField("Elevador",blank=True, null=True)
    equipamentoMotorizadoParaDeslocamentoInterno = models.JSONField("Equipamento Motorizado para Deslocamento Interno",blank=True, null=True)
    sinalizacaoVisual = models.JSONField("Sinalização Visual",blank=True, null=True)
    sinalizacaoTatil = models.JSONField("Sinalização Tátil",blank=True, null=True)
    alarmeDeEmergencia = models.JSONField("Alarme de Emergência",blank=True, null=True)
    comunicacao = models.JSONField("Comunicação",blank=True, null=True)
    balcaoDeAtendimento = models.JSONField("Balcão de Atendimento",blank=True, null=True)
    mobiliario = models.JSONField("Mobiliário",blank=True, null=True)
    sanitario = models.JSONField("Sanitário",blank=True, null=True)
    telefone = models.JSONField("Telefone",blank=True, null=True)
    
    # Classificação e localização do meio de hospedagem
    subtipo = models.JSONField(blank=True, null=True)
    natureza = models.CharField("Natureza", max_length=255, blank=True, null=True)
    localizacao = models.TextField("Localização", blank=True, null=True)
    periodo = models.JSONField(blank=True, null=True)
    tabelasHorario = models.JSONField("Tabelas de Horário",blank=True,null=True)
    estadoGeralDeConservacao = models.CharField("Estado Geral de Conservação", max_length=255, blank=True, null=True)
    
    
    # Dados empresariais
    razaoSocial = models.CharField( max_length=255, blank=True, null=True)
    nomeFantasia = models.CharField( max_length=255, blank=True, null=True)
    codigoCNAE = models.CharField("Código CNAE", max_length=50, blank=True, null=True)
    atividadeEconomica = models.TextField("Atividade Econômica", blank=True, null=True)
    inscricaoMunicipal = models.CharField("Inscrição Municipal", max_length=50, blank=True, null=True)
    inicioDaAtividade = models.CharField("Início da Atividade",max_length=255, blank=True, null=True)
    
    # Dados de quantitativos e capacidade
    qtdeFuncionariosPermanentes = models.CharField("Qtd. Funcionários Permanentes", max_length = 254, blank=True, null=True)
    qtdeFuncionariosTemporarios = models.CharField("Qtd. Funcionários Temporários", max_length = 254, blank=True, null=True)
    qtdeFuncionarisComDeficiencia = models.CharField("Qtd. Funcionários com Deficiência", max_length = 254, blank=True, null=True)
    latitude = models.CharField(max_length=255,blank=True, null=True)
    longitude = models.CharField(max_length=255,blank=True, null=True)
    
    # Endereço e contato
    avenidaRuaEtc = models.CharField("Avenida/Rua/etc.", max_length=255, blank=True, null=True)
    bairroLocalidade = models.CharField("Bairro/Localidade", max_length=255, blank=True, null=True)
    distrito = models.CharField("Distrito", max_length=255, blank=True, null=True)
    CEP = models.CharField("CEP", max_length=20, blank=True, null=True)
    whatsapp = models.CharField("WhatsApp", max_length=50, blank=True, null=True)
    instagram = models.CharField("Instagram", max_length=100, blank=True, null=True)
    email = models.CharField("Email", max_length=254, blank=True, null=True)
    site = models.CharField("Site", max_length=255,blank=True, null=True)
    pontosDeReferencia = models.TextField("Pontos de Referência", blank=True, null=True)
    
    # Dados de tabelas e informações adicionais
    outrasRegrasEInformacoes = models.TextField("Outras Regras e Informações", blank=True, null=True)
    nAnoOcupacao = models.CharField("Ano de Ocupação", max_length=255,blank=True, null=True)
    nCapacidadeDeVeiculos = models.CharField("Capacidade de Veículos", max_length = 254, blank=True, null=True)
    nAutomoveis = models.CharField("Número de Automóveis", max_length = 254, blank=True, null=True)
    nOnibus = models.CharField("Número de Ônibus", max_length = 254, blank=True, null=True)
    outrasAcessibilidade = models.CharField(max_length=255,blank=True, null=True)
    
    # Tabelas de instalações e equipamentos/espaços
    tabelaEquipamentoEEspaco = models.JSONField("Tabela Equipamento e Espaço",blank=True,null=True)
    tabelaEquipamentoEEspaco2 = models.JSONField("Tabela Equipamento e Espaço 2",blank=True,null=True )
    
    # Observações e referências
    outros = models.TextField("Outros", blank=True, null=True)
    
    ambientacaoTematica = models.CharField(max_length = 254, blank=True, null=True)
    entidadeManetedora = models.CharField(max_length = 254, blank=True, null=True)
    entidadeManetedoraEmail = models.CharField(max_length = 254, blank=True, null=True)
    entidadeManetedoraSite = models.CharField(max_length = 254, blank=True, null=True)
    entradaGratuita = models.CharField(max_length = 254, blank=True, null=True)
    entradaPaga = models.CharField(max_length = 254, blank=True, null=True)
    outrasIntalacoes = models.JSONField(blank=True,null=True)
    permissaoDeAcesso = models.CharField(max_length =255, blank=True, null=True)
    servicos = models.JSONField(blank=True, null=True)
    
    distanciasAeroporto = models.CharField(max_length=255, null=True, blank=True)
    distanciasRodoviaria  = models.CharField(max_length=255, null=True, blank=True)
    distanciaEstacaoFerroviaria  = models.CharField(max_length=255, null=True, blank=True)
    distanciaEstacaoMaritima  = models.CharField(max_length=255, null=True, blank=True)
    distanciaEstacaoMetroviaria  = models.CharField(max_length=255, null=True, blank=True)
    distanciaPontoDeOnibus  = models.CharField(max_length=255, null=True, blank=True)
    distanciaPontoDeTaxi  = models.CharField(max_length=255, null=True, blank=True)
    distanciasOutraNome  = models.CharField(max_length=255, null=True, blank=True)
    distanciaOutras  = models.CharField(max_length=255, null=True, blank=True)
    nomeDoDirigente  = models.CharField(max_length=255, null=True, blank=True)
    cargo  = models.CharField(max_length=255, null=True, blank=True)
    representacaoSetor  = models.CharField(max_length=255, null=True, blank=True)
    numeroDeAssociados  = models.CharField(max_length=255, null=True, blank=True)
    abrangencia  = models.CharField(max_length=255, null=True, blank=True)
    representividade  = models.CharField(max_length=255, null=True, blank=True)
    CNPJ  = models.CharField(max_length=255, null=True, blank=True)
    forum  = models.CharField(max_length=255, null=True, blank=True)
    conselho  = models.CharField(max_length=255, null=True, blank=True)
    federecao  = models.CharField(max_length=255, null=True, blank=True)
    associacao  = models.CharField(max_length=255, null=True, blank=True)
    outrosEntidade  = models.CharField(max_length=255, null=True, blank=True)
       
class InstalacoesEsportivas(Base):
   
    # Sinalizações e funcionamento
    sinalizacaoDeAcesso = models.CharField("Sinalização de Acesso",max_length=255,blank=True, null=True)
    sinalizacaoTuristica = models.CharField("Sinalização Turística",max_length=255,blank=True, null=True)
    funcionamento24h = models.CharField("Funcionamento 24h",max_length=255,blank=True, null=True)
    funcionamentoEmFeriados = models.CharField("Funcionamento em Feriados",max_length=255,blank=True, null=True)
    geradorDeEmergencia = models.CharField("Gerador de Emergência",max_length=255,blank=True, null=True)
    
    # Infraestrutura e localização do equipamento/edificação
    doEquipamentoEspaco = models.TextField("Do Equipamento/Espaço", blank=True, null=True)
    daAreaOuEdificacaoEmQueEstaLocalizado = models.TextField("Da Área/Edificação em que Está Localizado", blank=True, null=True)
    possuiFacilidade = models.CharField("Possui Facilidade",max_length=255,blank=True, null=True)
    sinalizacaoIndicativa = models.CharField("Sinalização Indicativa", max_length=255,blank=True, null=True)
    tipoDeOrganizacao = models.JSONField("Tipo de Organização",blank=True, null=True)
    proximidades = models.JSONField("Proximidades",blank=True, null=True)
    
    # Dados relacionados ao turismo e pagamentos
    segmentosOuTurismoEspecializado = models.JSONField("Segmentos ou Turismo Especializado",blank=True, null=True)
    formasDePagamento = models.JSONField("Formas de Pagamento",blank=True, null=True)
    reservas = models.JSONField("Reservas",blank=True, null=True)
    atendimentoEmLinguaEstrangeira = models.JSONField("Atendimento em Língua Estrangeira",blank=True, null=True)
    informativosImpressos = models.JSONField("Informativos Impressos",blank=True, null=True)
    restricoes = models.JSONField("Restrições",blank=True, null=True)
    mesesAltaTemporada = models.JSONField("Meses de Alta Temporada",blank=True, null=True)
    origemDosVisitantes = models.JSONField("Origem dos Visitantes",blank=True, null=True)
    
    # Produtos e serviços
    produtosHigienePessoal = models.JSONField("Produtos de Higiene Pessoal",blank=True, null=True)
    equipamentosEServicos = models.JSONField("Equipamentos e Serviços",blank=True, null=True)
    estacionamento = models.JSONField("Estacionamento",blank=True, null=True)
    restaurante = models.JSONField("Restaurante",blank=True, null=True)
    lanchonete = models.JSONField("Lanchonete",blank=True, null=True)
    instalacaoEEspacos = models.JSONField("Instalação e Espaços",blank=True, null=True)
    outrosEspacosEAtividades = models.JSONField("Outros Espaços e Atividades",blank=True, null=True)
    servicos = models.JSONField("Serviços",blank=True, null=True)
    equipamentos = models.JSONField("Equipamentos",blank=True, null=True)
    facilidadesEServicos = models.JSONField("Facilidades e Serviços",blank=True, null=True)
    facilidadesParaExecutivos = models.JSONField("Facilidades para Executivos",blank=True, null=True)
    pessoalCapacitadoParaReceberPCD = models.JSONField("Pessoal Capacitado para Receber PCD",blank=True, null=True)
    
    # Acessibilidade
    rotaExternaAcessivel = models.JSONField("Rota Externa Acessível",blank=True, null=True)
    simboloInternacionalDeAcesso = models.JSONField("Símbolo Internacional de Acesso",blank=True, null=True)
    localDeEmbarqueEDesembarque = models.JSONField("Local de Embarque e Desembarque",blank=True, null=True)
    vagaEmEstacionamento = models.JSONField("Vaga em Estacionamento",blank=True, null=True)
    areaDeCirculacaoAcessoInterno = models.JSONField("Área de Circulação/Acesso Interno",blank=True, null=True)
    escada = models.JSONField("Escada",blank=True, null=True)
    rampa = models.JSONField("Rampa",blank=True, null=True)
    piso = models.JSONField("Piso",blank=True, null=True)
    elevador = models.JSONField("Elevador",blank=True, null=True)
    equipamentoMotorizadoParaDeslocamentoInterno = models.JSONField("Equipamento Motorizado para Deslocamento Interno",blank=True, null=True)
    sinalizacaoVisual = models.JSONField("Sinalização Visual",blank=True, null=True)
    sinalizacaoTatil = models.JSONField("Sinalização Tátil",blank=True, null=True)
    alarmeDeEmergencia = models.JSONField("Alarme de Emergência",blank=True, null=True)
    comunicacao = models.JSONField("Comunicação",blank=True, null=True)
    balcaoDeAtendimento = models.JSONField("Balcão de Atendimento",blank=True, null=True)
    mobiliario = models.JSONField("Mobiliário",blank=True, null=True)
    sanitario = models.JSONField("Sanitário",blank=True, null=True)
    telefone = models.JSONField("Telefone",blank=True, null=True)
    
    # Classificação e localização do meio de hospedagem
    subtipo = models.JSONField(blank=True, null=True)
    natureza = models.CharField("Natureza", max_length=255, blank=True, null=True)
    localizacao = models.TextField("Localização", blank=True, null=True)
    tipoDeDiaria = models.CharField("Tipo de Diária", max_length=255, blank=True, null=True)
    periodo = models.JSONField(blank=True, null=True)
    tabelasHorario = models.JSONField("Tabelas de Horário",blank=True,null=True)
    energiaEletrica = models.TextField("Energia Elétrica", blank=True, null=True)
    estadoGeralDeConservacao = models.CharField("Estado Geral de Conservação", max_length=255, blank=True, null=True)
    
    # Dados de turismo e localização geográfica
    estadosTuristas = models.JSONField("Estados Turistas", blank=True, null=True)
    paisesTuristas = models.JSONField("Países Turistas", blank=True,null=True)
    
    # Dados empresariais
    razaoSocial = models.CharField("Razão Social", max_length=255, blank=True, null=True)
    nomeFantasia = models.CharField("Nome Fantasia", max_length=255, blank=True, null=True)
    codigoCNAE = models.CharField("Código CNAE", max_length=50, blank=True, null=True)
    atividadeEconomica = models.TextField("Atividade Econômica", blank=True, null=True)
    inscricaoMunicipal = models.CharField("Inscrição Municipal", max_length=50, blank=True, null=True)
    nomeDaRede = models.CharField("Nome da Rede", max_length=255, blank=True, null=True)
    CNPJ = models.CharField("CNPJ", max_length=20, blank=True, null=True)
    inicioDaAtividade = models.CharField("Início da Atividade",max_length=255, blank=True, null=True)
    
    # Dados de quantitativos e capacidade
    qtdeFuncionariosPermanentes = models.CharField("Qtd. Funcionários Permanentes", max_length = 254, blank=True, null=True)
    qtdeFuncionariosTemporarios = models.CharField("Qtd. Funcionários Temporários", max_length = 254, blank=True, null=True)
    qtdeFuncionarisComDeficiencia = models.CharField("Qtd. Funcionários com Deficiência", max_length = 254, blank=True, null=True)
    latitude = models.CharField(max_length=255,blank=True, null=True)
    longitude = models.CharField(max_length=255,blank=True, null=True)
    
    # Endereço e contato
    avenidaRuaEtc = models.CharField("Avenida/Rua/etc.", max_length=255, blank=True, null=True)
    bairroLocalidade = models.CharField("Bairro/Localidade", max_length=255, blank=True, null=True)
    distrito = models.CharField("Distrito", max_length=255, blank=True, null=True)
    CEP = models.CharField("CEP", max_length=20, blank=True, null=True)
    whatsapp = models.CharField("WhatsApp", max_length=50, blank=True, null=True)
    instagram = models.CharField("Instagram", max_length=100, blank=True, null=True)
    email = models.CharField("Email", max_length=254, blank=True, null=True)
    site = models.CharField("Site", max_length=255,blank=True, null=True)
    pontosDeReferencia = models.TextField("Pontos de Referência", blank=True, null=True)
    
    # Dados de tabelas e informações adicionais
    tabelaMTUR = models.JSONField("Tabela MTUR",blank=True,null=True)
    outrasRegrasEInformacoes = models.TextField("Outras Regras e Informações", blank=True, null=True)
    nAnoOcupacao = models.CharField("Ano de Ocupação", max_length=255,blank=True, null=True)
    nOcupacaoAltaTemporada = models.CharField("Ocupação em Alta Temporada", max_length=255,blank=True, null=True)
    nTotalDeUH = models.CharField("Total de UH", max_length = 254, blank=True, null=True)
    nTotalDeLeitos = models.CharField("Total de Leitos", max_length = 254, blank=True, null=True)
    nUhAdaptadasParaPCD = models.CharField("UH Adaptadas para PCD", max_length = 254, blank=True, null=True)
    nCapacidadeDeVeiculos = models.CharField("Capacidade de Veículos", max_length = 254, blank=True, null=True)
    nAutomoveis = models.CharField("Número de Automóveis", max_length = 254, blank=True, null=True)
    nOnibus = models.CharField("Número de Ônibus", max_length = 254, blank=True, null=True)
    capacidadeEmKVA = models.DecimalField("Capacidade (KVA)", max_digits=10, decimal_places=2, blank=True, null=True)
    geradorCapacidadeEmKVA = models.DecimalField("Capacidade do Gerador (KVA)", max_digits=10, decimal_places=2, blank=True, null=True)
    nCapacidadeInstaladaPorDia = models.CharField("Capacidade Instalada por Dia", max_length = 254, blank=True, null=True)
    nPessoasAtendidasSentadas = models.CharField("Qtd. de Pessoas Atendidas Sentadas", max_length = 254, blank=True, null=True)
    nCapacidadeSimultanea = models.CharField("Capacidade Simultânea", max_length = 254, blank=True, null=True)
    nPessoasAtendidasSentadasSimultanea = models.CharField("Qtd. de Pessoas Atendidas Sentadas (Simultânea)", max_length = 254, blank=True, null=True)
    lanchoneteCapacidadeInstaladaPorDia = models.CharField("Lanchonete - Capacidade Instalada por Dia", max_length = 254, blank=True, null=True)
    lanchoneteCapacidadePessoasAtendidasSentadas = models.CharField("Lanchonete - Pessoas Atendidas Sentadas", max_length = 254, blank=True, null=True)
    lanchoneteCapacidadeSimultanea = models.CharField("Lanchonete - Capacidade Simultânea", max_length = 254, blank=True, null=True)
    lanchoneteCapacidadeSentadasSimultanea = models.CharField("Lanchonete - Pessoas Sentadas Simultânea", max_length = 254, blank=True, null=True)
    outrasAcessibilidade = models.CharField(max_length=255,blank=True, null=True)
    
    # Tabelas de instalações e equipamentos/espaços
    tabelaInstalacoes = models.JSONField("Tabela Instalações",blank=True,null=True)
    tabelaEquipamentoEEspaco = models.JSONField("Tabela Equipamento e Espaço",blank=True,null=True)
    tabelaEquipamentoEEspaco2 = models.JSONField("Tabela Equipamento e Espaço 2",blank=True,null=True )
    
    # Observações e referências
    outros = models.TextField("Outros", blank=True, null=True)
    
    modalidadesPraticadasGinasio = models.JSONField(blank=True,null=True)
    ginasioAreaCoberta = models.CharField(max_length=255,blank=True, null=True)
    ginasioPoliesportivo = models.CharField(max_length=255,blank=True, null=True)
    pistaDeSkateTipoDePista = models.CharField(max_length=255,blank=True, null=True)
    vooLivreDecolagem = models.CharField(max_length=255,blank=True, null=True)
    melhorEpoca = models.CharField(max_length=255,blank=True, null=True)
    piscinaAreaCoberta = models.CharField(max_length=255,blank=True, null=True)
    piscinaTrampolim = models.CharField(max_length=255,blank=True, null=True)
    capacidadeEspectadoresTotal = models.CharField(max_length=255,blank=True, null=True)
    capacidadeEspectadoresArquibancada = models.CharField(max_length=255,blank=True, null=True)
    capacidadeEspectadoresCamarotes = models.CharField(max_length=255,blank=True, null=True)
    capacidadeEspectadoresCadeirasCativas = models.CharField(max_length=255,blank=True, null=True)
    capacidadeEspectadoresTribunasDeHonra = models.CharField(max_length=255,blank=True, null=True)
    capacidadeEspectadoresArquibancadasCobertas = models.CharField(max_length=255,blank=True, null=True)
    capacidadeEspectadoresOutrasCategorias = models.CharField(max_length=255,blank=True, null=True)
    ginasioTipoDePiso = models.CharField(max_length=255,blank=True, null=True)
    ginasioComprimento = models.CharField(max_length=255,blank=True, null=True)
    campoDeFutebolTipoDePiso = models.CharField(max_length=255,blank=True, null=True)
    campoDeFutebolComprimento = models.CharField(max_length=255,blank=True, null=True)
    campoDeFutebolAreaCoberta = models.CharField(max_length=255,blank=True, null=True)
    campoDeFutebolQuantidade = models.CharField(max_length=255,blank=True, null=True)
    autodromoComprimentoDaPista = models.CharField(max_length=255,blank=True, null=True)
    autodromoQuantidadeDePistas = models.CharField(max_length=255,blank=True, null=True)
    hipodromoTipoDePiso = models.CharField(max_length=255,blank=True, null=True)
    hipodromoComprimentoDaPista = models.CharField(max_length=255,blank=True, null=True)
    hipodromoQuantidadeDePistas = models.CharField(max_length=255,blank=True, null=True)
    pistaDeBolicheComprimentoDaPista = models.CharField(max_length=255,blank=True, null=True)
    pistaDeBolicheQuantidadeDePistas = models.CharField(max_length=255,blank=True, null=True)
    pistaDeSkateComprimentoDaPista = models.CharField(max_length=255,blank=True, null=True)
    pistaDeSkateAreaDaPista = models.CharField(max_length=255,blank=True, null=True)
    pistaDeSkateQuantidadeDePistas = models.CharField(max_length=255,blank=True, null=True)
    vooLivreTipoDeVoo = models.CharField(max_length=255,blank=True, null=True)
    vooLivreAltitude = models.CharField(max_length=255,blank=True, null=True)
    vooLivreDesnivel = models.CharField(max_length=255,blank=True, null=True)
    vooLivreQuadrante = models.CharField(max_length=255,blank=True, null=True)
    vooLivreWaypoint = models.CharField(max_length=255,blank=True, null=True)
    vooLivrePouso = models.CharField(max_length=255,blank=True, null=True)
    piscinaComprimento = models.CharField(max_length=255,blank=True, null=True)
    piscinaProfundidade = models.CharField(max_length=255,blank=True, null=True)
    piscinaLargura = models.CharField(max_length=255,blank=True, null=True)
    piscinaQuantidade = models.CharField(max_length=255,blank=True, null=True)
    piscinaOutroEquipamento = models.CharField(max_length=255,blank=True, null=True)
    outrasOutras = models.CharField(max_length=255,blank=True, null=True)
    caracteristicasEspecificas = models.CharField(max_length=255,blank=True, null=True)
    entidadeManetedora = models.CharField(max_length=255,blank=True, null=True)
    entidadeManetedoraEmail = models.CharField(max_length=255,blank=True, null=True)
    entidadeManetedoraSite = models.CharField(max_length=255,blank=True, null=True)
    entradaGratuita = models.CharField(max_length=255,blank=True, null=True)
    entradaPaga = models.CharField(max_length=255,blank=True, null=True)
    outrasInstalacoes = models.JSONField(blank=True, null=True)
    
class UnidadesDeConservacao(Base):
   
    sinalizacaoDeAcesso = models.CharField("Sinalização de Acesso",max_length=255,blank=True, null=True)
    sinalizacaoTuristica = models.CharField("Sinalização Turística",max_length=255,blank=True, null=True)
    funcionamento24h = models.CharField("Funcionamento 24h",max_length=255,blank=True, null=True)
    funcionamentoEmFeriados = models.CharField("Funcionamento em Feriados",max_length=255,blank=True, null=True)
    geradorDeEmergencia = models.CharField("Gerador de Emergência",max_length=255,blank=True, null=True)
    
    # Infraestrutura e localização do equipamento/edificação
    doEquipamentoEspaco = models.TextField("Do Equipamento/Espaço", blank=True, null=True)
    daAreaOuEdificacaoEmQueEstaLocalizado = models.TextField("Da Área/Edificação em que Está Localizado", blank=True, null=True)
    possuiFacilidade = models.CharField("Possui Facilidade",max_length=255,blank=True, null=True)
    sinalizacaoIndicativa = models.CharField("Sinalização Indicativa", max_length=255,blank=True, null=True)
    tipoDeOrganizacao = models.JSONField("Tipo de Organização",blank=True, null=True)
    proximidades = models.JSONField("Proximidades",blank=True, null=True)
    
    # Dados relacionados ao turismo e pagamentos
    segmentosOuTurismoEspecializado = models.JSONField("Segmentos ou Turismo Especializado",blank=True, null=True)
    formasDePagamento = models.JSONField("Formas de Pagamento",blank=True, null=True)
    reservas = models.JSONField("Reservas",blank=True, null=True)
    atendimentoEmLinguaEstrangeira = models.JSONField("Atendimento em Língua Estrangeira",blank=True, null=True)
    informativosImpressos = models.JSONField("Informativos Impressos",blank=True, null=True)
    restricoes = models.JSONField("Restrições",blank=True, null=True)
    mesesAltaTemporada = models.JSONField("Meses de Alta Temporada",blank=True, null=True)
    origemDosVisitantes = models.JSONField("Origem dos Visitantes",blank=True, null=True)
    
    # Produtos e serviços
    produtosHigienePessoal = models.JSONField("Produtos de Higiene Pessoal",blank=True, null=True)
    equipamentosEServicos = models.JSONField("Equipamentos e Serviços",blank=True, null=True)
    estacionamento = models.JSONField("Estacionamento",blank=True, null=True)
    restaurante = models.JSONField("Restaurante",blank=True, null=True)
    lanchonete = models.JSONField("Lanchonete",blank=True, null=True)
    instalacaoEEspacos = models.JSONField("Instalação e Espaços",blank=True, null=True)
    outrosEspacosEAtividades = models.JSONField("Outros Espaços e Atividades",blank=True, null=True)
    servicos = models.JSONField("Serviços",blank=True, null=True)
    equipamentos = models.JSONField("Equipamentos",blank=True, null=True)
    facilidadesEServicos = models.JSONField("Facilidades e Serviços",blank=True, null=True)
    facilidadesParaExecutivos = models.JSONField("Facilidades para Executivos",blank=True, null=True)
    pessoalCapacitadoParaReceberPCD = models.JSONField("Pessoal Capacitado para Receber PCD",blank=True, null=True)
    
    # Acessibilidade
    rotaExternaAcessivel = models.JSONField("Rota Externa Acessível",blank=True, null=True)
    simboloInternacionalDeAcesso = models.JSONField("Símbolo Internacional de Acesso",blank=True, null=True)
    localDeEmbarqueEDesembarque = models.JSONField("Local de Embarque e Desembarque",blank=True, null=True)
    vagaEmEstacionamento = models.JSONField("Vaga em Estacionamento",blank=True, null=True)
    areaDeCirculacaoAcessoInterno = models.JSONField("Área de Circulação/Acesso Interno",blank=True, null=True)
    escada = models.JSONField("Escada",blank=True, null=True)
    rampa = models.JSONField("Rampa",blank=True, null=True)
    piso = models.JSONField("Piso",blank=True, null=True)
    elevador = models.JSONField("Elevador",blank=True, null=True)
    equipamentoMotorizadoParaDeslocamentoInterno = models.JSONField("Equipamento Motorizado para Deslocamento Interno",blank=True, null=True)
    sinalizacaoVisual = models.JSONField("Sinalização Visual",blank=True, null=True)
    sinalizacaoTatil = models.JSONField("Sinalização Tátil",blank=True, null=True)
    alarmeDeEmergencia = models.JSONField("Alarme de Emergência",blank=True, null=True)
    comunicacao = models.JSONField("Comunicação",blank=True, null=True)
    balcaoDeAtendimento = models.JSONField("Balcão de Atendimento",blank=True, null=True)
    mobiliario = models.JSONField("Mobiliário",blank=True, null=True)
    sanitario = models.JSONField("Sanitário",blank=True, null=True)
    telefone = models.JSONField("Telefone",blank=True, null=True)
    
    # Classificação e localização do meio de hospedagem
    subtipo = models.JSONField(blank=True, null=True)
    natureza = models.CharField("Natureza", max_length=255, blank=True, null=True)
    localizacao = models.TextField("Localização", blank=True, null=True)
    tipoDeDiaria = models.CharField("Tipo de Diária", max_length=255, blank=True, null=True)
    periodo = models.JSONField(blank=True, null=True)
    tabelasHorario = models.JSONField("Tabelas de Horário",blank=True,null=True)
    energiaEletrica = models.TextField("Energia Elétrica", blank=True, null=True)
    estadoGeralDeConservacao = models.CharField("Estado Geral de Conservação", max_length=255, blank=True, null=True)
    
    # Dados de turismo e localização geográfica
    estadosTuristas = models.JSONField("Estados Turistas", blank=True, null=True)
    paisesTuristas = models.JSONField("Países Turistas", blank=True,null=True)
    
    # Dados empresariais
    razaoSocial = models.CharField("Razão Social", max_length=255, blank=True, null=True)
    nomeFantasia = models.CharField("Nome Fantasia", max_length=255, blank=True, null=True)
    codigoCNAE = models.CharField("Código CNAE", max_length=50, blank=True, null=True)
    atividadeEconomica = models.TextField("Atividade Econômica", blank=True, null=True)
    inscricaoMunicipal = models.CharField("Inscrição Municipal", max_length=50, blank=True, null=True)
    nomeDaRede = models.CharField("Nome da Rede", max_length=255, blank=True, null=True)
    CNPJ = models.CharField("CNPJ", max_length=20, blank=True, null=True)
    inicioDaAtividade = models.CharField("Início da Atividade",max_length=255, blank=True, null=True)
    
    # Dados de quantitativos e capacidade
    qtdeFuncionariosPermanentes = models.CharField("Qtd. Funcionários Permanentes", max_length = 254, blank=True, null=True)
    qtdeFuncionariosTemporarios = models.CharField("Qtd. Funcionários Temporários", max_length = 254, blank=True, null=True)
    qtdeFuncionarisComDeficiencia = models.CharField("Qtd. Funcionários com Deficiência", max_length = 254, blank=True, null=True)
    latitude = models.CharField(max_length=255,blank=True, null=True)
    longitude = models.CharField(max_length=255,blank=True, null=True)
    
    # Endereço e contato
    avenidaRuaEtc = models.CharField("Avenida/Rua/etc.", max_length=255, blank=True, null=True)
    bairroLocalidade = models.CharField("Bairro/Localidade", max_length=255, blank=True, null=True)
    distrito = models.CharField("Distrito", max_length=255, blank=True, null=True)
    CEP = models.CharField("CEP", max_length=20, blank=True, null=True)
    whatsapp = models.CharField("WhatsApp", max_length=50, blank=True, null=True)
    instagram = models.CharField("Instagram", max_length=100, blank=True, null=True)
    email = models.CharField("Email", max_length=254, blank=True, null=True)
    site = models.CharField("Site", max_length=255,blank=True, null=True)
    pontosDeReferencia = models.TextField("Pontos de Referência", blank=True, null=True)
    
    # Dados de tabelas e informações adicionais
    tabelaMTUR = models.JSONField("Tabela MTUR",blank=True,null=True)
    outrasRegrasEInformacoes = models.TextField("Outras Regras e Informações", blank=True, null=True)
    nAnoOcupacao = models.CharField("Ano de Ocupação", max_length=255,blank=True, null=True)
    nOcupacaoAltaTemporada = models.CharField("Ocupação em Alta Temporada", max_length=255,blank=True, null=True)
    nTotalDeUH = models.CharField("Total de UH", max_length = 254, blank=True, null=True)
    nTotalDeLeitos = models.CharField("Total de Leitos", max_length = 254, blank=True, null=True)
    nUhAdaptadasParaPCD = models.CharField("UH Adaptadas para PCD", max_length = 254, blank=True, null=True)
    nCapacidadeDeVeiculos = models.CharField("Capacidade de Veículos", max_length = 254, blank=True, null=True)
    nAutomoveis = models.CharField("Número de Automóveis", max_length = 254, blank=True, null=True)
    nOnibus = models.CharField("Número de Ônibus", max_length = 254, blank=True, null=True)
    capacidadeEmKVA = models.DecimalField("Capacidade (KVA)", max_digits=10, decimal_places=2, blank=True, null=True)
    geradorCapacidadeEmKVA = models.DecimalField("Capacidade do Gerador (KVA)", max_digits=10, decimal_places=2, blank=True, null=True)
    nCapacidadeInstaladaPorDia = models.CharField("Capacidade Instalada por Dia", max_length = 254, blank=True, null=True)
    nPessoasAtendidasSentadas = models.CharField("Qtd. de Pessoas Atendidas Sentadas", max_length = 254, blank=True, null=True)
    nCapacidadeSimultanea = models.CharField("Capacidade Simultânea", max_length = 254, blank=True, null=True)
    nPessoasAtendidasSentadasSimultanea = models.CharField("Qtd. de Pessoas Atendidas Sentadas (Simultânea)", max_length = 254, blank=True, null=True)
    lanchoneteCapacidadeInstaladaPorDia = models.CharField("Lanchonete - Capacidade Instalada por Dia", max_length = 254, blank=True, null=True)
    lanchoneteCapacidadePessoasAtendidasSentadas = models.CharField("Lanchonete - Pessoas Atendidas Sentadas", max_length = 254, blank=True, null=True)
    lanchoneteCapacidadeSimultanea = models.CharField("Lanchonete - Capacidade Simultânea", max_length = 254, blank=True, null=True)
    lanchoneteCapacidadeSentadasSimultanea = models.CharField("Lanchonete - Pessoas Sentadas Simultânea", max_length = 254, blank=True, null=True)
    outrasAcessibilidade = models.CharField(max_length=255,blank=True, null=True)
    
    # Tabelas de instalações e equipamentos/espaços
    tabelaInstalacoes = models.JSONField("Tabela Instalações",blank=True,null=True)
    tabelaEquipamentoEEspaco = models.JSONField("Tabela Equipamento e Espaço",blank=True,null=True)
    tabelaEquipamentoEEspaco2 = models.JSONField("Tabela Equipamento e Espaço 2",blank=True,null=True )
    
    # Observações e referências
    outros = models.TextField("Outros", blank=True, null=True)
    esferaAdministrativa = models.CharField(max_length=255,blank=True, null=True)
    distanciasAeroporto = models.CharField(max_length=255,blank=True, null=True)
    distanciasRodoviaria = models.CharField(max_length=255,blank=True, null=True)
    distanciaEstacaoFerroviaria = models.CharField(max_length=255,blank=True, null=True)
    distanciaEstacaoMaritima = models.CharField(max_length=255,blank=True, null=True)
    distanciaEstacaoMetroviaria = models.CharField(max_length=255,blank=True, null=True)
    distanciaPontoDeOnibus = models.CharField(max_length=255,blank=True, null=True)
    distanciaPontoDeTaxi = models.CharField(max_length=255,blank=True, null=True)
    distanciasOutraNome = models.CharField(max_length=255,blank=True, null=True)
    distanciaOutras = models.CharField(max_length=255,blank=True, null=True)
    entidadeManetedora = models.CharField(max_length=255,blank=True, null=True)
    entidadeManetedoraEmail = models.CharField(max_length=255,blank=True, null=True)
    entidadeManetedoraSite = models.CharField(max_length=255,blank=True, null=True)
    planoDeManejo = models.CharField(max_length=255,blank=True, null=True)
    visitacao = models.CharField(max_length=255,blank=True, null=True)
    finalidadeDaVisitacao = models.CharField(max_length=255,blank=True, null=True)
    agendada = models.CharField(max_length=255,blank=True, null=True)
    autoguiada = models.CharField(max_length=255,blank=True, null=True)
    guiada = models.CharField(max_length=255,blank=True, null=True)
    entradaGratuita = models.CharField(max_length=255,blank=True, null=True)
    entradaPaga = models.CharField(max_length=255,blank=True, null=True)
    centroDeRecepcao = models.CharField(max_length=255,blank=True, null=True)
    postoDeInformacao = models.CharField(max_length=255,blank=True, null=True)
    portariaPrincipal = models.CharField(max_length=255,blank=True, null=True)
    guarita = models.CharField(max_length=255,blank=True, null=True)
    bilheteria = models.CharField(max_length=255,blank=True, null=True)
    anoBase = models.CharField(max_length=255,blank=True, null=True)
    principalPublicoFrequentador = models.CharField(max_length=255,blank=True, null=True)
    integraRoteiros = models.CharField(max_length=255,blank=True, null=True)
    integraGuiaTuristico = models.CharField(max_length=255,blank=True, null=True)
    roteiro1 = models.CharField(max_length=255,blank=True, null=True)
    siteRoteiro1 = models.CharField(max_length=255,blank=True, null=True)
    roteiro2 = models.CharField(max_length=255,blank=True, null=True)
    siteRoteiro2 = models.CharField(max_length=255,blank=True, null=True)
    roteiro3 = models.CharField(max_length=255,blank=True, null=True)
    siteRoteiro3 = models.CharField(max_length=255,blank=True, null=True)
    roteiro4 = models.CharField(max_length=255,blank=True, null=True)
    siteRoteiro4 = models.CharField(max_length=255,blank=True, null=True)
    roteiro5 = models.CharField(max_length=255,blank=True, null=True)
    siteRoteiro5 = models.CharField(max_length=255,blank=True, null=True)
    Guia1 = models.CharField(max_length=255,blank=True, null=True)
    siteGuia1 = models.CharField(max_length=255,blank=True, null=True)
    Guia2 = models.CharField(max_length=255,blank=True, null=True)
    siteGuia2 = models.CharField(max_length=255,blank=True, null=True)
    Guia3 = models.CharField(max_length=255,blank=True, null=True)
    siteGuia3 = models.CharField(max_length=255,blank=True, null=True)
    Guia4 = models.CharField(max_length=255,blank=True, null=True)
    siteGuia4 = models.CharField(max_length=255,blank=True, null=True)
    Guia5 = models.CharField(max_length=255,blank=True, null=True)
    siteGuia5 = models.CharField(max_length=255,blank=True, null=True)
    
    # Campos List<String>? -> JSONField
    outrasInstalacoes = models.JSONField(blank=True,null=True)
    outrosEquipamentos = models.JSONField(blank=True,null=True)

    # Campos String? -> CharField
    arvorismo = models.CharField(max_length=255,blank=True, null=True)
    atividadesCulturais = models.CharField(max_length=255,blank=True, null=True)
    atividadesPedagogicas = models.CharField(max_length=255,blank=True, null=True)
    boiaCross = models.CharField(max_length=255,blank=True, null=True)
    bungeeJump = models.CharField(max_length=255,blank=True, null=True)
    caminhada = models.CharField(max_length=255,blank=True, null=True)
    canoagem = models.CharField(max_length=255,blank=True, null=True)
    cavalgada = models.CharField(max_length=255,blank=True, null=True)
    ciclismo = models.CharField(max_length=255,blank=True, null=True)
    escalada = models.CharField(max_length=255,blank=True, null=True)
    ginastica = models.CharField(max_length=255,blank=True, null=True)
    kitesurf = models.CharField(max_length=255,blank=True, null=True)
    mergulho = models.CharField(max_length=255,blank=True, null=True)
    motocross = models.CharField(max_length=255,blank=True, null=True)
    mountainBike = models.CharField(max_length=255,blank=True, null=True)
    observacao = models.CharField(max_length=255,blank=True, null=True)
    offRoad = models.CharField(max_length=255,blank=True, null=True)
    parapenteAsaDelta = models.CharField(max_length=255,blank=True, null=True)
    pesca = models.CharField(max_length=255,blank=True, null=True)
    rafting = models.CharField(max_length=255,blank=True, null=True)
    rapel = models.CharField(max_length=255,blank=True, null=True)
    remo = models.CharField(max_length=255,blank=True, null=True)
    safariFotografico = models.CharField(max_length=255,blank=True, null=True)
    skate = models.CharField(max_length=255,blank=True, null=True)
    vela = models.CharField(max_length=255,blank=True, null=True)
    vooLivre = models.CharField(max_length=255,blank=True, null=True)
    windsurf = models.CharField(max_length=255,blank=True, null=True)
    trilha = models.CharField(max_length=255,blank=True, null=True)
    outraAtividade = models.CharField(max_length=255,blank=True, null=True)
    outroAtividade = models.CharField(max_length=255,blank=True, null=True)
    extensaoCaracteristicas = models.CharField(max_length=255,blank=True, null=True)
    quedasDAgua = models.CharField(max_length=255,blank=True, null=True)
    rio = models.CharField(max_length=255,blank=True, null=True)
    tipoCatarata = models.CharField(max_length=255,blank=True, null=True)
    riacho = models.CharField(max_length=255,blank=True, null=True)
    quedasDAguaRiacho = models.CharField(max_length=255,blank=True, null=True)
    tipoRiacho = models.CharField(max_length=255,blank=True, null=True)
    corrego = models.CharField(max_length=255,blank=True, null=True)
    quedasDAguaCorrego = models.CharField(max_length=255,blank=True, null=True)
    tipoCorrego = models.CharField(max_length=255,blank=True, null=True)
    fonte = models.CharField(max_length=255,blank=True, null=True)
    lagoLagoa = models.CharField(max_length=255,blank=True, null=True)
    alagado = models.CharField(max_length=255,blank=True, null=True)
    outrasHidrografia = models.CharField(max_length=255,blank=True, null=True)
    relevo = models.CharField(max_length=255,blank=True, null=True)
    vegetacao = models.CharField(max_length=255,blank=True, null=True)
    especieEndemica = models.CharField(max_length=255,blank=True, null=True)

    # Campos List<String>? -> JSONField
    melhoresMesesEndemica = models.JSONField(blank=True,null=True)

    # Campos String? -> CharField
    especieRara = models.CharField(max_length=255,blank=True, null=True)
    especieEmExtincao = models.CharField(max_length=255,blank=True, null=True)
    especieExotica = models.CharField(max_length=255,blank=True, null=True)

    # Campos List<String>? -> JSONField
    melhoresMesesRara = models.JSONField(blank=True,null=True)
    melhoresMesesEmExtincao = models.JSONField(blank=True,null=True)
    melhoresMesesExotica = models.JSONField(blank=True,null=True)

    # Campos String? -> CharField
    especieOutra = models.CharField(max_length=255,blank=True, null=True)
    outrasEspecies = models.CharField(max_length=255,blank=True, null=True)

    # Campos List<String>? -> JSONField
    melhoresMesesOutra = models.JSONField(blank=True,null=True)

    # Campos String? -> CharField
    faunaEndemica = models.CharField(max_length=255,blank=True, null=True)
    faunaRara = models.CharField(max_length=255,blank=True, null=True)
    faunaEmExtincao = models.CharField(max_length=255,blank=True, null=True)
    faunaExotica = models.CharField(max_length=255,blank=True, null=True)

    # Campos List<String>? -> JSONField
    faunaMelhoresMesesEndemica = models.JSONField(blank=True,null=True)
    faunaMelhoresMesesRara = models.JSONField(blank=True,null=True)
    faunaMelhoresMesesEmExtincao = models.JSONField(blank=True,null=True)
    faunaMelhoresMesesExotica = models.JSONField(blank=True,null=True)

    # Campos String? -> CharField
    faunaOutra = models.CharField(max_length=255,blank=True, null=True)
    faunaOutrasEspecies = models.CharField(max_length=255,blank=True, null=True)

    # Campos List<String>? -> JSONField
    melhoresMesesOutraFaunaOutra = models.JSONField(blank=True,null=True)
    agropecuaria = models.JSONField(blank=True,null=True)
    industrial = models.JSONField(blank=True,null=True)
    extrativista = models.JSONField(blank=True,null=True)

    # Campos String? -> CharField
    descritivoEspecifidadeAtrativo = models.CharField(max_length=255,blank=True, null=True)
    trilhaDeAcesso = models.CharField(max_length=255,blank=True, null=True)
    extensaoAcessoAoAtrativo = models.CharField(max_length=255,blank=True, null=True)
    grauDeDificuldade = models.CharField(max_length=255,blank=True, null=True)
    empresa1 = models.CharField(max_length=255,blank=True, null=True)
    telefone1 = models.CharField(max_length=255,blank=True, null=True)
    email1 = models.CharField(max_length=255,blank=True, null=True)
    site1 = models.CharField(max_length=255,blank=True, null=True)
    empresa2 = models.CharField(max_length=255,blank=True, null=True)
    telefone2 = models.CharField(max_length=255,blank=True, null=True)
    email2 = models.CharField(max_length=255,blank=True, null=True)
    site2 = models.CharField(max_length=255,blank=True, null=True)
    empresa3 = models.CharField(max_length=255,blank=True, null=True)
    telefone3 = models.CharField(max_length=255,blank=True, null=True)
    email3 = models.CharField(max_length=255,blank=True, null=True)
    site3 = models.CharField(max_length=255,blank=True, null=True)
    empresa4 = models.CharField(max_length=255,blank=True, null=True)
    telefone4 = models.CharField(max_length=255,blank=True, null=True)
    email4 = models.CharField(max_length=255,blank=True, null=True)
    site4 = models.CharField(max_length=255,blank=True, null=True)
    empresa5 = models.CharField(max_length=255,blank=True, null=True)
    telefone5 = models.CharField(max_length=255,blank=True, null=True)
    email5 = models.CharField(max_length=255,blank=True, null=True)
    site5 = models.CharField(max_length=255,blank=True, null=True)
    fretadoEmpresa1 = models.CharField(max_length=255,blank=True, null=True)
    fretadoTipoDeTransporte1 = models.CharField(max_length=255,blank=True, null=True)
    fretadoTelefone1 = models.CharField(max_length=255,blank=True, null=True)
    fretadoEmail1 = models.CharField(max_length=255,blank=True, null=True)
    fretadoSite1 = models.CharField(max_length=255,blank=True, null=True)
    fretadoEmpresa2 = models.CharField(max_length=255,blank=True, null=True)
    fretadoTipoDeTransporte2 = models.CharField(max_length=255,blank=True, null=True)
    fretadoTelefone2 = models.CharField(max_length=255,blank=True, null=True)
    fretadoEmail2 = models.CharField(max_length=255,blank=True, null=True)
    fretadoSite2 = models.CharField(max_length=255,blank=True, null=True)
    fretadoEmpresa3 = models.CharField(max_length=255,blank=True, null=True)
    fretadoTipoDeTransporte3 = models.CharField(max_length=255,blank=True, null=True)
    fretadoTelefone3 = models.CharField(max_length=255,blank=True, null=True)
    fretadoEmail3 = models.CharField(max_length=255,blank=True, null=True)
    fretadoSite3 = models.CharField(max_length=255,blank=True, null=True)
    fretadoEmpresa4 = models.CharField(max_length=255,blank=True, null=True)
    fretadoTipoDeTransporte4 = models.CharField(max_length=255,blank=True, null=True)
    fretadoTelefone4 = models.CharField(max_length=255,blank=True, null=True)
    fretadoEmail4 = models.CharField(max_length=255,blank=True, null=True)
    fretadoSite4 = models.CharField(max_length=255,blank=True, null=True)
    fretadoEmpresa5 = models.CharField(max_length=255,blank=True, null=True)
    fretadoTipoDeTransporte5 = models.CharField(max_length=255,blank=True, null=True)
    fretadoTelefone5 = models.CharField(max_length=255,blank=True, null=True)
    fretadoEmail5 = models.CharField(max_length=255,blank=True, null=True)
    fretadoSite5 = models.CharField(max_length=255,blank=True, null=True)
    instalacoesOutras = models.CharField(max_length=255, blank=True, null=True)
    nomeOficial = models.CharField(max_length=255, blank=True, null=True)

class EventosProgramados(Base):
    tipoLista = models.JSONField(blank=True,null=True)
    nomeOficial = models.CharField(max_length=255,blank=True,null=True)
    # Campos String? -> CharField
    cnpjRealizador = models.CharField(max_length=255,blank=True, null=True)
    entidadeManetedoraWhatsapp = models.CharField(max_length=255,blank=True, null=True)
    entidadeManetedoraInstagram = models.CharField(max_length=255,blank=True, null=True)
    periodoDeRealizacao = models.CharField(max_length=255,blank=True, null=True)
    periodicidade = models.CharField(max_length=255,blank=True, null=True)
    caraterEvento = models.CharField(max_length=255,blank=True, null=True)
    descritivoDasEspecifidades = models.CharField(max_length=255,blank=True, null=True)
    sinalizacaoDeAcesso = models.CharField("Sinalização de Acesso",max_length=255,blank=True, null=True)
    sinalizacaoTuristica = models.CharField("Sinalização Turística",max_length=255,blank=True, null=True)
    funcionamento24h = models.CharField("Funcionamento 24h",max_length=255,blank=True, null=True)
    funcionamentoEmFeriados = models.CharField("Funcionamento em Feriados",max_length=255,blank=True, null=True)
    geradorDeEmergencia = models.CharField("Gerador de Emergência",max_length=255,blank=True, null=True)
    
    # Infraestrutura e localização do equipamento/edificação
    doEquipamentoEspaco = models.TextField("Do Equipamento/Espaço", blank=True, null=True)
    daAreaOuEdificacaoEmQueEstaLocalizado = models.TextField("Da Área/Edificação em que Está Localizado", blank=True, null=True)
    possuiFacilidade = models.CharField("Possui Facilidade",max_length=255,blank=True, null=True)
    sinalizacaoIndicativa = models.CharField("Sinalização Indicativa", max_length=255,blank=True, null=True)
    tipoDeOrganizacao = models.JSONField("Tipo de Organização",blank=True, null=True)
    proximidades = models.JSONField("Proximidades",blank=True, null=True)
    
    # Dados relacionados ao turismo e pagamentos
    segmentosOuTurismoEspecializado = models.JSONField("Segmentos ou Turismo Especializado",blank=True, null=True)
    formasDePagamento = models.JSONField("Formas de Pagamento",blank=True, null=True)
    reservas = models.JSONField("Reservas",blank=True, null=True)
    atendimentoEmLinguaEstrangeira = models.JSONField("Atendimento em Língua Estrangeira",blank=True, null=True)
    informativosImpressos = models.JSONField("Informativos Impressos",blank=True, null=True)
    restricoes = models.JSONField("Restrições",blank=True, null=True)
    mesesAltaTemporada = models.JSONField("Meses de Alta Temporada",blank=True, null=True)
    origemDosVisitantes = models.JSONField("Origem dos Visitantes",blank=True, null=True)
    
    # Produtos e serviços
    produtosHigienePessoal = models.JSONField("Produtos de Higiene Pessoal",blank=True, null=True)
    equipamentosEServicos = models.JSONField("Equipamentos e Serviços",blank=True, null=True)
    estacionamento = models.JSONField("Estacionamento",blank=True, null=True)
    restaurante = models.JSONField("Restaurante",blank=True, null=True)
    lanchonete = models.JSONField("Lanchonete",blank=True, null=True)
    instalacaoEEspacos = models.JSONField("Instalação e Espaços",blank=True, null=True)
    outrosEspacosEAtividades = models.JSONField("Outros Espaços e Atividades",blank=True, null=True)
    servicos = models.JSONField("Serviços",blank=True, null=True)
    equipamentos = models.JSONField("Equipamentos",blank=True, null=True)
    facilidadesEServicos = models.JSONField("Facilidades e Serviços",blank=True, null=True)
    facilidadesParaExecutivos = models.JSONField("Facilidades para Executivos",blank=True, null=True)
    pessoalCapacitadoParaReceberPCD = models.JSONField("Pessoal Capacitado para Receber PCD",blank=True, null=True)
    
    # Acessibilidade
    rotaExternaAcessivel = models.JSONField("Rota Externa Acessível",blank=True, null=True)
    simboloInternacionalDeAcesso = models.JSONField("Símbolo Internacional de Acesso",blank=True, null=True)
    localDeEmbarqueEDesembarque = models.JSONField("Local de Embarque e Desembarque",blank=True, null=True)
    vagaEmEstacionamento = models.JSONField("Vaga em Estacionamento",blank=True, null=True)
    areaDeCirculacaoAcessoInterno = models.JSONField("Área de Circulação/Acesso Interno",blank=True, null=True)
    escada = models.JSONField("Escada",blank=True, null=True)
    rampa = models.JSONField("Rampa",blank=True, null=True)
    piso = models.JSONField("Piso",blank=True, null=True)
    elevador = models.JSONField("Elevador",blank=True, null=True)
    equipamentoMotorizadoParaDeslocamentoInterno = models.JSONField("Equipamento Motorizado para Deslocamento Interno",blank=True, null=True)
    sinalizacaoVisual = models.JSONField("Sinalização Visual",blank=True, null=True)
    sinalizacaoTatil = models.JSONField("Sinalização Tátil",blank=True, null=True)
    alarmeDeEmergencia = models.JSONField("Alarme de Emergência",blank=True, null=True)
    comunicacao = models.JSONField("Comunicação",blank=True, null=True)
    balcaoDeAtendimento = models.JSONField("Balcão de Atendimento",blank=True, null=True)
    mobiliario = models.JSONField("Mobiliário",blank=True, null=True)
    sanitario = models.JSONField("Sanitário",blank=True, null=True)
    telefone = models.JSONField("Telefone",blank=True, null=True)
    
    # Classificação e localização do meio de hospedagem
    subtipo = models.JSONField(blank=True, null=True)
    natureza = models.CharField("Natureza", max_length=255, blank=True, null=True)
    localizacao = models.TextField("Localização", blank=True, null=True)
    tipoDeDiaria = models.CharField("Tipo de Diária", max_length=255, blank=True, null=True)
    periodo = models.JSONField(blank=True, null=True)
    tabelasHorario = models.JSONField("Tabelas de Horário",blank=True,null=True)
    energiaEletrica = models.TextField("Energia Elétrica", blank=True, null=True)
    estadoGeralDeConservacao = models.CharField("Estado Geral de Conservação", max_length=255, blank=True, null=True)
    
    # Dados de turismo e localização geográfica
    estadosTuristas = models.JSONField("Estados Turistas", blank=True, null=True)
    paisesTuristas = models.JSONField("Países Turistas", blank=True,null=True)
    
    # Dados empresariais
    razaoSocial = models.CharField("Razão Social", max_length=255, blank=True, null=True)
    nomeFantasia = models.CharField("Nome Fantasia", max_length=255, blank=True, null=True)
    codigoCNAE = models.CharField("Código CNAE", max_length=50, blank=True, null=True)
    atividadeEconomica = models.TextField("Atividade Econômica", blank=True, null=True)
    inscricaoMunicipal = models.CharField("Inscrição Municipal", max_length=50, blank=True, null=True)
    nomeDaRede = models.CharField("Nome da Rede", max_length=255, blank=True, null=True)
    CNPJ = models.CharField("CNPJ", max_length=20, blank=True, null=True)
    inicioDaAtividade = models.CharField("Início da Atividade",max_length=255, blank=True, null=True)
    
    # Dados de quantitativos e capacidade
    qtdeFuncionariosPermanentes = models.CharField("Qtd. Funcionários Permanentes", max_length = 254, blank=True, null=True)
    qtdeFuncionariosTemporarios = models.CharField("Qtd. Funcionários Temporários", max_length = 254, blank=True, null=True)
    qtdeFuncionarisComDeficiencia = models.CharField("Qtd. Funcionários com Deficiência", max_length = 254, blank=True, null=True)
    latitude = models.CharField(max_length=255,blank=True, null=True)
    longitude = models.CharField(max_length=255,blank=True, null=True)
    
    # Endereço e contato
    avenidaRuaEtc = models.CharField("Avenida/Rua/etc.", max_length=255, blank=True, null=True)
    bairroLocalidade = models.CharField("Bairro/Localidade", max_length=255, blank=True, null=True)
    distrito = models.CharField("Distrito", max_length=255, blank=True, null=True)
    CEP = models.CharField("CEP", max_length=20, blank=True, null=True)
    whatsapp = models.CharField("WhatsApp", max_length=50, blank=True, null=True)
    instagram = models.CharField("Instagram", max_length=100, blank=True, null=True)
    email = models.CharField("Email", max_length=254, blank=True, null=True)
    site = models.CharField("Site", max_length=255,blank=True, null=True)
    pontosDeReferencia = models.TextField("Pontos de Referência", blank=True, null=True)
    
    # Dados de tabelas e informações adicionais
    tabelaMTUR = models.JSONField("Tabela MTUR",blank=True,null=True)
    outrasRegrasEInformacoes = models.TextField("Outras Regras e Informações", blank=True, null=True)
    nAnoOcupacao = models.CharField("Ano de Ocupação", max_length=255,blank=True, null=True)
    nOcupacaoAltaTemporada = models.CharField("Ocupação em Alta Temporada", max_length=255,blank=True, null=True)
    nTotalDeUH = models.CharField("Total de UH", max_length = 254, blank=True, null=True)
    nTotalDeLeitos = models.CharField("Total de Leitos", max_length = 254, blank=True, null=True)
    nUhAdaptadasParaPCD = models.CharField("UH Adaptadas para PCD", max_length = 254, blank=True, null=True)
    nCapacidadeDeVeiculos = models.CharField("Capacidade de Veículos", max_length = 254, blank=True, null=True)
    nAutomoveis = models.CharField("Número de Automóveis", max_length = 254, blank=True, null=True)
    nOnibus = models.CharField("Número de Ônibus", max_length = 254, blank=True, null=True)
    capacidadeEmKVA = models.DecimalField("Capacidade (KVA)", max_digits=10, decimal_places=2, blank=True, null=True)
    geradorCapacidadeEmKVA = models.DecimalField("Capacidade do Gerador (KVA)", max_digits=10, decimal_places=2, blank=True, null=True)
    nCapacidadeInstaladaPorDia = models.CharField("Capacidade Instalada por Dia", max_length = 254, blank=True, null=True)
    nPessoasAtendidasSentadas = models.CharField("Qtd. de Pessoas Atendidas Sentadas", max_length = 254, blank=True, null=True)
    nCapacidadeSimultanea = models.CharField("Capacidade Simultânea", max_length = 254, blank=True, null=True)
    nPessoasAtendidasSentadasSimultanea = models.CharField("Qtd. de Pessoas Atendidas Sentadas (Simultânea)", max_length = 254, blank=True, null=True)
    lanchoneteCapacidadeInstaladaPorDia = models.CharField("Lanchonete - Capacidade Instalada por Dia", max_length = 254, blank=True, null=True)
    lanchoneteCapacidadePessoasAtendidasSentadas = models.CharField("Lanchonete - Pessoas Atendidas Sentadas", max_length = 254, blank=True, null=True)
    lanchoneteCapacidadeSimultanea = models.CharField("Lanchonete - Capacidade Simultânea", max_length = 254, blank=True, null=True)
    lanchoneteCapacidadeSentadasSimultanea = models.CharField("Lanchonete - Pessoas Sentadas Simultânea", max_length = 254, blank=True, null=True)
    outrasAcessibilidade = models.CharField(max_length=255,blank=True, null=True)
    
    # Tabelas de instalações e equipamentos/espaços
    tabelaInstalacoes = models.JSONField("Tabela Instalações",blank=True,null=True)
    tabelaEquipamentoEEspaco = models.JSONField("Tabela Equipamento e Espaço",blank=True,null=True)
    tabelaEquipamentoEEspaco2 = models.JSONField("Tabela Equipamento e Espaço 2",blank=True,null=True )
    
    # Observações e referências
    outros = models.TextField("Outros", blank=True, null=True)
    esferaAdministrativa = models.CharField(max_length=255,blank=True, null=True)
    distanciasAeroporto = models.CharField(max_length=255,blank=True, null=True)
    distanciasRodoviaria = models.CharField(max_length=255,blank=True, null=True)
    distanciaEstacaoFerroviaria = models.CharField(max_length=255,blank=True, null=True)
    distanciaEstacaoMaritima = models.CharField(max_length=255,blank=True, null=True)
    distanciaEstacaoMetroviaria = models.CharField(max_length=255,blank=True, null=True)
    distanciaPontoDeOnibus = models.CharField(max_length=255,blank=True, null=True)
    distanciaPontoDeTaxi = models.CharField(max_length=255,blank=True, null=True)
    distanciasOutraNome = models.CharField(max_length=255,blank=True, null=True)
    distanciaOutras = models.CharField(max_length=255,blank=True, null=True)
    entidadeManetedora = models.CharField(max_length=255,blank=True, null=True)
    entidadeManetedoraEmail = models.CharField(max_length=255,blank=True, null=True)
    entidadeManetedoraSite = models.CharField(max_length=255,blank=True, null=True)
    planoDeManejo = models.CharField(max_length=255,blank=True, null=True)
    visitacao = models.CharField(max_length=255,blank=True, null=True)
    finalidadeDaVisitacao = models.CharField(max_length=255,blank=True, null=True)
    agendada = models.CharField(max_length=255,blank=True, null=True)
    autoguiada = models.CharField(max_length=255,blank=True, null=True)
    guiada = models.CharField(max_length=255,blank=True, null=True)
    entradaGratuita = models.CharField(max_length=255,blank=True, null=True)
    entradaPaga = models.CharField(max_length=255,blank=True, null=True)
    centroDeRecepcao = models.CharField(max_length=255,blank=True, null=True)
    postoDeInformacao = models.CharField(max_length=255,blank=True, null=True)
    portariaPrincipal = models.CharField(max_length=255,blank=True, null=True)
    guarita = models.CharField(max_length=255,blank=True, null=True)
    bilheteria = models.CharField(max_length=255,blank=True, null=True)
    anoBase = models.CharField(max_length=255,blank=True, null=True)
    principalPublicoFrequentador = models.CharField(max_length=255,blank=True, null=True)
    integraRoteiros = models.CharField(max_length=255,blank=True, null=True)
    integraGuiaTuristico = models.CharField(max_length=255,blank=True, null=True)
    roteiro1 = models.CharField(max_length=255,blank=True, null=True)
    siteRoteiro1 = models.CharField(max_length=255,blank=True, null=True)
    roteiro2 = models.CharField(max_length=255,blank=True, null=True)
    siteRoteiro2 = models.CharField(max_length=255,blank=True, null=True)
    roteiro3 = models.CharField(max_length=255,blank=True, null=True)
    siteRoteiro3 = models.CharField(max_length=255,blank=True, null=True)
    roteiro4 = models.CharField(max_length=255,blank=True, null=True)
    siteRoteiro4 = models.CharField(max_length=255,blank=True, null=True)
    roteiro5 = models.CharField(max_length=255,blank=True, null=True)
    siteRoteiro5 = models.CharField(max_length=255,blank=True, null=True)
    Guia1 = models.CharField(max_length=255,blank=True, null=True)
    siteGuia1 = models.CharField(max_length=255,blank=True, null=True)
    Guia2 = models.CharField(max_length=255,blank=True, null=True)
    siteGuia2 = models.CharField(max_length=255,blank=True, null=True)
    Guia3 = models.CharField(max_length=255,blank=True, null=True)
    siteGuia3 = models.CharField(max_length=255,blank=True, null=True)
    Guia4 = models.CharField(max_length=255,blank=True, null=True)
    siteGuia4 = models.CharField(max_length=255,blank=True, null=True)
    Guia5 = models.CharField(max_length=255,blank=True, null=True)
    siteGuia5 = models.CharField(max_length=255,blank=True, null=True)
    
    # Campos List<String>? -> JSONField
    outrasInstalacoes = models.JSONField(blank=True,null=True)
    outrosEquipamentos = models.JSONField(blank=True,null=True)

    # Campos String? -> CharField
    arvorismo = models.CharField(max_length=255,blank=True, null=True)
    atividadesCulturais = models.CharField(max_length=255,blank=True, null=True)
    atividadesPedagogicas = models.CharField(max_length=255,blank=True, null=True)
    boiaCross = models.CharField(max_length=255,blank=True, null=True)
    bungeeJump = models.CharField(max_length=255,blank=True, null=True)
    caminhada = models.CharField(max_length=255,blank=True, null=True)
    canoagem = models.CharField(max_length=255,blank=True, null=True)
    cavalgada = models.CharField(max_length=255,blank=True, null=True)
    ciclismo = models.CharField(max_length=255,blank=True, null=True)
    escalada = models.CharField(max_length=255,blank=True, null=True)
    ginastica = models.CharField(max_length=255,blank=True, null=True)
    kitesurf = models.CharField(max_length=255,blank=True, null=True)
    mergulho = models.CharField(max_length=255,blank=True, null=True)
    motocross = models.CharField(max_length=255,blank=True, null=True)
    mountainBike = models.CharField(max_length=255,blank=True, null=True)
    observacao = models.CharField(max_length=255,blank=True, null=True)
    offRoad = models.CharField(max_length=255,blank=True, null=True)
    parapenteAsaDelta = models.CharField(max_length=255,blank=True, null=True)
    pesca = models.CharField(max_length=255,blank=True, null=True)
    rafting = models.CharField(max_length=255,blank=True, null=True)
    rapel = models.CharField(max_length=255,blank=True, null=True)
    remo = models.CharField(max_length=255,blank=True, null=True)
    safariFotografico = models.CharField(max_length=255,blank=True, null=True)
    skate = models.CharField(max_length=255,blank=True, null=True)
    vela = models.CharField(max_length=255,blank=True, null=True)
    vooLivre = models.CharField(max_length=255,blank=True, null=True)
    windsurf = models.CharField(max_length=255,blank=True, null=True)
    trilha = models.CharField(max_length=255,blank=True, null=True)
    outraAtividade = models.CharField(max_length=255,blank=True, null=True)
    outroAtividade = models.CharField(max_length=255,blank=True, null=True)
    extensaoCaracteristicas = models.CharField(max_length=255,blank=True, null=True)
    quedasDAgua = models.CharField(max_length=255,blank=True, null=True)
    rio = models.CharField(max_length=255,blank=True, null=True)
    tipoCatarata = models.CharField(max_length=255,blank=True, null=True)
    riacho = models.CharField(max_length=255,blank=True, null=True)
    quedasDAguaRiacho = models.CharField(max_length=255,blank=True, null=True)
    tipoRiacho = models.CharField(max_length=255,blank=True, null=True)
    corrego = models.CharField(max_length=255,blank=True, null=True)
    quedasDAguaCorrego = models.CharField(max_length=255,blank=True, null=True)
    tipoCorrego = models.CharField(max_length=255,blank=True, null=True)
    fonte = models.CharField(max_length=255,blank=True, null=True)
    lagoLagoa = models.CharField(max_length=255,blank=True, null=True)
    alagado = models.CharField(max_length=255,blank=True, null=True)
    outrasHidrografia = models.CharField(max_length=255,blank=True, null=True)
    relevo = models.CharField(max_length=255,blank=True, null=True)
    vegetacao = models.CharField(max_length=255,blank=True, null=True)
    especieEndemica = models.CharField(max_length=255,blank=True, null=True)

    # Campos List<String>? -> JSONField
    melhoresMesesEndemica = models.JSONField(blank=True,null=True)

    # Campos String? -> CharField
    especieRara = models.CharField(max_length=255,blank=True, null=True)
    especieEmExtincao = models.CharField(max_length=255,blank=True, null=True)
    especieExotica = models.CharField(max_length=255,blank=True, null=True)

    # Campos List<String>? -> JSONField
    melhoresMesesRara = models.JSONField(blank=True,null=True)
    melhoresMesesEmExtincao = models.JSONField(blank=True,null=True)
    melhoresMesesExotica = models.JSONField(blank=True,null=True)

    # Campos String? -> CharField
    especieOutra = models.CharField(max_length=255,blank=True, null=True)
    outrasEspecies = models.CharField(max_length=255,blank=True, null=True)

    # Campos List<String>? -> JSONField
    melhoresMesesOutra = models.JSONField(blank=True,null=True)

    # Campos String? -> CharField
    faunaEndemica = models.CharField(max_length=255,blank=True, null=True)
    faunaRara = models.CharField(max_length=255,blank=True, null=True)
    faunaEmExtincao = models.CharField(max_length=255,blank=True, null=True)
    faunaExotica = models.CharField(max_length=255,blank=True, null=True)

    # Campos List<String>? -> JSONField
    faunaMelhoresMesesEndemica = models.JSONField(blank=True,null=True)
    faunaMelhoresMesesRara = models.JSONField(blank=True,null=True)
    faunaMelhoresMesesEmExtincao = models.JSONField(blank=True,null=True)
    faunaMelhoresMesesExotica = models.JSONField(blank=True,null=True)

    # Campos String? -> CharField
    faunaOutra = models.CharField(max_length=255,blank=True, null=True)
    faunaOutrasEspecies = models.CharField(max_length=255,blank=True, null=True)

    # Campos List<String>? -> JSONField
    melhoresMesesOutraFaunaOutra = models.JSONField(blank=True,null=True)
    agropecuaria = models.JSONField(blank=True,null=True)
    industrial = models.JSONField(blank=True,null=True)
    extrativista = models.JSONField(blank=True,null=True)

    # Campos String? -> CharField
    descritivoEspecifidadeAtrativo = models.CharField(max_length=255,blank=True, null=True)
    trilhaDeAcesso = models.CharField(max_length=255,blank=True, null=True)
    extensaoAcessoAoAtrativo = models.CharField(max_length=255,blank=True, null=True)
    grauDeDificuldade = models.CharField(max_length=255,blank=True, null=True)
    empresa1 = models.CharField(max_length=255,blank=True, null=True)
    telefone1 = models.CharField(max_length=255,blank=True, null=True)
    email1 = models.CharField(max_length=255,blank=True, null=True)
    site1 = models.CharField(max_length=255,blank=True, null=True)
    empresa2 = models.CharField(max_length=255,blank=True, null=True)
    telefone2 = models.CharField(max_length=255,blank=True, null=True)
    email2 = models.CharField(max_length=255,blank=True, null=True)
    site2 = models.CharField(max_length=255,blank=True, null=True)
    empresa3 = models.CharField(max_length=255,blank=True, null=True)
    telefone3 = models.CharField(max_length=255,blank=True, null=True)
    email3 = models.CharField(max_length=255,blank=True, null=True)
    site3 = models.CharField(max_length=255,blank=True, null=True)
    empresa4 = models.CharField(max_length=255,blank=True, null=True)
    telefone4 = models.CharField(max_length=255,blank=True, null=True)
    email4 = models.CharField(max_length=255,blank=True, null=True)
    site4 = models.CharField(max_length=255,blank=True, null=True)
    empresa5 = models.CharField(max_length=255,blank=True, null=True)
    telefone5 = models.CharField(max_length=255,blank=True, null=True)
    email5 = models.CharField(max_length=255,blank=True, null=True)
    site5 = models.CharField(max_length=255,blank=True, null=True)
    fretadoEmpresa1 = models.CharField(max_length=255,blank=True, null=True)
    fretadoTipoDeTransporte1 = models.CharField(max_length=255,blank=True, null=True)
    fretadoTelefone1 = models.CharField(max_length=255,blank=True, null=True)
    fretadoEmail1 = models.CharField(max_length=255,blank=True, null=True)
    fretadoSite1 = models.CharField(max_length=255,blank=True, null=True)
    fretadoEmpresa2 = models.CharField(max_length=255,blank=True, null=True)
    fretadoTipoDeTransporte2 = models.CharField(max_length=255,blank=True, null=True)
    fretadoTelefone2 = models.CharField(max_length=255,blank=True, null=True)
    fretadoEmail2 = models.CharField(max_length=255,blank=True, null=True)
    fretadoSite2 = models.CharField(max_length=255,blank=True, null=True)
    fretadoEmpresa3 = models.CharField(max_length=255,blank=True, null=True)
    fretadoTipoDeTransporte3 = models.CharField(max_length=255,blank=True, null=True)
    fretadoTelefone3 = models.CharField(max_length=255,blank=True, null=True)
    fretadoEmail3 = models.CharField(max_length=255,blank=True, null=True)
    fretadoSite3 = models.CharField(max_length=255,blank=True, null=True)
    fretadoEmpresa4 = models.CharField(max_length=255,blank=True, null=True)
    fretadoTipoDeTransporte4 = models.CharField(max_length=255,blank=True, null=True)
    fretadoTelefone4 = models.CharField(max_length=255,blank=True, null=True)
    fretadoEmail4 = models.CharField(max_length=255,blank=True, null=True)
    fretadoSite4 = models.CharField(max_length=255,blank=True, null=True)
    fretadoEmpresa5 = models.CharField(max_length=255,blank=True, null=True)
    fretadoTipoDeTransporte5 = models.CharField(max_length=255,blank=True, null=True)
    fretadoTelefone5 = models.CharField(max_length=255,blank=True, null=True)
    fretadoEmail5 = models.CharField(max_length=255,blank=True, null=True)
    fretadoSite5 = models.CharField(max_length=255,blank=True, null=True)
    instalacoesOutras = models.CharField(max_length=255, blank=True, null=True) 