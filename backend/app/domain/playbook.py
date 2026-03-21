"""Hardcoded playbook clauses for Lavanderia 60 Minutos franchise contracts."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PlaybookClause:
    """A standard clause from the franchise playbook."""

    code: str
    title: str
    full_text: str
    category: str


PLAYBOOK_CLAUSES: list[PlaybookClause] = [
    PlaybookClause(
        code="INFRAESTRUTURA",
        title="Ciência da Infraestrutura",
        category="infraestrutura",
        full_text=(
            "O LOCADOR, neste ato, em conformidade com o art. 22 da lei 8.245/9, "
            "manifesta sua ciência quanto à necessidade por parte da LOCATÁRIA, em que "
            "pese a infraestrutura e licenças mínima necessária para viabilizar a "
            "implantação e operação da atividade econômica a ser explorada, qual seja, "
            "lavanderia de autoatendimento, as quais incluem rede fornecedora de água, "
            "rede coletora de esgoto, rede elétrica no sistema trifásico, licenças, "
            "alvarás de funcionamento no CNAE de lavanderias)."
        ),
    ),
    PlaybookClause(
        code="RESCISAO_INFRAESTRUTURA",
        title="Rescisão por Inviabilidade de Infraestrutura",
        category="infraestrutura",
        full_text=(
            "Caso a infraestrutura do imóvel (rede de água, esgoto ou elétrica) não "
            "atenda às necessidades da LOCATÁRIA, assim como a inviabilidade técnica ou "
            "legal (licenças dos órgãos públicos) para a implantação da loja, a presente "
            "avença será rescindida de pleno direito, sem que isto implique em qualquer "
            "penalidade, tanto para o LOCADOR quanto para o LOCATÁRIO, garantido ao "
            "LOCADOR o recebimento dos aluguéis até a data de entrega do ponto."
        ),
    ),
    PlaybookClause(
        code="CONDOMINIO",
        title="Declaração Condominial",
        category="infraestrutura",
        full_text=(
            "O LOCADOR declara, neste ato, que inexiste qualquer estatuto ou convenção "
            "condominial que vincule o presente instrumento."
        ),
    ),
    PlaybookClause(
        code="OBRAS",
        title="Das Obras",
        category="obras",
        full_text=(
            "O LOCATÁRIO não poderá realizar qualquer modificação ou benfeitoria "
            "estrutural no imóvel, objeto da presente locação, sem a prévia e expressa "
            "autorização por escrito do LOCADOR, não podendo os mesmos, de qualquer "
            "forma, prejudicar a solidez, segurança, estrutura e estética do prédio, "
            "devendo, ainda, observar as leis, posturas e regulamentos pertinentes, "
            "responsabilizando-se por eventuais multas e penalidades.\n\n"
            "PARÁGRAFO ÚNICO: o LOCADOR, ciente das necessidades por parte da LOCATÁRIA "
            "da infraestrutura e licenças mínima necessária para viabilizar a implantação "
            "e operação da atividade econômica a ser explorada, autoriza de forma prévia, "
            "com base no art. 22 da lei 8.245/9, a realização das seguintes melhorias:\n"
            "- Adaptação da rede elétrica, adequando-a às necessidades das atividades do "
            "LOCATÁRIO, incluindo a mudança para o sistema trifásico, caso ainda não "
            "tenha;\n"
            "- Instalação na parte interna do imóvel de equipamentos de autoatendimento, "
            "luminarias e tomadas, respeitando o padrão da franquia;\n"
            "- Adesivos que se fizerem necessários à identificação da marca Lavanderia "
            "60 Minutos, tanto na parte interna quanto na parte externa do imóvel, "
            "respeitando sempre as dimensões, o layout da marca, assim como as Leis "
            "Municipais vigentes e estatutos condominiais que existirem;\n"
            "- Instalação de divisória interna;\n"
            "- Instalação de ACM e luminoso na fachada do imóvel, respeitando sempre as "
            "dimensões, o layout da marca, assim como as Leis Municipais vigentes e "
            "estatutos condominiais que existirem;\n"
            "- Reforma/troca do piso interno, caso necessário;\n"
            "- Instalação/adaptação de condicionador e exaustor de ar;\n"
            "- Adaptação da rede de água e esgoto, conforme necessidade da LOCATÁRIA;\n"
            "- Instalação de um relógio medidor para a devida aferição mensal do consumo "
            "de água e/ou energia elétrica, caso não exista."
        ),
    ),
    PlaybookClause(
        code="EXCLUSIVIDADE",
        title="Da Exclusividade",
        category="comercial",
        full_text=(
            "Fica acordado que o LOCADOR não locará, sublocará ou explorará, ponto ou "
            "espaço comercial, dentro do mesmo imóvel para todas e quaisquer outras "
            "atividades de lavanderias ou afins."
        ),
    ),
    PlaybookClause(
        code="PRAZO",
        title="Do Prazo",
        category="temporal",
        full_text=(
            "Não havendo comunicação em contrário, por qualquer das partes, com no "
            "mínimo 90 (noventa) dias antes do encerramento dele, este contrato de "
            "imóvel será renovado automaticamente por igual período."
        ),
    ),
    PlaybookClause(
        code="VISTORIAS",
        title="Das Vistorias",
        category="operacional",
        full_text=(
            "Toda e qualquer vistoria deverá, compulsoriamente, ser realizada na "
            "presença do LOCATÁRIO ou pessoa por este indicado, sob pena de infração "
            "contratual além das responsabilizações civis e criminais possíveis."
        ),
    ),
    PlaybookClause(
        code="CESSAO",
        title="Da Cessão",
        category="comercial",
        full_text=(
            "É expressamente proibido ao LOCATÁRIO sublocar, ceder ou emprestar, a "
            "qualquer título, o imóvel, no todo ou em parte, ou transferir o presente "
            "contrato, sob pena de reconhecida infração contratual, sendo possível a sua "
            "rescisão motivada.\n\n"
            "PARÁGRAFO PRIMEIRO: Resta acordado entre as PARTES, de forma excepcional, "
            "que será autorizada a exploração do ponto comercial ora avençado, "
            "exclusivamente, aos seus franqueados e parceiros comerciais, sem qualquer "
            "tipo de cobrança ou ônus em virtude de tal transação.\n\n"
            "PARÁGRAFO SEGUNDO: Ocorrendo a necessidade de substituição do FIADOR, fica "
            "a LOCATÁRIA compelida a apresentar um novo FIADOR para a APROVAÇÃO DA "
            "ADMINISTRADORA, ou, se preferir, que a garantia seja substituída pela "
            "modalidade pactuada entre as partes.\n\n"
            "PARÁGRAFO TERCEIRO: Sob nenhuma hipótese poderá ser alterado a destinação "
            "do ponto ora locado que lhe atribui a Cláusula I deste contrato, "
            "permanecendo a LOCATÁRIA responsável pelo presente contrato independentemente "
            "da realização da citada cessão."
        ),
    ),
    PlaybookClause(
        code="OBRIGACAO_NAO_FAZER",
        title="Da Obrigação de Não Fazer",
        category="comercial",
        full_text=(
            "Caso se opere o distrato do presente instrumento ou não efetive-se sua "
            "renovação por decisão unilateral do LOCADOR, este fica impedido de locar o "
            "ponto fruto desta negociação para quaisquer atividades de lavanderia ou "
            "afins pelo prazo de 24 (vinte e quatro) meses, conforme Lei nº 8.245/91 "
            "(Lei do Inquilinato); Art. 52, II, §1º.\n\n"
            "PARÁGRAFO ÚNICO: A aplicação das multas previstas neste contrato não exime "
            "a obrigação de não fazer determinada no caput desta cláusula, conforme Lei "
            "do Inquilinato (Lei nº 8.245/91)."
        ),
    ),
]


def get_clause_by_code(code: str) -> PlaybookClause | None:
    """Return a playbook clause by its code, or None if not found."""
    for clause in PLAYBOOK_CLAUSES:
        if clause.code == code:
            return clause
    return None
