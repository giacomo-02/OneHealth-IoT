def classifica(
    ecoli,
    enterococchi
):

    if ecoli is None or enterococchi is None:
        return "Sconosciuta"


    if ecoli <= 100 and enterococchi <= 40:
        return "Eccellente"


    if ecoli <= 250 and enterococchi <= 100:
        return "Buona"


    if ecoli <= 500 and enterococchi <= 200:
        return "Sufficiente"


    return "Scarsa"



def genera_alert(
    ecoli,
    enterococchi
):

    alerts = []


    if ecoli is not None:

        if ecoli > 500:
            alerts.append(
                f"CRITICO:E.coli>{ecoli}"
            )

        elif ecoli > 250:
            alerts.append(
                f"ALLERTA:E.coli>{ecoli}"
            )


    if enterococchi is not None:

        if enterococchi > 200:
            alerts.append(
                f"CRITICO:Enterococchi>{enterococchi}"
            )

        elif enterococchi > 100:
            alerts.append(
                f"ALLERTA:Enterococchi>{enterococchi}"
            )


    return alerts



def analizza_arpa(
    ecoli,
    enterococchi
):

    alert = genera_alert(
        ecoli,
        enterococchi
    )


    return {

        "classificazione":
            classifica(
                ecoli,
                enterococchi
            ),

        "alert":
            alert,

        "ha_alert":
            len(alert) > 0

    }
