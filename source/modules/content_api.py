from datetime import datetime
import jwt
from httpx import AsyncClient
from config import JWT_SECRET


class ContentApi:
    access_token: str
    headers: dict

    def __init__(self, user_id: str):
        ts_now = datetime.now().timestamp()
        jwt_data = {'id': user_id,
                    'role': 'Admin',
                    'iat': ts_now,
                    'exp': ts_now + 10  # Токен будет жить 10 секунд, для разовых операций
                    }
        self.access_token = jwt.encode(payload=jwt_data, key=JWT_SECRET)
        self.headers = {'Authorization': f'Bearer {self.access_token}'}

    async def delete(self, file_url: str) -> None:
        """
        Метод для удаления файла из файловой системы контентого мс.
        :param file_url: ссылка на файл
        """

        async with AsyncClient(verify=True) as async_session:
            await async_session.delete(
                url=file_url,
                headers=self.headers
            )

