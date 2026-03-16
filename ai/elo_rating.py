def calculate_elo(win, lose):

    base = 1500

    rating = base + (win - lose) * 10

    return rating
