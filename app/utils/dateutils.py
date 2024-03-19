from datetime import datetime

def dernier_jour_du_mois(month, year):
    """
        La fonction prend en entrée un mois (1-12) et une année et renvoie le dernier jour du mois sous forme d'objet (datetime).
    """
    # Les mois avec trente jours.
    thirty_day_months = {4, 6, 9, 11}

    # Vérification d'année bissextile.
    if month == 2:
        is_leap_year = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
        last_day = 29 if is_leap_year else 28
    elif month in thirty_day_months:
        last_day = 30
    else:
        last_day = 31

    # Créé une date située sur le dernier jour du mois puis la renvoie.
    last_day_of_month = datetime(year, month, last_day)
    return last_day_of_month
