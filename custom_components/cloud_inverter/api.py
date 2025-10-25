"""API Client for Cloud Inverter."""
import logging
import aiohttp
import asyncio
from typing import Any

from .const import (
    ENDPOINT_LOGIN,
    ENDPOINT_MEMBER_DATA,
    ENDPOINT_ALL_MEMBERS,
    ENDPOINT_GROUP_LIST,
    ENDPOINT_INVERTER_DETAIL,
)

_LOGGER = logging.getLogger(__name__)

# Default initial authorization token for login
DEFAULT_AUTH_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJ3d3cuY2xvdWRpbnZlcnRlci5uZXQiLCJhdWQiOiJ3d3cuY2xvdWRpbnZlcnRlci5uZXQiLCJpYXQiOjE3NjA2Mjg2NTYsIm5iZiI6MTc2MDYyODY1NiwiZXhwIjoxNzkxNzMyNjU2LCJkYXRhIjp7Ik1lbWJlckF1dG9JRCI6bnVsbH19.YacN4_8qHUgWrlvkQqGvVdbHlTJwqsJ4_e7FMeUpfw0"

# Default sign value (you may need to update this if it changes)
DEFAULT_SIGN = "3kNFdvKEsLcyS6GsYUV/PeMKGj1Lkq05PA81+SG5Dljmx6KBvhhV7DhC8qrIPUX60AqLZQ0t8QbqUhVB9VW5oT+5iNwnvvkzDyqtAq03BKCRctLpzBbfaWlMYhgxCM/m"


