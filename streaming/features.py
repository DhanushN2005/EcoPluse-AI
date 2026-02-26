# Feature engineering logic for environmental data
def calculate_momentum(history):
    if len(history) < 2: return 0.0
    return history[-1] - history[-2]

def heat_index(temp, humidity):
    return temp + 0.55 * (humidity / 100) * (temp - 14.5)
