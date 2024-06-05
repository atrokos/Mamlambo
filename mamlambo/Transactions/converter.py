from typing import Any


class Converter:
    def __init__(self, conversion_data: list[dict[str, Any]]) -> None:
        self._conversions: dict[str, set[str]] = dict()
        self._conversion_values: dict[str, dict[str, float]] = dict()
        self._find_conversions(conversion_data)

    def convert(self, from_currency: str, to_currency: str, value: float) -> str:
        if from_currency == to_currency:
            return "{:.2f}".format(value)

        try:
            return "{:.2f}".format(value * self._conversion_values[from_currency][to_currency])
        except KeyError:
            return "Unsupported conversion"

    def get_available_conversions(self, currency: str) -> list[str]:
        try:
            return list(self._conversions[currency])
        except KeyError:
            return []

    def get_all_currencies(self):
        return list(self._conversions.keys())

    def _find_conversions(self, conversion_data):
        graph = dict()
        conversions = dict()

        for entry in conversion_data:
            from_node = entry['#1']
            to_node = entry['#2']
            value = entry['Value']

            if from_node not in graph:
                graph[from_node] = {to_node: value}
            else:
                graph[from_node][to_node] = value

            if to_node not in graph:
                graph[to_node] = {from_node: 1/value}
            else:
                graph[to_node][from_node] = 1/value

            if from_node not in conversions:
                conversions[from_node] = set()
            conversions[from_node].add(to_node)
            if to_node not in conversions:
                conversions[to_node] = set()
            conversions[to_node].add(from_node)

        self._conversion_values = graph
        self._conversions = conversions


if __name__ == '__main__':
    conv = [
        {
            "#1": "CZK",
            "#2": "USD",
            "Value": 0.044
        },
        {
            "#1": "EUR",
            "#2": "GBP",
            "Value": 0.86
        },
        {
            "#1": "JPY",
            "#2": "USD",
            "Value": 0.0092
        },
        {
            "#1": "USD",
            "#2": "EUR",
            "Value": 0.92
        }
    ]
    converter = Converter(conv)
    print(converter.get_available_conversions("CZK"))
    print(converter.convert("CZK", "USD", 50))


