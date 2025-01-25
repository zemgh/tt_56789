import os
import asyncio

import aiohttp

from fastapi import HTTPException, status

from src.schemas import WalletDataDict, ResourcesDict


TRON_API_URL = os.getenv('TRON_API_URL', 'testcase')
TRON_API_KEY = os.getenv('TRON_API_KEY', 'testcase')


class TronService:
    async def fetch_tron_wallet(self, wallet_address: str) -> WalletDataDict:
        payload = {
            'address': wallet_address,
            'visible': True
        }
        headers = {
            'TRON-PRO-API-KEY': TRON_API_KEY,
            'accept': 'application/json',
            'content-type': 'application/json'
        }

        async with aiohttp.ClientSession() as session:
            account, resources = await asyncio.gather(
                self._fetch_account(session, payload, headers),
                self._fetch_resources(session, payload, headers)
            )

        return WalletDataDict(
            address=account['address'],
            balance=account['balance'],
            resources=ResourcesDict(**resources)
        )

    async def _fetch_account(self, session, payload, headers) -> dict:
        account = await self._fetch('/getaccount', session, payload, headers)

        if 'Error' in account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Address does not exists'
            )

        return account

    async def _fetch_resources(self, session, payload, headers) -> dict:
        resources = await self._fetch('/getaccountresource', session, payload, headers)

        if resources == {}:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Address does not exists'
            )

        return resources

    async def _fetch(self, url, session, payload, headers) -> dict:
        async with session.post(
                TRON_API_URL + url,
                json=payload,
                headers=headers) as response:

            if response.status == 200:
                return await response.json()

            if response.status == 400:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Bad request'
                )

            else:
                # 403, 503 etc
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail='Service unavailable'
                )



