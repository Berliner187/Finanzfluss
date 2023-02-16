from datetime import datetime


class AssetCalculation:
    """
        Класс расчетных операций по вкладу и накопительному счету
        self.initial_investment_amount - сумма первоначальных вложений
        self.annual_rate - годовая ставка, в процентах
    """
    def __init__(self, amount, annual_rate):
        self.investment_amount = amount
        self.annual_rate = annual_rate

    @staticmethod
    def get_number_days_in_year():
        year_now = datetime.now().year
        if year_now % 4 == 0: return 366
        else: return 365

    # <--- Расчет простых процентов --->
    def calculation_capitalization(self, number_of_deposit_days):
        return (self.investment_amount * self.annual_rate * number_of_deposit_days / self.get_number_days_in_year()) / 100

    # <--- Расчет сложных процентов --->
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


class PassiveCalculation:
    def __init__(self, amount, annual_rate, term):
        self.amount = amount
        self.annual_rate = annual_rate
        self.term = term

    # <--- Аннуитетный кредит --->
    # Расчет ежемесячного платежа
    def monthly_payment(self):
        annual_rate = self.annual_rate / (100 * 12)
        return round(self.amount * (annual_rate / (1 - (1 + annual_rate) ** -self.term)), 2)

    def total_overpayment(self):
        return round((self.monthly_payment() * self.term) - self.amount, 2)


# print(AssetCalculation(59500, 6).calculation_capitalization(30))
print(PassiveCalculation(20_000, 12, 36).monthly_payment())
print(PassiveCalculation(20_000, 12, 36).total_overpayment())
