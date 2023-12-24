from __future__ import annotations

import gzip
import logging
from pathlib import Path
from typing import Union, List, Tuple, Set

from hippolyzer.lib.base import llsd
from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.inventory import InventoryModel, InventoryCategory, InventoryItem
from hippolyzer.lib.base.templates import AssetType, FolderType
from hippolyzer.lib.client.state import BaseClientSession


LOG = logging.getLogger(__name__)


class InventoryManager:
    def __init__(self, session: BaseClientSession):
        self._session = session
        self.model: InventoryModel = InventoryModel()
        self._load_skeleton()

    def _load_skeleton(self):
        assert not self.model.nodes
        skel_cats: List[dict] = self._session.login_data.get('inventory-skeleton', [])
        for skel_cat in skel_cats:
            self.model.add(InventoryCategory(
                name=skel_cat["name"],
                cat_id=UUID(skel_cat["folder_id"]),
                parent_id=UUID(skel_cat["parent_id"]),
                # Don't use the version from the skeleton, this flags the inventory as needing
                # completion from the inventory cache. This matches indra's behavior.
                version=InventoryCategory.VERSION_NONE,
                type=AssetType.CATEGORY,
                pref_type=FolderType(skel_cat.get("type_default", FolderType.NONE)),
                owner_id=self._session.agent_id,
            ))

    def load_cache(self, path: Union[str, Path]):
        # Per indra, rough flow for loading inv on login is:
        # 1. Look at inventory skeleton from login response
        # 2. Pre-populate model with categories from the skeleton, including their versions
        # 3. Read the inventory cache, tracking categories and items separately
        # 4. Walk the list of categories in our cache. If the cat exists in the skeleton and the versions
        #    match, then we may load the category and its descendants from cache.
        # 5. Any categories in the skeleton but not in the cache, or those with mismatched versions must be fetched.
        #    The viewer does this by setting the local version of the cats to -1 and forcing a descendent fetch
        #    over AIS.
        #
        # By the time you call this function call, you should have already loaded the inventory skeleton
        # into the model set its inventory category versions to VERSION_NONE.

        skel_cats: List[dict] = self._session.login_data['inventory-skeleton']
        # UUID -> version map for inventory skeleton
        skel_versions = {UUID(cat["folder_id"]): cat["version"] for cat in skel_cats}
        LOG.info(f"Parsing inv cache at {path}")
        cached_categories, cached_items = self._parse_cache(path)
        LOG.info(f"Done parsing inv cache at {path}")
        loaded_cat_ids: Set[UUID] = set()

        for cached_cat in cached_categories:
            existing_cat: InventoryCategory = self.model.get(cached_cat.cat_id)  # noqa
            # Don't clobber an existing cat unless it just has a placeholder version,
            # maybe from loading the skeleton?
            if existing_cat and existing_cat.version != InventoryCategory.VERSION_NONE:
                continue
            # Cached cat isn't the same as what the inv server says it should be, can't use it.
            if cached_cat.version != skel_versions.get(cached_cat.cat_id):
                continue
            if existing_cat:
                # Remove the category so that we can replace it, but leave any children in place
                self.model.unlink(existing_cat, single_only=True)
            self.model.add(cached_cat)
            # Any items in this category in our cache file are usable and should be added
            loaded_cat_ids.add(cached_cat.cat_id)

        for cached_item in cached_items:
            # The skeleton doesn't have any items, so if we run into any items they should be exactly the
            # same as what we're trying to add. No point clobbering.
            if cached_item.item_id in self.model:
                continue
            # The parent category didn't have a cache hit against the inventory skeleton, can't add!
            if cached_item.parent_id not in loaded_cat_ids:
                continue
            self.model.add(cached_item)

    def _parse_cache(self, path: Union[str, Path]) -> Tuple[List[InventoryCategory], List[InventoryItem]]:
        """Warning, may be incredibly slow due to llsd.parse_notation() behavior"""
        categories: List[InventoryCategory] = []
        items: List[InventoryItem] = []
        # Parse our cached items and categories out of the compressed inventory cache
        first_line = True
        with gzip.open(path, "rb") as f:
            # Line-delimited LLSD notation!
            for line in f.readlines():
                # TODO: Parsing of invcache is dominated by `parse_notation()`. It's stupidly inefficient.
                node_llsd = llsd.parse_notation(line)
                if first_line:
                    # First line is the file header
                    first_line = False
                    if node_llsd['inv_cache_version'] not in (2, 3):
                        raise ValueError(f"Unknown cache version: {node_llsd!r}")
                    continue

                if InventoryCategory.ID_ATTR in node_llsd:
                    if (cat_node := InventoryCategory.from_llsd(node_llsd)) is not None:
                        categories.append(cat_node)
                elif InventoryItem.ID_ATTR in node_llsd:
                    if (item_node := InventoryItem.from_llsd(node_llsd)) is not None:
                        items.append(item_node)
                else:
                    LOG.warning(f"Unknown node type in inv cache: {node_llsd!r}")
        return categories, items
