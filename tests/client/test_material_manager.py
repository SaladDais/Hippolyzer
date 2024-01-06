import unittest
from typing import Any

import aioresponses

from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base import llsd
from hippolyzer.lib.client.object_manager import ClientObjectManager

from . import MockClientRegion


class MaterialManagerTest(unittest.IsolatedAsyncioTestCase):
    FAKE_CAPS = {
        "RenderMaterials": "http://127.0.0.1:8023"
    }

    GET_RENDERMATERIALS_BODY = [
        {'ID': UUID(int=1).bytes,
         'Material': {'AlphaMaskCutoff': 0, 'DiffuseAlphaMode': 1, 'EnvIntensity': 0,
                      'NormMap': UUID(int=4), 'NormOffsetX': 0, 'NormOffsetY': 0,
                      'NormRepeatX': 10000, 'NormRepeatY': 10000, 'NormRotation': 0, 'SpecColor': [255, 255, 255, 255],
                      'SpecExp': 51, 'SpecMap': UUID(int=5), 'SpecOffsetX': 0,
                      'SpecOffsetY': 0, 'SpecRepeatX': 10000, 'SpecRepeatY': 10000, 'SpecRotation': 0}},
        {'ID': UUID(int=2).bytes,
         'Material': {'AlphaMaskCutoff': 0, 'DiffuseAlphaMode': 0, 'EnvIntensity': 0,
                      'NormMap': UUID(int=6), 'NormOffsetX': 0, 'NormOffsetY': 0,
                      'NormRepeatX': 10000, 'NormRepeatY': -10000, 'NormRotation': 0,
                      'SpecColor': [255, 255, 255, 255], 'SpecExp': 51,
                      'SpecMap': UUID(int=7), 'SpecOffsetX': 0, 'SpecOffsetY': 0,
                      'SpecRepeatX': 10000, 'SpecRepeatY': -10000, 'SpecRotation': 0}},
        {'ID': UUID(int=3).bytes,
         'Material': {'AlphaMaskCutoff': 0, 'DiffuseAlphaMode': 1, 'EnvIntensity': 50,
                      'NormMap': UUID.ZERO, 'NormOffsetX': 0, 'NormOffsetY': 0,
                      'NormRepeatX': 10000, 'NormRepeatY': 10000, 'NormRotation': 0, 'SpecColor': [255, 255, 255, 255],
                      'SpecExp': 200, 'SpecMap': UUID(int=8), 'SpecOffsetX': 0,
                      'SpecOffsetY': 0, 'SpecRepeatX': 10000, 'SpecRepeatY': 10000, 'SpecRotation': 0}},
    ]

    def _make_rendermaterials_resp(self, resp: Any) -> bytes:
        return llsd.format_xml({"Zipped": llsd.zip_llsd(resp)})

    async def asyncSetUp(self):
        self.aio_mock = aioresponses.aioresponses()
        self.aio_mock.start()
        # Requesting all materials
        self.aio_mock.get(
            self.FAKE_CAPS['RenderMaterials'],
            body=self._make_rendermaterials_resp(self.GET_RENDERMATERIALS_BODY)
        )
        # Specific material request
        self.aio_mock.post(
            self.FAKE_CAPS['RenderMaterials'],
            body=self._make_rendermaterials_resp([self.GET_RENDERMATERIALS_BODY[0]])
        )
        self.region = MockClientRegion(self.FAKE_CAPS)
        self.manager = ClientObjectManager(self.region)

    async def asyncTearDown(self):
        self.aio_mock.stop()

    async def test_fetch_all_materials(self):
        await self.manager.request_all_materials()
        self.assertListEqual([UUID(int=1), UUID(int=2), UUID(int=3)], list(self.manager.state.materials.keys()))

    async def test_fetch_some_materials(self):
        mats = await self.manager.request_materials((UUID(int=1),))
        self.assertListEqual([UUID(int=1)], list(mats.keys()))
        self.assertListEqual([UUID(int=1)], list(self.manager.state.materials.keys()))
