"""Cloud Inverter API client."""
import logging
import json
import asyncio
from typing import Any, Dict, Optional
import aiohttp
from datetime import datetime

_LOGGER = logging.getLogger(__name__)


class CloudInverterAPI:
    """API client for Cloud Inverter (SenergyTec)."""

    BASE_URL = "https://www.cloudinverter.net"
    LOGIN_ENDPOINT = "/dist/server/api/CodeIgniter/index.php/Senergytec/web/v2/Inverterapi/UserLogin_v1"
    MEMBER_DATA_ENDPOINT = "/dist/server/api/CodeIgniter/index.php/Senergytec/web/v2/Inverterapi/GetMemberData"
    GROUP_LIST_ENDPOINT = "/dist/server/api/CodeIgniter/index.php/Senergytec/web/v2/Inverterapi/GroupList"
    INVERTER_DETAIL_ENDPOINT = "/dist/server/api/CodeIgniter/index.php/Senergytec/web/v2/Inverterapi/InverterDetailInfoNewone"

    def __init__(self, username: str, password: str):
        """Initialize the API client."""
        self.username = username
        self.password = password
        self.token: Optional[str] = None
        self.member_auto_id: Optional[str] = None
        self.goods_id: Optional[str] = None
        self.session: Optional[aiohttp.ClientSession] = None

    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self):
        """Close the session."""
        if self.session:
            await self.session.close()
            self.session = None

    async def _make_request(
        self, endpoint: str, data: Dict[str, Any], authenticated: bool = True
    ) -> Dict[str, Any]:
        """Make HTTP request to Cloud Inverter API."""
        try:
            session = await self.get_session()
            url = f"{self.BASE_URL}{endpoint}"

            headers = {
                "Content-Type": "application/json",
            }

            if authenticated and self.token:
                headers["Authorization"] = self.token

            async with session.post(
                url, json=data, headers=headers, timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status == 200:
                    response_data = await resp.json()
                    return response_data
                else:
                    _LOGGER.error(f"API request failed with status {resp.status} for endpoint {endpoint}")
                    return {}

        except asyncio.TimeoutError:
            _LOGGER.error(f"API request timeout for endpoint {endpoint}")
            return {}
        except Exception as e:
            _LOGGER.error(f"API request error for {endpoint}: {e}")
            return {}

    async def login(self) -> bool:
        """Login to Cloud Inverter API and get token."""
        try:
            _LOGGER.debug("Attempting login to Cloud Inverter API")

            login_data = {
                "MemberID": self.username,
                "Password": self.password,
                "remember": True,
                "type": "1",
            }

            response = await self._make_request(
                self.LOGIN_ENDPOINT, login_data, authenticated=False
            )

            if response.get("status") == "ok":
                self.token = response.get("token")
                self.member_auto_id = response.get("MemberAutoID")
                _LOGGER.info(f"Successfully logged in. Member ID: {self.member_auto_id}")
                return True
            else:
                error_msg = response.get("error", "Unknown error")
                _LOGGER.error(f"Login failed: {error_msg}")
                return False

        except Exception as e:
            _LOGGER.error(f"Login exception: {e}")
            return False

    async def get_member_data(self) -> Dict[str, Any]:
        """Get member data including timezone and system info."""
        if not self.token:
            if not await self.login():
                return {}

        try:
            _LOGGER.debug("Fetching member data")

            data = {
                "MemberAutoID": self.member_auto_id,
                "language": "en-US",
            }

            response = await self._make_request(self.MEMBER_DATA_ENDPOINT, data)
            return response

        except Exception as e:
            _LOGGER.error(f"Get member data error: {e}")
            return {}

    async def get_inverters(self) -> list:
        """Get list of available inverters."""
        if not self.token:
            if not await self.login():
                return []

        try:
            _LOGGER.debug("Fetching inverter list")

            data = {
                "MemberAutoID": self.member_auto_id,
                "inputValue": "",
            }

            response = await self._make_request(self.GROUP_LIST_ENDPOINT, data)
            inverters = response.get("AllGroupList", [])

            if inverters:
                # Store the first inverter's ID
                self.goods_id = inverters[0].get("AutoID")
                _LOGGER.info(f"Found {len(inverters)} inverter(s). Primary: {self.goods_id}")

            return inverters

        except Exception as e:
            _LOGGER.error(f"Error fetching inverters: {e}")
            return []

    async def get_inverter_detail(self, goods_id: Optional[str] = None) -> Dict[str, Any]:
        """Get detailed inverter information."""
        if not self.token:
            if not await self.login():
                return {}

        try:
            if not goods_id:
                if not self.goods_id:
                    # Try to fetch inverters first
                    inverters = await self.get_inverters()
                    if not inverters:
                        _LOGGER.error("No inverters found and no goods_id provided")
                        return {}
                goods_id = self.goods_id

            _LOGGER.debug(f"Fetching inverter detail for {goods_id}")

            data = {
                "GoodsID": goods_id,
                "MemberAutoID": self.member_auto_id,
            }

            response = await self._make_request(self.INVERTER_DETAIL_ENDPOINT, data)
            inverter_data = response.get("data", {})

            if not inverter_data:
                _LOGGER.warning(f"No inverter data received for {goods_id}")

            return inverter_data

        except Exception as e:
            _LOGGER.error(f"Error fetching inverter detail: {e}")
            return {}

    async def get_all_data(self) -> Dict[str, Any]:
        """Get all inverter data in a single call."""
        if not self.token:
            _LOGGER.debug("Token not available, logging in")
            if not await self.login():
                return {"success": False, "timestamp": datetime.now().isoformat()}

        try:
            # Get inverter details
            inverter_data = await self.get_inverter_detail()

            if not inverter_data:
                _LOGGER.warning("No inverter data available")
                return {"success": False, "timestamp": datetime.now().isoformat()}

            return {
                "timestamp": datetime.now().isoformat(),
                "data": inverter_data,
                "success": True,
            }

        except Exception as e:
            _LOGGER.error(f"Error getting all data: {e}")
            return {"success": False, "timestamp": datetime.now().isoformat()}
