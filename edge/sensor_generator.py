import random
import math
from datetime import datetime


def seasonal_factor():
    month = datetime.now().month

    if month in [6, 7, 8]:
        return 1.15
    elif month in [9, 10]:
        return 1.05
    elif month in [11, 12, 1, 2]:
        return 0.85
    else:
        return 0.95


def rain_factor():
    # simulazione pioggia/eventi di dilavamento
    return 1.4 if random.random() < 0.15 else 1.0


def generate_measurements(risk=0, zona=None):

    stagione = seasonal_factor()
    pioggia = rain_factor()

    risk = max(0, min(1, risk))


    temperature = round(
        14 +
        10 * math.sin(
            (datetime.now().month - 3) * math.pi / 6
        )
        + random.gauss(0, 0.5),
        2
    )


    ph = round(
        max(
            6.5,
            min(
                9,
                random.gauss(
                    8.1 - risk * 0.4,
                    0.1
                )
            )
        ),
        2
    )


    turbidity = round(
        max(
            0.1,
            random.gauss(3,1)
            *
            (1 + risk * 4)
            *
            stagione
            *
            pioggia
        ),
        2
    )


    conductivity = round(
        max(
            30,
            random.gauss(
                52,
                2
            )
            *
            (1-risk*0.15)
        ),
        2
    )


    dissolved_oxygen = round(
        max(
            2,
            random.gauss(
                8,
                0.5
            )
            -
            risk*2.5
            -
            (temperature-20)*0.1
        ),
        2
    )


    nitrates = round(
        max(
            0.1,
            random.gauss(
                5,
                1.5
            )
            *
            (1+risk*4)
            *
            stagione
        ),
        2
    )


    phosphates = round(
        max(
            0.01,
            random.gauss(
                0.1,
                0.05
            )
            *
            (1+risk*8)
            *
            pioggia
        ),
        3
    )


    chlorophyll = round(
        max(
            0.1,
            random.gauss(
                2,
                0.8
            )
            *
            stagione
            *
            (1+risk*2)
        ),
        2
    )


    ecoli = int(
        max(
            1,
            random.gauss(
                20,
                10
            )
            *
            (1+risk*40)
            *
            stagione
            *
            pioggia
        )
    )


    enterococci = int(
        max(
            0,
            random.gauss(
                8,
                4
            )
            *
            (1+risk*18)
            *
            stagione
            *
            pioggia
        )
    )


    lead = round(
        max(
            0.01,
            random.gauss(
                0.5,
                0.2
            )
            *
            (1+risk*15)
        ),
        3
    )


    mercury = round(
        max(
            0.001,
            random.gauss(
                0.05,
                0.02
            )
            *
            (1+risk*20)
        ),
        4
    )


    arsenic = round(
        max(
            0.1,
            random.gauss(
                1.5,
                0.5
            )
            *
            (1+risk*12)
        ),
        3
    )


    cadmium = round(
        max(
            0.001,
            random.gauss(
                0.03,
                0.01
            )
            *
            (1+risk*30)
        ),
        4
    )


    chlorine = round(
        max(
            0,
            random.gauss(
                0.2,
                0.03
            )
        ),
        3
    )


    orp = round(
        max(
            50,
            random.gauss(
                280,
                25
            )
            -
            risk*200
        ),
        2
    )


    return {

        "ph": ph,

        "temperature": temperature,

        "turbidity": turbidity,

        "conductivity": conductivity,

        "dissolved_oxygen": dissolved_oxygen,


        "nitrates": nitrates,

        "phosphates": phosphates,

        "chlorophyll_a": chlorophyll,


        "ecoli": ecoli,

        "enterococci": enterococci,


        "lead": lead,

        "mercury": mercury,

        "arsenic": arsenic,

        "cadmium": cadmium,


        "chlorine": chlorine,

        "orp": orp
    }
