from rest_framework import serializers
from .models import *
from apidjango.models import validate_cpf
from django.core.mail import send_mail
from django.utils.timezone import now, timedelta

class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, required=True)

    def validate_new_password(self, value):
        # Validação customizada (se necessário, por exemplo, força mínima, etc.)
        if len(value) < 8:
            raise serializers.ValidationError("A senha deve ter pelo menos 8 caracteres.")
        return value

class UserSerializer(serializers.ModelSerializer):
    pesquisas = serializers.PrimaryKeyRelatedField(
        many = True,
        queryset = Pesquisa.objects.all(),
        required=False
        )
         
    class Meta:
        model = CustomUser
        fields = ['id','username', 'CPF', 'email', 'password', 'is_active',  'acessLevel', 'status', 'password', 'telefone', 'pesquisas']
        extra_kwargs = {'password': {'write_only': True, 'required': False, 'allow_blank': True}}


    def create(self, validated_data):
        pesquisas_data = validated_data.pop('pesquisas', [])
        user = CustomUser(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        if pesquisas_data:
            user.pesquisas.set(pesquisas_data)
        return user
    
    def update(self, instance, validated_data):
        pesquisas_data = validated_data.pop('pesquisas', None)
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password and password.strip() != "":
            instance.set_password(password)
        instance.save()
        
        if pesquisas_data is not None:
            instance.pesquisas.set(pesquisas_data)
        return instance
    
    def validate_CPF(self, value):
        validate_cpf(value)
        return value 

class PesquisaSerializer(serializers.ModelSerializer):



    quantidadePesquisadores = serializers.IntegerField(source='usuario.count', read_only = True)
    usuario = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), many=True)
    admin_email = serializers.ReadOnlyField(source='admin.email')
    admin_telefone = serializers.ReadOnlyField(source='admin.telefone')
    quantidadeLocais = serializers.SerializerMethodField()

    
    class Meta:
        model = Pesquisa
        fields = '__all__'

    def update(self, instance, validated_data):
        return super().update(instance, validated_data) 
    
    def get_quantidadeLocais(self, obj):
        return obj.bases.filter(is_active=True).count()

class ContatoInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContatoInfo
        fields = ['nome', 'endereco', 'whatsapp', 'email']

class ServicoEspecializadoInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicoEspecializadoInfo
        fields = ['email', 'servicos_especializados', 'outras_informacoes']

class InfoGeraisSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfoGerais
        fields = ['razao_social', 'nome_fantasia', 'cnpj', 'endereco', 'telefone']

class EnderecoInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnderecoInfo
        fields = ['email', 'site', 'tipoImoveis', 'outrasInfo']

