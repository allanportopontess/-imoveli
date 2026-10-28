"""Lê o calendário iCal exportado pelo Airbnb e grava agenda.json para a LP.

Uso: python3 tools/sync_agenda.py "<link .ics do Airbnb>"
     (ou defina a variável AIRBNB_ICAL_URL)

agenda.json guarda as noites ocupadas como intervalos [início, fim),
no mesmo formato do iCal: o dia de saída fica livre para nova chegada.
"""
import datetime as dt
import json
import os
import re
import sys
import urllib.request

AQUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(AQUI, "agenda.json")
FUSO = dt.timezone(dt.timedelta(hours=-3))  # America/Recife


def baixar(url):
    req = urllib.request.Request(url, headers={"User-Agent": "RefugioUrbanoSync/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def ler_data(valor):
    valor = valor.strip()[:8]
    return dt.date(int(valor[:4]), int(valor[4:6]), int(valor[6:8]))


def intervalos(ics):
    texto = re.sub(r"\r?\n[ \t]", "", ics)  # desfaz linhas dobradas do iCal
    hoje = dt.datetime.now(FUSO).date()
    saida = []
    for bloco in re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", texto, re.S):
        ini = re.search(r"^DTSTART[^:]*:(\S+)", bloco, re.M)
        fim = re.search(r"^DTEND[^:]*:(\S+)", bloco, re.M)
        if not ini:
            continue
        a = ler_data(ini.group(1))
        b = ler_data(fim.group(1)) if fim else a + dt.timedelta(days=1)
        if b > hoje:
            saida.append([max(a, hoje).isoformat(), b.isoformat()])
    return sorted(saida)


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("AIRBNB_ICAL_URL", "")
    if not url:
        sys.exit("Informe o link .ics do Airbnb.")
    ics = baixar(url)
    if "BEGIN:VCALENDAR" not in ics:
        sys.exit("O link não devolveu um calendário iCal.")
    dados = {
        "atualizado": dt.datetime.now(FUSO).isoformat(timespec="minutes"),
        "bloqueados": intervalos(ics),
    }
    try:
        with open(SAIDA, encoding="utf-8") as f:
            if json.load(f).get("bloqueados") == dados["bloqueados"]:
                print("Agenda sem mudanças.")
                return
    except (OSError, ValueError):
        pass
    with open(SAIDA, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=1)
    print(f"{len(dados['bloqueados'])} períodos ocupados gravados em agenda.json")


if __name__ == "__main__":
    main()
