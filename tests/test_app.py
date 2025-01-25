import asyncio
import pytest

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, patch, Mock

import aiohttp

from fastapi import status

from src.repositories import QueryRepository


@pytest.mark.asyncio
async def test_create_query(db_session):
    test_address = 'a' * 34
    repo = QueryRepository(db_session)

    await repo.create(address=test_address)

    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_get_wallet_integration(client):
    ENDPOINT_URL = '/api/v1/tron/wallet'
    test_address = 'a' * 34
    test_wrong_address = False
    test_response_status = status.HTTP_200_OK

    account = {
                'address': test_address,
                'balance': 100,
    }
    resources = {
                'freeNetLimit': 1,
                'TotalNetLimit': 1,
                'TotalNetWeight': 1,
                'TotalEnergyLimit': 1,
                'TotalEnergyWeight': 1,
    }

    @asynccontextmanager
    async def mock_post_context(*args, **kwargs):
        nonlocal test_wrong_address, test_response_status

        mock_response = AsyncMock()
        target_url = args[0].split('/')[-1]

        if target_url == 'getaccount':
            mock_response.json.return_value = account if not test_wrong_address else {'Error': 'error'}
        elif target_url == 'getaccountresource':
            mock_response.json.return_value = resources if not test_wrong_address else {}

        mock_response.status = test_response_status

        yield mock_response

    with patch.object(aiohttp.ClientSession, 'post', new_callable=Mock) as mock_post:
        mock_post.side_effect = lambda *args, **kwargs: mock_post_context(*args, **kwargs)

        # correct wallet address
        response = await client.post(ENDPOINT_URL, json={'address': test_address})
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['address'] == account['address'] == test_address
        assert response.json()['balance'] == account['balance']
        assert response.json()['resources'] == resources
        assert mock_post.call_count == 2

        # wrong wallet address
        test_wrong_address = True
        response = await client.post(ENDPOINT_URL, json={'address': test_address})
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {'detail': 'Address does not exists'}

        # wrong tron api request
        test_response_status = status.HTTP_400_BAD_REQUEST
        response = await client.post(ENDPOINT_URL, json={'address': test_address})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # tron api unavailable
        test_response_status = status.HTTP_503_SERVICE_UNAVAILABLE
        response = await client.post(ENDPOINT_URL, json={'address': test_address})
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE

        # rate limiter
        test_wrong_address = False
        test_response_status = status.HTTP_200_OK
        responses = await asyncio.gather(
            *[client.post(ENDPOINT_URL, json={'address': test_address}) for _ in range(50)]
        )
        for response in responses:
            if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                assert True
                break
        else:
            assert False