class LocadorasDeImoveisSerializer(serializers.ModelSerializer):
    contatos = InfoGeraisSerializer(many=True)  # Aninhando os dados completos
    servicos_especializados = EnderecoInfoSerializer(many=True)

    
    class Meta:
        model = LocadorasDeImoveis
        fields = [
            'id', 'pesquisa', 'contatos', 'servicos_especializados',
            'tipo_formulario', 'uf', 'regiao_turistica', 'municipio',
            'tipo', 'observacoes', 'referencias',
            'nome_pesquisador', 'telefone_pesquisador', 'email_pesquisador',
            'nome_coordenador', 'telefone_coordenador', 'email_coordenador'
        ]

    def create(self, validated_data):
        contatos_data = validated_data.pop('contatos', [])
        servicos_data = validated_data.pop('servicos_especializados', [])
        
        sistema_de_seguranca = LocadorasDeImoveis.objects.create(**validated_data)
        
        for contato_data in contatos_data:
            contato = InfoGerais.objects.create(**contato_data)
            sistema_de_seguranca.contatos.add(contato)
        
        for servico_data in servicos_data:
            servico = EnderecoInfo.objects.create(**servico_data)
            sistema_de_seguranca.servicos_especializados.add(servico)
        
        return sistema_de_seguranca

    def update(self, instance, validated_data):
        contatos_data = validated_data.pop('contatos', None)
        servicos_data = validated_data.pop('servicos_especializados', None)
        
        instance.tipo_formulario = validated_data.get('tipo_formulario', instance.tipo_formulario)
        instance.uf = validated_data.get('uf', instance.uf)
        instance.regiao_turistica = validated_data.get('regiao_turistica', instance.regiao_turistica)
        instance.municipio = validated_data.get('municipio', instance.municipio)
        instance.tipo = validated_data.get('tipo', instance.tipo)
        instance.observacoes = validated_data.get('observacoes', instance.observacoes)
        instance.referencias = validated_data.get('referencias', instance.referencias)
        instance.nome_pesquisador = validated_data.get('nome_pesquisador', instance.nome_pesquisador)
        instance.telefone_pesquisador = validated_data.get('telefone_pesquisador', instance.telefone_pesquisador)
        instance.email_pesquisador = validated_data.get('email_pesquisador', instance.email_pesquisador)
        instance.nome_coordenador = validated_data.get('nome_coordenador', instance.nome_coordenador)
        instance.telefone_coordenador = validated_data.get('telefone_coordenador', instance.telefone_coordenador)
        instance.email_coordenador = validated_data.get('email_coordenador', instance.email_coordenador)

        # Salva os campos principais atualizados
        instance.save()

        
        if contatos_data is not None:
            instance.contatos.clear()
            for contato_data in contatos_data:
                contato = InfoGerais.objects.create(**contato_data)
                instance.contatos.add(contato)
        
        if servicos_data is not None:
            instance.servicos_especializados.clear()
            for servico_data in servicos_data:
                servico = EnderecoInfo.objects.create(**servico_data)
                instance.servicos_especializados.add(servico)
        
        return instance
    
class InformacoesGuiamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = InformacoesGuiamento
        fields = ['nome_completo', 'cpf', 'email', 'endereco', 'telefone']

class InformacoesGuiamentoCadasturSerializer(serializers.ModelSerializer):
    class Meta:
        model = InformacoesGuiamentoCadastur
        fields = ['escolaridade', 'servicos_especializados_formulario', 'numero_cadastur', 'outras_informacoes', 'outros_cadastros']

class GuiamentoEConducaoTuristicaSerializer(serializers.ModelSerializer):
    contatos = InformacoesGuiamentoSerializer(many=True)  # Aninhando os dados completos
    servicos_especializados = InformacoesGuiamentoCadasturSerializer(many=True)

    
    class Meta:
        model = GuiamentoEConducaoTuristica
        fields = [
            'id', 'pesquisa', 'contatos', 'subtipos', 'servicos_especializados',
            'tipo_formulario', 'uf', 'regiao_turistica', 'municipio',
            'tipo', 'observacoes', 'referencias',
            'nome_pesquisador', 'telefone_pesquisador', 'email_pesquisador',
            'nome_coordenador', 'telefone_coordenador', 'email_coordenador'
        ]

    def create(self, validated_data):
        contatos_data = validated_data.pop('contatos', [])
        servicos_data = validated_data.pop('servicos_especializados', [])
        
        sistema_de_seguranca = GuiamentoEConducaoTuristica.objects.create(**validated_data)
        
        for contato_data in contatos_data:
            contato = InformacoesGuiamento.objects.create(**contato_data)
            sistema_de_seguranca.contatos.add(contato)
        
        for servico_data in servicos_data:
            servico = InformacoesGuiamentoCadastur.objects.create(**servico_data)
            sistema_de_seguranca.servicos_especializados.add(servico)
        
        return sistema_de_seguranca

    def update(self, instance, validated_data):
        contatos_data = validated_data.pop('contatos', None)
        servicos_data = validated_data.pop('servicos_especializados', None)
        
        instance.tipo_formulario = validated_data.get('tipo_formulario', instance.tipo_formulario)
        instance.uf = validated_data.get('uf', instance.uf)
        instance.regiao_turistica = validated_data.get('regiao_turistica', instance.regiao_turistica)
        instance.municipio = validated_data.get('municipio', instance.municipio)
        instance.tipo = validated_data.get('tipo', instance.tipo)
        instance.subtipos = validated_data.get('subtipos', instance.subtipos)
        instance.observacoes = validated_data.get('observacoes', instance.observacoes)
        instance.referencias = validated_data.get('referencias', instance.referencias)
        instance.nome_pesquisador = validated_data.get('nome_pesquisador', instance.nome_pesquisador)
        instance.telefone_pesquisador = validated_data.get('telefone_pesquisador', instance.telefone_pesquisador)
        instance.email_pesquisador = validated_data.get('email_pesquisador', instance.email_pesquisador)
        instance.nome_coordenador = validated_data.get('nome_coordenador', instance.nome_coordenador)
        instance.telefone_coordenador = validated_data.get('telefone_coordenador', instance.telefone_coordenador)
        instance.email_coordenador = validated_data.get('email_coordenador', instance.email_coordenador)

        # Salva os campos principais atualizados
        instance.save()

        
        if contatos_data is not None:
            instance.contatos.clear()
            for contato_data in contatos_data:
                contato = InformacoesGuiamento.objects.create(**contato_data)
                instance.contatos.add(contato)
        
        if servicos_data is not None:
            instance.servicos_especializados.clear()
            for servico_data in servicos_data:
                servico = InformacoesGuiamentoCadastur.objects.create(**servico_data)
                instance.servicos_especializados.add(servico)
        
        return instance

class GastronomiaArtesanatoInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GastronomiaArtesanatoInfo
        fields = ['nome_completo', 'atelie_aberto', 'email', 'endereco', 'telefone']

class GastronomiaArtesanatoInfoAtelieSerializer(serializers.ModelSerializer):
    class Meta:
        model = GastronomiaArtesanatoInfoAtelie
        fields = ['ano_inicio_atividade', 'premiacao', 'outras_informacoes',]

class GastronomiaArtesanatoSerializer(serializers.ModelSerializer):
    contatos = GastronomiaArtesanatoInfoSerializer(many=True)  # Aninhando os dados completos
    servicos_especializados = GastronomiaArtesanatoInfoAtelieSerializer(many=True)

    
    class Meta:
        model = GastronomiaArtesanato
        fields = [
            'id', 'pesquisa', 'contatos', 'subtipos', 'servicos_especializados',
            'tipo_formulario', 'uf', 'regiao_turistica', 'municipio',
            'tipo', 'observacoes', 'referencias',
            'nome_pesquisador', 'telefone_pesquisador', 'email_pesquisador',
            'nome_coordenador', 'telefone_coordenador', 'email_coordenador',
            'nomeProduto', 'historicoProduto01', 'historicoProduto02', 'historicoProduto03',
            'historicoProduto04', 'modoPreparo01', 'modoPreparo02', 'modoPreparo03', 'modoPreparo04',
            'integraRoteiros', 'integraGuiaTuristico', 'roteiro1', 'siteRoteiro1',
            'roteiro2', 'siteRoteiro2', 'roteiro3', 'siteRoteiro3', 'roteiro4',
            'siteRoteiro4', 'roteiro5', 'siteRoteiro5', 'Guia1', 'siteGuia1',
            'Guia2', 'siteGuia2', 'Guia3', 'siteGuia3', 'Guia4', 'siteGuia4',
            'Guia5', 'siteGuia5', 'locaisDeComercializacao', 'descritivoEspecialidades',
            'tabelaEquipamentoEEspaco', 'tabelaEquipamentoEEspaco2', 'doEquipamentoEspaco', 'daAreaOuEdificacaoEmQueEstaLocalizado'
        ]

    def create(self, validated_data):
        contatos_data = validated_data.pop('contatos', [])
        servicos_data = validated_data.pop('servicos_especializados', [])
        
        sistema_de_seguranca = GastronomiaArtesanato.objects.create(**validated_data)
        
        for contato_data in contatos_data:
            contato = GastronomiaArtesanatoInfo.objects.create(**contato_data)
            sistema_de_seguranca.contatos.add(contato)
        
        for servico_data in servicos_data:
            servico = GastronomiaArtesanatoInfoAtelie.objects.create(**servico_data)
            sistema_de_seguranca.servicos_especializados.add(servico)
        
        return sistema_de_seguranca

    def update(self, instance, validated_data):
        contatos_data = validated_data.pop('contatos', None)
        servicos_data = validated_data.pop('servicos_especializados', None)
        
        instance.tipo_formulario = validated_data.get('tipo_formulario', instance.tipo_formulario)
        instance.uf = validated_data.get('uf', instance.uf)
        instance.regiao_turistica = validated_data.get('regiao_turistica', instance.regiao_turistica)
        instance.municipio = validated_data.get('municipio', instance.municipio)
        instance.tipo = validated_data.get('tipo', instance.tipo)
        instance.subtipos = validated_data.get('subtipos', instance.subtipos)
        instance.nomeProduto = validated_data.get('nomeProduto', instance.nomeProduto)
        instance.historicoProduto01 = validated_data.get('historicoProduto01', instance.historicoProduto01)
        instance.historicoProduto02 = validated_data.get('historicoProduto02', instance.historicoProduto02)
        instance.historicoProduto03 = validated_data.get('historicoProduto03', instance.historicoProduto03)
        instance.historicoProduto04 = validated_data.get('historicoProduto04', instance.historicoProduto04)
        instance.modoPreparo01 = validated_data.get('modoPreparo01', instance.modoPreparo01)
        instance.modoPreparo02 = validated_data.get('modoPreparo02', instance.modoPreparo02)
        instance.modoPreparo03 = validated_data.get('modoPreparo03', instance.modoPreparo03)
        instance.modoPreparo04 = validated_data.get('modoPreparo04', instance.modoPreparo04)
        instance.integraRoteiros = validated_data.get('integraRoteiros', instance.integraRoteiros)
        instance.integraGuiaTuristico = validated_data.get('integraGuiaTuristico', instance.integraGuiaTuristico)
        instance.roteiro1 = validated_data.get('roteiro1', instance.roteiro1)
        instance.siteRoteiro1 = validated_data.get('siteRoteiro1', instance.siteRoteiro1)
        instance.roteiro2 = validated_data.get('roteiro2', instance.roteiro2)
        instance.siteRoteiro2 = validated_data.get('siteRoteiro2', instance.siteRoteiro2)
        instance.roteiro3 = validated_data.get('roteiro3', instance.roteiro3)
        instance.siteRoteiro3 = validated_data.get('siteRoteiro3', instance.siteRoteiro3)
        instance.roteiro4 = validated_data.get('roteiro4', instance.roteiro4)
        instance.siteRoteiro4 = validated_data.get('siteRoteiro4', instance.siteRoteiro4)
        instance.roteiro5 = validated_data.get('roteiro5', instance.roteiro5)
        instance.siteRoteiro5 = validated_data.get('siteRoteiro5', instance.siteRoteiro5)
        instance.Guia1 = validated_data.get('Guia1', instance.Guia1)
        instance.siteGuia1 = validated_data.get('siteGuia1', instance.siteGuia1)
        instance.Guia2 = validated_data.get('Guia2', instance.Guia2)
        instance.siteGuia2 = validated_data.get('siteGuia2', instance.siteGuia2)
        instance.Guia3 = validated_data.get('Guia3', instance.Guia3)
        instance.siteGuia3 = validated_data.get('siteGuia3', instance.siteGuia3)
        instance.Guia4 = validated_data.get('Guia4', instance.Guia4)
        instance.siteGuia4 = validated_data.get('siteGuia4', instance.siteGuia4)
        instance.Guia5 = validated_data.get('Guia5', instance.Guia5)
        instance.siteGuia5 = validated_data.get('siteGuia5', instance.siteGuia5)
        instance.locaisDeComercializacao = validated_data.get('locaisDeComercializacao', instance.locaisDeComercializacao)
        instance.descritivoEspecialidades = validated_data.get('descritivoEspecialidades', instance.descritivoEspecialidades)
        instance.subtipos = validated_data.get('subtipos', instance.subtipos)
        instance.observacoes = validated_data.get('observacoes', instance.observacoes)
        instance.referencias = validated_data.get('referencias', instance.referencias)
        instance.nome_pesquisador = validated_data.get('nome_pesquisador', instance.nome_pesquisador)
        instance.telefone_pesquisador = validated_data.get('telefone_pesquisador', instance.telefone_pesquisador)
        instance.email_pesquisador = validated_data.get('email_pesquisador', instance.email_pesquisador)
        instance.nome_coordenador = validated_data.get('nome_coordenador', instance.nome_coordenador)
        instance.telefone_coordenador = validated_data.get('telefone_coordenador', instance.telefone_coordenador)
        instance.email_coordenador = validated_data.get('email_coordenador', instance.email_coordenador)
        instance.tabelaEquipamentoEEspaco = validated_data.get('tabelaEquipamentoEEspaco', instance.tabelaEquipamentoEEspaco)
        instance.tabelaEquipamentoEEspaco2 = validated_data.get('tabelaEquipamentoEEspaco2', instance.tabelaEquipamentoEEspaco2)
        instance.doEquipamentoEspaco= validated_data.get('doEquipamentoEspaco', instance.doEquipamentoEspaco)
        instance.daAreaOuEdificacaoEmQueEstaLocalizado = validated_data.get('daAreaOuEdificacaoEmQueEstaLocalizado', instance.daAreaOuEdificacaoEmQueEstaLocalizado)
        # Salva os campos principais atualizados
        instance.save()

        
        if contatos_data is not None:
            instance.contatos.clear()
            for contato_data in contatos_data:
                contato = GastronomiaArtesanatoInfo.objects.create(**contato_data)
                instance.contatos.add(contato)
        
        if servicos_data is not None:
            instance.servicos_especializados.clear()
            for servico_data in servicos_data:
                servico = GastronomiaArtesanatoInfoAtelie.objects.create(**servico_data)
                instance.servicos_especializados.add(servico)
        
        return instance



