from http import HTTPStatus


def check_fields_in_response(fields, response_json, url):
    '''Проверяет корректность отображения полей для запросов'''
    for field in fields:
        assert field in response_json, (
            f'Убедитесь, что в ответ на запрос к `{url}'
            f' указано поле {field}'
        )
        assert response_json[field] == fields[field], (
            f'Убедитесь, что в ответ на запрос к '
            f'`{url}` для объекта верно отображается поле {field}'
        )


def check_only_safe_methods_allowed(user_client, url):
    '''Проверяет, что с помощью эндпоинта нет возможности изменить объект'''
    responses = [
        user_client.post(url),
        user_client.patch(url),
        user_client.put(url),
        user_client.delete(url),
    ]
    for response in responses:
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            'Убедитесь, что в ответ на небезопасные методы к '
            f'`{url}` возвращается статус 405'
        )
