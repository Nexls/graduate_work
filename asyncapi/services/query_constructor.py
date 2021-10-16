from __future__ import annotations
import logging


LIMIT_PER_PAGE = 50


class QueryConstructor:
    """
    Класс для парсинга параметров вручную, потому что наличие скобочек []
    в параметрах не дает воспользоваться штатным средством.
    Использовать класс надо методом цепочки вызовов:
    QueryConstructor(body).add_sort().add_limits().add_single_field_search('full_name')
    """

    def __init__(self, body: dict) -> None:
        self.body = body
        self._payload = {}

    def add_sort(self) -> QueryConstructor:
        if 'sort' not in self.body:
            return self

        sort_order = 'asc'
        sort = self.body['sort']
        if sort[0] == '-':
            sort_order = 'desc'
            sort = sort[1:]

        self._payload['sort'] = [{sort: sort_order}]

        return self

    def add_limits(self) -> QueryConstructor:
        limit = LIMIT_PER_PAGE

        if 'page_size' in self.body:
            try:
                limit = int(self.body['page_size'])
                if limit <= 0:
                    limit = LIMIT_PER_PAGE
            except Exception:
                logging.error('Error converting "page_size" to int')
        # limit всегда заполняем, хотя бы дефолтным значением, чтобы не запрашивать лишнего
        self._payload['size'] = limit

        if 'page_number' in self.body:
            try:
                page = int(self.body['page_number'])
                if page > 0:
                    self._payload['from'] = (page-1) * limit
            except Exception:
                logging.error('Error converting "page[number]" to int')

        return self

    def add_filter(self, field: str, query_param_name: str) -> QueryConstructor:
        if query_param_name not in self.body:
            return self

        self._payload['query'] = {
            'bool': {
                'must': {
                    'term': {field: self.body[query_param_name]}
                }
            }
        }

        return self

    def add_multi_field_search(self, fields: list) -> QueryConstructor:
        if 'query' not in self.body:
            return self

        self._payload['query'] = {
            'multi_match': {
                'query': self.body['query'],
                'fuzziness': 'auto',
                'fields': fields,
            }
        }
        return self

    def add_single_field_search(self, field: str) -> QueryConstructor:
        if 'query' not in self.body:
            return self

        self._payload['query'] = {
            'bool': {
                'must': {
                    'match': {field: self.body['query']}
                }
            }
        }
        return self

    def get_payload(self) -> dict:
        return self._payload