class SistemaDeSegurancaSerializer(serializers.ModelSerializer):
    contatos = ContatoInfoSerializer(many=True)  # Aninhando os dados completos
    servicos_especializados = ServicoEspecializadoInfoSerializer(many=True)

    
    class Meta:
        model = SistemaDeSeguranca
        fields = [
            'id', 'pesquisa', 'contatos', 'servicos_especializados',
            'tipo_formulario', 'uf', 'regiao_turistica', 'municipio',
            'tipo', 'observacoes', 'referencias',
            'nome_pesquisador', 'telefone_pesquisador', 'email_pesquisador',
            'nome_coordenador', 'telefone_coordenador', 'email_coordenador'
        ]

    def create(self, validated_data):
        contatos_data = validated_data.pop('contatos', [])
        servicos_data = validated_data.pop('servicos_especializados', [])
        
        sistema_de_seguranca = SistemaDeSeguranca.objects.create(**validated_data)
        
        for contato_data in contatos_data:
            contato = ContatoInfo.objects.create(**contato_data)
            sistema_de_seguranca.contatos.add(contato)
        
        for servico_data in servicos_data:
            servico = ServicoEspecializadoInfo.objects.create(**servico_data)
            sistema_de_seguranca.servicos_especializados.add(servico)
        
        return sistema_de_seguranca

    def update(self, instance, validated_data):
        contatos_data = validated_data.pop('contatos', None)
        servicos_data = validated_data.pop('servicos_especializados', None)
        
        instance.tipo_formulario = validated_data.get('tipo_formulario', instance.tipo_formulario)
        instance.uf = validated_data.get('uf', instance.uf)
        instance.regiao_turistica = validated_data.get('regiao_turistica', instance.regiao_turistica)
        instance.municipio = validated_data.get('municipio', instance.municipio)
        instance.tipo = validated_data.get('tipo', instance.tipo)
        instance.observacoes = validated_data.get('observacoes', instance.observacoes)
        instance.referencias = validated_data.get('referencias', instance.referencias)
        instance.nome_pesquisador = validated_data.get('nome_pesquisador', instance.nome_pesquisador)
        instance.telefone_pesquisador = validated_data.get('telefone_pesquisador', instance.telefone_pesquisador)
        instance.email_pesquisador = validated_data.get('email_pesquisador', instance.email_pesquisador)
        instance.nome_coordenador = validated_data.get('nome_coordenador', instance.nome_coordenador)
        instance.telefone_coordenador = validated_data.get('telefone_coordenador', instance.telefone_coordenador)
        instance.email_coordenador = validated_data.get('email_coordenador', instance.email_coordenador)

        # Salva os campos principais atualizados
        instance.save()

        
        if contatos_data is not None:
            instance.contatos.clear()
            for contato_data in contatos_data:
                contato = ContatoInfo.objects.create(**contato_data)
                instance.contatos.add(contato)
        
        if servicos_data is not None:
            instance.servicos_especializados.clear()
            for servico_data in servicos_data:
                servico = ServicoEspecializadoInfo.objects.create(**servico_data)
                instance.servicos_especializados.add(servico)
        
        return instance

