"""
Parasyti nesudėtingą biudžeto programą taip,
kad joje būtų atvaizduojami konkretaus vartotojo biudžeto įrašai
ir jie būtų matomi tik jam prisijungus.
"""
from budget_prog import app
if __name__ == '__main__':
     app.run(host='127.0.0.1', port=5000, debug=True)