class CloudInverterAPI:
    """Class to communicate with Cloud Inverter API."""

    def __init__(self, username: str, password: str, session: aiohttp.ClientSession = None):
        """Initialize the API client."""
        self.username = username
        self.password = password
        self.session = session
        self.token = None
        self.member_auto_id = None
        self.goods_id = None
        self._close_session = False

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get aiohttp session."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
            self._close_session = True
        return self.session

    async def close(self):
        """Close the session."""
        if self._close_session and self.session:
            await self.session.close()

    async def login(self) -> bool:
        """Login to Cloud Inverter API."""
        try:
            session = await self._get_session()
            
            # Prepare login payload
            payload = {
                "MemberID": self.username,
                "Password": self.password,
                "remember": True,
                "sign": DEFAULT_SIGN,
                "type": "1"
            }
            
            headers = {
                "Content-Type": "application/json",
                "authorization": DEFAULT_AUTH_TOKEN
            }
            
            async with asyncio.timeout(30):
                async with session.post(ENDPOINT_LOGIN, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("status") == "ok":
                            self.token = data.get("token")
                            self.member_auto_id = data.get("MemberAutoID")
                            _LOGGER.info("Successfully logged in to Cloud Inverter. Member ID: %s", self.member_auto_id)
                            return True
                        else:
                            _LOGGER.error("Login failed: Invalid credentials or status")
                            return False
                    else:
                        _LOGGER.error("Login failed with status %s: %s", response.status, await response.text())
                        return False
                    
        except asyncio.TimeoutError:
            _LOGGER.error("Login timeout - could not connect to Cloud Inverter API")
            return False
        except Exception as err:
            _LOGGER.error("Error during login: %s", err)
            return False

    async def get_member_data(self) -> dict[str, Any]:
        """Get member data."""
        if not self.token or not self.member_auto_id:
            if not await self.login():
                return {}
            
        try:
            session = await self._get_session()
            
            payload = {
                "MemberAutoID": self.member_auto_id,
                "language": "en-US",
                "sign": "eOQKIdmAVNdcrWOxOmktv3gP3dQRvRMn46atrTD1J5qi0f8u3Uh6bIfepeHSMfFR2Jkp6gyAN7nlartB83m1EAdHqus6LUID8Pu3z4463is="
            }
            
            headers = {
                "Content-Type": "application/json",
                "authorization": self.token,
                "cookie": "timezone=Asia%2FKarachi"
            }
            
            async with asyncio.timeout(30):
                async with session.post(ENDPOINT_MEMBER_DATA, json=payload, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    return {}
                    
        except Exception as err:
            _LOGGER.error("Error getting member data: %s", err)
            return {}

    async def get_group_list(self) -> list[dict[str, Any]]:
        """Get list of inverter groups."""
        if not self.token or not self.member_auto_id:
            if not await self.login():
                return []
            
        try:
            session = await self._get_session()
            
            payload = {
                "MemberAutoID": self.member_auto_id,
                "inputValue": "",
                "sign": "eOQKIdmAVNdcrWOxOmktv5d2jIygN0ID/LcvUbmuSnboEVMSWqplaZ2btt8g/ywYDX3dt9LyGPyI8DxJPjYUsA=="
            }
            
            headers = {
                "Content-Type": "application/json",
                "authorization": self.token,
                "cookie": "timezone=Asia%2FKarachi"
            }
            
            async with asyncio.timeout(30):
                async with session.post(ENDPOINT_GROUP_LIST, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        _LOGGER.debug("Group list response: %s", data)
                        groups = data.get("AllGroupList", [])
                        if groups and len(groups) > 0:
                            # Store the AutoID from the first group
                            first_group = groups[0]
                            # The AutoID is what we need for getting inverter details
                            self.goods_id = str(first_group.get("AutoID"))
                            _LOGGER.info("Found inverter group. AutoID: %s, Type: %s", 
                                       self.goods_id, first_group.get("GoodsTypeName"))
                        else:
                            _LOGGER.warning("No inverter groups found in response")
                        return groups
                    else:
                        _LOGGER.error("Failed to get group list (status %s): %s", response.status, await response.text())
                        return []
                    
        except Exception as err:
            _LOGGER.error("Error getting group list: %s", err, exc_info=True)
            return []

    async def get_inverter_data(self, goods_id: str = None) -> dict[str, Any]:
        """Get detailed inverter data."""
        if not self.token or not self.member_auto_id:
            if not await self.login():
                return {}
            
        # Get goods_id if not provided
        if goods_id is None:
            if self.goods_id is None:
                # Get the goods_id from group list first
                groups = await self.get_group_list()
                if not groups:
                    _LOGGER.error("No inverter groups found")
                    return {}
            goods_id = self.goods_id
            
        if goods_id is None:
            _LOGGER.error("No goods_id available")
            return {}
            
        try:
            session = await self._get_session()
            
            # According to your API call, we need to use the actual serial number
            # But we'll try with the AutoID first, and if that fails, 
            # we'll need to get the actual GoodsID from somewhere else
            
            # First attempt: Try getting all members to find the actual GoodsID
            all_members_payload = {
                "MemberAutoID": self.member_auto_id,
                "sign": "eOQKIdmAVNdcrWOxOmktv5d2jIygN0ID/LcvUbmuSnboEVMSWqplaZ2btt8g/ywYDX3dt9LyGPyI8DxJPjYUsA=="
            }
            
            headers = {
                "Content-Type": "application/json",
                "authorization": self.token,
                "cookie": "timezone=Asia%2FKarachi"
            }
            
            # Try to get the actual device serial from getAllAllMember
            try:
                async with asyncio.timeout(30):
                    async with session.post(ENDPOINT_ALL_MEMBERS, json=all_members_payload, headers=headers) as response:
                        if response.status == 200:
                            members_data = await response.json()
                            _LOGGER.debug("All members data: %s", members_data)
            except Exception as e:
                _LOGGER.debug("Could not get all members data: %s", e)
            
            # Now try to get the inverter detail using the AutoID from group
            # Based on your example, the GoodsID should come from somewhere
            # Let's try to construct the request with what we have
            payload = {
                "GoodsID": goods_id,  # Using AutoID for now
                "MemberAutoID": self.member_auto_id,
                "sign": "bA/YbB72GDQL6DmqFtfIYLfV68qsRoH+B7Q2ZhFbiwWqDwO37OAcUqk/RAHWIcG75YQIVk7uvfISm3P0f/V0i6mgF+Dr5/P4eaq6skBL8HQ="
            }
            
            _LOGGER.debug("Requesting inverter data with GoodsID: %s", goods_id)
            
            async with asyncio.timeout(30):
                async with session.post(ENDPOINT_INVERTER_DETAIL, json=payload, headers=headers) as response:
                    response_text = await response.text()
                    _LOGGER.debug("Inverter detail response (status %s): %s", response.status, response_text)
                    
                    if response.status == 200:
                        try:
                            data = await response.json() if response_text else {}
                            if data:
                                _LOGGER.info("Successfully retrieved inverter data")
                                return data
                            else:
                                _LOGGER.warning("Received empty inverter data")
                                return {}
                        except Exception as e:
                            _LOGGER.error("Failed to parse inverter data JSON: %s", e)
                            return {}
                    else:
                        _LOGGER.error("Failed to get inverter data (status %s): %s", response.status, response_text)
                        return {}
                    
        except Exception as err:
            _LOGGER.error("Error getting inverter data: %s", err, exc_info=True)
            return {}

    async def test_connection(self) -> bool:
        """Test if we can authenticate with the API."""
        try:
            # Try to login
            if not await self.login():
                _LOGGER.error("Test connection failed: Login unsuccessful")
                return False
            
            # Try to get group list to ensure full connection
            groups = await self.get_group_list()
            if not groups:
                _LOGGER.error("Test connection failed: No inverter groups found")
                return False
            
            _LOGGER.info("Connection test successful! Found %d inverter group(s)", len(groups))
            return True
            
        except Exception as err:
            _LOGGER.error("Connection test failed with exception: %s", err)
            return False