class RodoviaSerializer(serializers.ModelSerializer):
    # tipo_de_organizacao_instituicao = serializers.PrimaryKeyRelatedField(many=True, queryset=TipoOrganizacao.objects.all())
    # posto_de_combustivel = serializers.PrimaryKeyRelatedField(many=True, queryset=PostoDeCombustivel.objects.all())
    # outros_servicos = serializers.PrimaryKeyRelatedField(many=True, queryset=OutrosServicos.objects.all())
    # estruturas_ao_longo_da_vida = serializers.PrimaryKeyRelatedField(many=True, queryset=EstruturasAoLongoDaVia.objects.all())

    class Meta:
        model = Rodovia
        fields = '__all__'  # ou especifique os campos que você deseja incluir

class AlimentosEBebidasSerializer(serializers.ModelSerializer):

    class Meta:
        model = AlimentosEBebidas
        fields = '__all__'

class MeioDeHospedagemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeioDeHospedagem
        fields = '__all__'

class OutrosMeiosDeHospedagemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutrosMeiosDeHospedagem
        fields = '__all__'

class AgenciaDeTurismoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgenciaDeTurismo
        fields = '__all__'

class TransporteTuristicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransporteTuristico
        fields = '__all__'
        
class ComercioTuristicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComercioTuristico
        fields = '__all__'

