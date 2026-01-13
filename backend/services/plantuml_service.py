"""
PlantUML Service

Handles PlantUML code validation and rendering to SVG/PNG.
Supports both online PlantUML server and local rendering.
"""

from __future__ import annotations

import base64
import zlib
from typing import Optional, Literal
import httpx


class PlantUMLService:
    """
    Service for validating and rendering PlantUML diagrams.
    Uses public PlantUML server for rendering.
    """

    def __init__(self):
        self.server_url = "http://www.plantuml.com/plantuml"
        self.timeout = 30.0

    def validate_syntax(self, plantuml_code: str) -> tuple[bool, Optional[str]]:
        """
        Validate PlantUML syntax.

        Args:
            plantuml_code: PlantUML code to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not plantuml_code or not plantuml_code.strip():
            return False, "PlantUML code cannot be empty"

        if not plantuml_code.strip().startswith("@startuml"):
            return False, "PlantUML code must start with @startuml"

        if not plantuml_code.strip().endswith("@enduml"):
            return False, "PlantUML code must end with @enduml"

        # Check for balanced braces
        open_braces = plantuml_code.count("{")
        close_braces = plantuml_code.count("}")
        if open_braces != close_braces:
            return False, f"Unbalanced braces: {open_braces} opening, {close_braces} closing"

        return True, None

    async def render_svg(self, plantuml_code: str) -> bytes:
        """
        Render PlantUML code to SVG.

        Args:
            plantuml_code: PlantUML code to render

        Returns:
            SVG content as bytes

        Raises:
            ValueError: If PlantUML code is invalid
            httpx.HTTPError: If rendering fails
        """
        is_valid, error = self.validate_syntax(plantuml_code)
        if not is_valid:
            raise ValueError(f"Invalid PlantUML syntax: {error}")

        encoded = self._encode_plantuml(plantuml_code)
        url = f"{self.server_url}/svg/{encoded}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.content

    async def render_png(self, plantuml_code: str) -> bytes:
        """
        Render PlantUML code to PNG.

        Args:
            plantuml_code: PlantUML code to render

        Returns:
            PNG content as bytes

        Raises:
            ValueError: If PlantUML code is invalid
            httpx.HTTPError: If rendering fails
        """
        is_valid, error = self.validate_syntax(plantuml_code)
        if not is_valid:
            raise ValueError(f"Invalid PlantUML syntax: {error}")

        encoded = self._encode_plantuml(plantuml_code)
        url = f"{self.server_url}/png/{encoded}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.content

    async def render(
        self,
        plantuml_code: str,
        format: Literal["svg", "png"] = "svg"
    ) -> bytes:
        """
        Render PlantUML code to specified format.

        Args:
            plantuml_code: PlantUML code to render
            format: Output format (svg or png)

        Returns:
            Rendered diagram as bytes
        """
        if format == "svg":
            return await self.render_svg(plantuml_code)
        elif format == "png":
            return await self.render_png(plantuml_code)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _encode_plantuml(self, plantuml_code: str) -> str:
        """
        Encode PlantUML code for URL.
        Uses PlantUML's text encoding algorithm.

        Args:
            plantuml_code: PlantUML code to encode

        Returns:
            Encoded string for URL
        """
        # Compress using zlib
        compressed = zlib.compress(plantuml_code.encode('utf-8'))[2:-4]

        # Encode to PlantUML's custom base64
        encoded = self._plantuml_encode(compressed)

        return encoded

    def _plantuml_encode(self, data: bytes) -> str:
        """
        Encode bytes using PlantUML's custom base64 alphabet.

        Args:
            data: Bytes to encode

        Returns:
            Encoded string
        """
        # PlantUML uses a custom base64 alphabet
        alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"

        result = []
        for i in range(0, len(data), 3):
            # Get 3 bytes (or less for the last group)
            chunk = data[i:i+3]

            # Pad if necessary
            while len(chunk) < 3:
                chunk += b'\x00'

            # Convert to integer
            b1, b2, b3 = chunk[0], chunk[1], chunk[2]

            # Encode using PlantUML alphabet
            result.append(alphabet[(b1 >> 2) & 0x3F])
            result.append(alphabet[((b1 & 0x3) << 4) | ((b2 >> 4) & 0xF)])
            result.append(alphabet[((b2 & 0xF) << 2) | ((b3 >> 6) & 0x3)])
            result.append(alphabet[b3 & 0x3F])

        # Remove padding characters if we padded
        length = len(data)
        if length % 3 == 1:
            result = result[:-2]
        elif length % 3 == 2:
            result = result[:-1]

        return ''.join(result)
