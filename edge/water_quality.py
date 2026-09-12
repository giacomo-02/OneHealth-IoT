def calculate_wqi(measurements):

    score = 100


    ph = measurements["ph"]

    if ph < 6.5 or ph > 9:
        score -= 20


    turbidity = measurements["turbidity"]

    if turbidity > 10:
        score -= 30

    elif turbidity > 5:
        score -= 15


    oxygen = measurements["dissolved_oxygen"]

    if oxygen < 5:
        score -= 30

    elif oxygen < 7:
        score -= 15


    nitrates = measurements["nitrates"]

    if nitrates > 20:
        score -= 20

    elif nitrates > 10:
        score -= 10


    ecoli = measurements["ecoli"]

    if ecoli > 1000:
        score -= 40

    elif ecoli > 500:
        score -= 25

    elif ecoli > 100:
        score -= 10


    enterococci = measurements["enterococci"]

    if enterococci > 700:
        score -= 30

    elif enterococci > 300:
        score -= 15


    return max(score, 0)



def classify_quality(wqi):

    if wqi >= 90:
        return "Eccellente"

    elif wqi >= 70:
        return "Buona"

    elif wqi >= 50:
        return "Sufficiente"

    else:
        return "Scarsa"


def analyze_water(measurements):

    wqi = calculate_wqi(measurements)

    classification = classify_quality(wqi)

    return {
        "wqi": wqi,
        "status": classification
    }