class EspacoParaEventosSerializer(serializers.ModelSerializer):
    class Meta:
        model = EspacoParaEventos
        fields = '__all__'
        
class ServicosParaEventosSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicosParaEventos
        fields = '__all__'

class ParquesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parques
        fields = '__all__'

class EspacosDeDiversaoECulturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EspacosDeDiversaoECultura
        fields = '__all__'

class InformacoesTuristicasSerializer(serializers.ModelSerializer):
    class Meta:
        model = InformacoesTuristicas
        fields = '__all__'
        
class EntidadesAssociativasSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntidadesAssociativas
        fields = '__all__'

class UnidadesDeConservacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadesDeConservacao
        fields = '__all__'

class EventosProgramadosSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventosProgramados
        fields = '__all__'
        
class InformacoesBasicasSerializer(serializers.ModelSerializer):
    class Meta:
        model = InformacaoBasicaDoMunicipio
        fields = '__all__'
        
class InstalacoesEsportivasSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstalacoesEsportivas
        fields = '__all__'

class EquipamentoSerializer(serializers.Serializer):
    tipo = serializers.CharField()
    dados = serializers.JSONField()

class DynamicBaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Base
        fields = '__all__'

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = CustomUser.objects.get(email=value)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Nenhum usuário com esse email foi encontrado")

        user.generate_otp()
        send_mail(
            "Código para recuperar sua senha",
            f"Seu código para recuperar sua senha é: {user.otp}",
            "britomurilorog@gmail.com",
            [user.email],
            fail_silently=False
        )
        return value

class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            user = CustomUser.objects.get(email=data["email"])
        except CustomUser.DoesNotExist:   
            raise serializers.ValidationError({"email": "usuário não encontrado."})
        
        if user.otp!=data["otp"]:
            raise serializers.ValidationError({"otp": "OTP invalido"})
        
        if user.otp_exp < now():
            raise serializers.ValidationError({"otp": "OTP expirado"})

        user.otp_verified = True
        user.save()

        return data

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            user = CustomUser.objects.get(email=data["email"])
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({"email": "user não encontrado"})

        if not user.otp_verified:
            raise serializers.ValidationError({"otp": "verificação por OTP necessária"})
        
        return data

    
    def save(self, **kwargs):
        user = CustomUser.objects.get(email=self.validated_data["email"])
        user.set_password(self.validated_data["new_password"])
        user.otp = None  # Clear OTP after successful reset
        user.otp_exp = None
        user.otp_verified = False  # Reset verification status
        user.save()
        return user