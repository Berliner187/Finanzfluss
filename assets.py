from datetime import datetime


class AccumulationAccounts:
    """
        Расчет дохода по вкладу
        self.initial_investment_amount - сумма первоначальных вложений
    """
    def __init__(self, amount, annual_rate):
        self.investment_amount = amount
        self.annual_rate = annual_rate

    @staticmethod
    def get_number_days_in_year():
        year_now = datetime.now().year
        if year_now % 4 == 0:
            return 366
        else:
            return 365

    # Расчет простого процента
    def calculation_capitalization(self, number_of_deposit_days):
        return (self.investment_amount *
                self.annual_rate * number_of_deposit_days /
                self.get_number_days_in_year()) / 100

    # Расчет сложных процентов
    # Ежедневная капитализация
    def calculation_daily_capitalization(self, number_of_deposit_days):
        N = self.annual_rate / 100
        K = self.get_number_days_in_year()
        T = number_of_deposit_days
        capitalization = self.investment_amount * (1 + N / K) ** T
        return round(capitalization - self.investment_amount, 2)

    # Ежемесячная капитализация
    def calculation_monthly_capitalization(self, months):
        capitalization = self.investment_amount * (1 + self.annual_rate / 100 / 12) ** months
        return round(capitalization - self.investment_amount, 2)


# print(AccumulationAccounts(25500, 6).calculation_monthly_capitalization(6))
