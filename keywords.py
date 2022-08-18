brands = [['Vinataba', 'Tổng công ty thuốc lá Việt Nam'],
          ['British American Tobacco', 'BAT'],
          ["Philip Morris International", 'PMI', 'Philip Morris Việt Nam', 'Philip Morris', "Phillip Morris International", 'Phillip Morris Việt Nam', 'Phillip Morris'],
          ['Thuốc lá Sài Gòn'],
          ['Thuốc lá Thăng Long']]

intents = ['ủng hộ', 'tài trợ', 'xây dựng', 'hỗ trợ']

keywords = [
    {
        'keyword': [[b, intent] for b in brand for intent in intents],
        'brand': brand[0],
        'type': 'vi pham_1'
    } for brand in brands]

type_1 = []

# keywords = [[brand, intent] for brand in brands for intent in intents]
