
import json
from pathlib import Path
import streamlit as st
from ia import analisar

st.set_page_config(page_title="Orienta IA")
st.title("Orienta IA")
st.warning("Protótipo com instituições e preços fictícios.")
st.caption("Explore possibilidades. Você decide seu caminho.")

try:
    caminho = Path(__file__).with_name("base.json")
    base = json.loads(caminho.read_text(encoding="utf-8"))

except (OSError, json.JSONDecodeError):
    st.error("Confira o arquivo base.json e sua formatação.")
    st.stop()

with st.form("perfil"):
    interesses = st.text_area(
        "O que você gosta de fazer?",
        max_chars=1000
    )

    objetivo = st.selectbox("Seu objetivo", [
        "Escolher uma graduação", "Entrar no mercado",
        "Mudar de área"
    ])

    area = st.selectbox("Área", sorted({x["area"] for x in base}))
    cidade = st.selectbox("Cidade", sorted({x["cidade"] for x in base}))

    rotina = st.text_input(
        "Horários e preferências de estudo",
        max_chars=300
    )

    limite = st.number_input(
        "Orçamento mensal em reais",
        min_value=0.0,
        step=50.0
    )

    consentiu = st.checkbox(
        "Autorizo enviar interesses, objetivo e rotina à API de IA."
    )

    st.caption("Não informe nome, CPF, telefone ou documentos.")
    enviou = st.form_submit_button("Comparar e analisar")

    if enviou:
        if not interesses.strip():
            st.error("Descreva pelo menos um interesse.")
            st.stop()

        ofertas = [
            x for x in base
            if x["area"] == area and x["cidade"] == cidade
        ]

        if not ofertas:
            st.info("Sem registros para os filtros selecionados.")
            st.stop()

        for o in ofertas:
            with st.expander(
                o["curso"] + " | " + o["instituicao"],
                expanded=True
            ):
                st.write(o["rotina"])
                st.write("Tipo:", o["tipo"], "| Turno:", o["turno"])
                st.write("Ingresso:", o["ingresso"])
                st.write("Condição da bolsa:", o["condicao_bolsa"])

                valor = o["mensalidade_integral"]
                bolsa = o["bolsa_percentual"]

                if valor is None or bolsa is None:
                    st.write("Preço completo não disponível.")
                else:
                    liquido = round(valor * (1 - bolsa / 100), 2)
                    total = round(liquido * o["duracao_meses"], 2)

                    st.write(f"Integral mensal: R$ {valor:.2f}")
                    st.write(f"Simulado após bolsa: R$ {liquido:.2f}")
                    st.write(f"Total sem reajustes e extras: R$ {total:.2f}")
                    st.write("Dentro do orçamento mensal:", liquido <= limite)

                st.write(
                    "Salário médio:",
                    o["salario_medio"]
                    if o["salario_medio"] is not None
                    else "Não disponível"
                )

                st.write(
                    "Nota de corte:",
                    o["nota_corte"]
                    if o["nota_corte"] is not None
                    else "Não disponível"
                )

                st.caption(
                    o["id"] + " | " + o["fonte"]
                    + " | Consulta: " + o["consultado_em"]
                )

        if consentiu:
            perfil = {
                "interesses": interesses,
                "objetivo": objetivo,
                "rotina": rotina
            }

            with st.spinner("Analisando as opções..."):
                texto = analisar(perfil, ofertas)

            st.subheader("Análise da IA")
            st.text(texto)
            st.caption("Confira os fatos nos registros acima.")

        else:
            st.info("Comparação local concluída, sem envio à IA.")